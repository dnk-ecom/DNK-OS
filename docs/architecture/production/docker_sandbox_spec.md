---
title: "DNK OS Docker Sandbox Technical Specification v1.0"
description: "Technical Specification for Ephemeral Docker Sandbox Isolation, Security Profiles & Execution Lifecycle in DNK OS"
mrh_id: "docs/architecture/production/docker_sandbox_spec.md"
status: Active
archetype: GENERAL_DOC
version: "2.0.0"
updated: 2026-11-18
tags:
  - architecture
  - dnk-os
---

> [!metadata]- ⚙️ Системні метадані та інваріанти (MRH Header)
> ```yaml
> # --- DNK-MRH-HEADER ---
> mrh_id: "docs/architecture/production/docker_sandbox_spec.md"
> purpose: "Technical Specification for Ephemeral Docker Sandbox Isolation, Security Profiles & Execution Lifecycle in DNK OS"
> canonical_source: true
> alters_files: []
> triggers_tasks: []
> status: "Active"
> version: "2.0.0"
> updated_at: "2026-11-18"
> author: "DNK-e.com Maksym & Antigravity"
> # --- END DNK-MRH-HEADER ---
> ```

# 🐳 DNK OS Docker Sandbox Technical Specification v1.0

> **System:** DNK OS MVP — Production Hardening  
> **Sub-Phase:** Phase 3.1 (Docker Sandbox Isolation)  
> **Target Runtime:** Docker Engine 26+ / Containerd / gVisor (runsc)  
> **Document Status:** Canonical Technical Specification  

---

## 1. Architectural Overview & Threat Model

The DNK OS Docker Sandbox is an ephemeral, fail-closed isolation boundary designed to execute arbitrary, untrusted third-party plugins, user-authored Python/Node.js scripts, and autonomous agent tasks without risking the host system, shared memory, or backend services.

```
+-----------------------------------------------------------------------------------+
| Host Worker Node (Linux Kernel 6.x / Ubuntu 24.04 LTS / cgroups v2)              |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | DNK OS Orchestrator Worker (dnk_sandbox_manager)                            |  |
|  | - Unix Socket / Docker API Client                                           |  |
|  | - Ephemeral Volume Allocator                                                |  |
|  | - Lifecycle Supervisor & Hard Timeout Enforcer                              |  |
|  +-----------------------+-----------------------------------------------------+  |
|                          | gRPC / Unix Socket                                     |
|                          v                                                        |
|  +-----------------------------------------------------------------------------+  |
|  | Ephemeral Sandbox Container (gVisor `runsc` / Non-Root UID 10001)           |  |
|  |                                                                             |  |
|  |  +-------------------------+  +------------------------------------------+  |  |
|  |  | Root Filesystem (ro)    |  | Memory Limits: Max 512MB (OOM-kill)      |  |  |
|  |  | /bin, /usr, /lib        |  | CPU Limits: 1.0 vCPU (quota 100000/100000)|  |  |
|  |  +-------------------------+  +------------------------------------------+  |  |
|  |  | Ephemeral Tmpfs (rw)    |  | Network: Isolated Namespace (`none`)     |  |  |
|  |  | /tmp (128MB, noexec)    |  | No External Internet Access by default   |  |  |
|  |  +-------------------------+  +------------------------------------------+  |  |
|  |  | App Workdir (ro/rw-tmp) |  | Security: Seccomp-BPF + AppArmor Strict  |  |  |
|  |  | /workspace/input.json   |  | Capabilities: Drop ALL, no SETUID        |  |  |
|  |  +-------------------------+  +------------------------------------------+  |  |
|  |                                                                             |  |
|  |  Execution Engine: Python 3.12-slim / Node.js 20-alpine (Cosign Verified)   |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

### Threat Mitigation Matrix

| Threat Vector | Potential Impact | Sandbox Defense Mechanism |
|---|---|---|
| **Host Filesystem Tampering** | Arbitrary file overwrite, credential theft | Rootfs mounted `read-only`; `/tmp` mounted on isolated `tmpfs` with `noexec,nosuid,nodev`. |
| **Container Escape / Kernel Exploits** | Host takeover, node compromise | Multi-layer containment: gVisor user-space kernel (`runsc`), Seccomp-BPF filter, AppArmor strict profile, `drop ALL` Linux capabilities. |
| **Resource Exhaustion (DoS)** | CPU starvation, host out-of-memory | Cgroups v2: Hard quota on CPU (`1.0 vCPU`), memory hard ceiling (`512MB` max), PIDs limit (`64` max). |
| **Lateral Network Scanning / Exfiltration** | Attacking internal databases, AWS metadata | `NetworkMode: "none"` default; no host loopback access; strict egress proxy with whitelist if approval granted. |
| **Privilege Escalation** | Root execution inside container | Container runs under static unprivileged UID/GID `10001:10001` (`dnkrunner`); `no-new-privileges:true`. |
| **Zombie / Infinite Loop Processes** | Worker thread exhaustion | Asynchronous watchdog with 5–30s hard timeout SIGTERM → 2s grace → SIGKILL. |

---

## 2. Container Isolation Architecture

### 2.1 Compute & Memory Isolation (cgroups v2)
Every plugin invocation spawns a dedicated container instance with strict runtime limits enforced via Linux `cgroups v2`:

```json
{
  "HostConfig": {
    "Memory": 536870912,
    "MemorySwap": 536870912,
    "MemoryReservation": 268435456,
    "NanoCpus": 1000000000,
    "CpuPeriod": 100000,
    "CpuQuota": 100000,
    "PidsLimit": 64,
    "OomKillDisable": false,
    "StorageOpt": {
      "size": "512M"
    }
  }
}
```

- **Memory**: Hard ceiling of 512 MB. Swap is disabled (`MemorySwap == Memory`) to prevent host SSD thrashing.
- **CPU Quota**: 100,000 µs per 100,000 µs period (maximum 1.0 vCPU core equivalent).
- **Process ID (PID) Limit**: Max 64 processes/threads per container to prevent fork bombs.
- **OOM Killer**: Enabled. If memory exceeds 512 MB, the container is killed immediately and returns `SANDBOX_OOM_KILLED`.

### 2.2 Filesystem & Volume Isolation
- **Read-Only Root**: The entire root filesystem (`/`) is mounted immutable (`ReadonlyRootfs: true`).
- **Tmpfs Mounts**:
  - `/tmp`: `tmpfs` with max size `128MB`, mounted with `rw,noexec,nosuid,nodev`.
  - `/run`: `tmpfs` with max size `16MB`, mounted with `rw,noexec,nosuid,nodev`.
- **Payload Exchange**:
  - Input payload injected via read-only bind mount or stdin pipe: `/workspace/input.json` (`ro`).
  - Output captured via stdout/stderr stream or write-only scratch volume `/workspace/output/` (`rw`, 64MB cap).

### 2.3 Network Sandboxing
- Default network mode: `--network none` (`NetworkMode: "none"`).
- Containers possess no network interfaces other than a disconnected local loopback.
- Access to `169.254.169.254` (cloud metadata), internal VPC endpoints, and the host bridge is physically absent.
- **Approval-Gated Network Mode**:
  - If a plugin manifest explicitly declares `network_access: true` AND is granted an approved token via the Human-in-the-Loop (HITL) gate, the container is connected to an isolated bridge network `dnk-sandbox-egress`.
  - The bridge routes strictly through an egress filtering proxy (Envoy / Squid) that enforces domain whitelisting, SNI checking, and rate limiting (max 10 req/min).

---

## 3. Security Hardening & Isolation Profiles

### 3.1 Non-Root User Execution
Containers must never execute as UID 0. The Dockerfile and execution configuration mandate:
- User: `dnkrunner` (UID `10001`, GID `10001`).
- `SecurityOpt`: `["no-new-privileges:true"]`. Prevents processes from acquiring additional privileges via `setuid` or `setgid` binaries.

### 3.2 Linux Capabilities
All standard Linux capabilities are dropped. No supplementary capabilities are retained:
```json
{
  "CapDrop": ["ALL"],
  "CapAdd": []
}
```

### 3.3 Seccomp-BPF Profile
A custom, restrictive Seccomp profile blocks dangerous system calls:
- **Blocked Syscalls**: `ptrace`, `sys_chroot`, `sys_boot`, `reboot`, `kexec_load`, `mount`, `umount2`, `pivot_root`, `setns`, `unshare`, `clone` (with flags creating new user namespaces), `bpf`, `perf_event_open`.
- **Allowed Syscalls**: Basic computation, memory management (`read`, `write`, `openat`, `close`, `fstat`, `mmap`, `mprotect`, `munmap`, `brk`, `rt_sigaction`, `rt_sigprocmask`, `ioctl` on tty, `nanosleep`, `exit_group`).

### 3.4 AppArmor Profile (`dnk-sandbox-strict`)
```apparmor
#include <tunables/global>

profile dnk-sandbox-strict flags=(attach_disconnected,mediate_deleted) {
  #include <abstractions/base>

  # Deny network access by default
  deny network,

  # Deny raw access to hardware, devices, kernel
  deny /dev/** rwklx,
  deny /proc/sys/** rwklx,
  deny /sys/** rwklx,

  # Allow read access to runtime libraries
  /usr/local/lib/** r,
  /usr/lib/** r,
  /lib/** r,

  # Allow execution of plugin entrypoint
  /usr/local/bin/python3 rix,
  /usr/local/bin/node rix,

  # Allow temporary file writes
  owner /tmp/** rw,
  owner /workspace/output/** rw,

  # Deny reading sensitive host or container configuration
  deny /etc/shadow* rwklx,
  deny /etc/passwd* wklx,
}
```

---

## 4. Execution Lifecycle & Supervisor

The execution of a plugin within the sandbox follows a strict state machine:

```
[INIT] ──> [ALLOCATE] ──> [START] ──> [RUNNING] ──┬──> [COMPLETED] ──> [CLEANUP]
                                                  │
                                                  ├──> [TIMEOUT]   ──> [FORCE_KILL] ──> [CLEANUP]
                                                  │
                                                  └──> [OOM/FAULT] ──> [RECORD_ERR] ──> [CLEANUP]
```

### Lifecycle Specifications

| State | Action / Validation | Max Time Budget |
|---|---|---|
| **1. ALLOCATE** | Generate ephemeral container ID, write `/workspace/input.json`, mount tmpfs. | < 150 ms |
| **2. START** | Invoke container run via Docker Engine API with Seccomp & AppArmor flags. | < 350 ms |
| **3. RUNNING** | Stream stdout/stderr buffers; supervisor watchdog monitors process tree. | 5 – 30 s (configurable) |
| **4. TERMINATION** | Normal exit (code 0) or non-zero exit code captured. | < 50 ms |
| **5. TIMEOUT KILL** | If running > configured limit: send `SIGTERM` → 2s wait → send `SIGKILL`. | Max 2000 ms |
| **6. CLEANUP** | Remove container (`docker rm -f`), unmount and purge scratch tmpfs directory. | < 100 ms |

### Supervisor Watchdog Invariant
- Every execution is governed by an asynchronous `asyncio.wait_for` timeout.
- The default execution window is **10 seconds**; maximum allowed extension via manifest is **30 seconds**.
- Upon timeout expiration, the supervisor triggers an immediate forced termination, logs the event to the audit trail, and marks the task as `TIMED_OUT`.

---

## 5. Base Image Management & Supply Chain Security

### 5.1 Base Images
To maintain minimal attack surfaces, sandbox environments use distroless or minimal Alpine/Slim bases:
- **Python Runtime**: `dnk-sandbox-python:3.12-slim` (stripped of compilers, pip cache, and debugging utilities).
- **Node.js Runtime**: `dnk-sandbox-node:20-alpine` (hardened user, minimal package manager cache).

### 5.2 Build Once, Deploy Many (BODM)
- Base images are built via reproducible GitHub Actions CI pipelines with pinned digests (`sha256:...`).
- Dependencies are frozen with cryptographically verified lockfiles (`poetry.lock` / `pnpm-lock.yaml`).
- No compilation or external package installation is permitted at runtime inside the sandbox container.

### 5.3 Cryptographic Image Signing & Verification
- **Cosign (Sigstore)**: All container images built for DNK OS are signed via Cosign using private KMS keys.
- **Admission Verification**: The Docker Sandbox Manager verifies the signature and digest of the base image against the trusted public key before launching any container:
  ```bash
  cosign verify --key /etc/dnk/cosign.pub dnk-registry.internal/dnk-sandbox-python:3.12-slim
  ```
- If signature verification fails or digest mismatch occurs, the worker halts immediately and flags a security incident.
