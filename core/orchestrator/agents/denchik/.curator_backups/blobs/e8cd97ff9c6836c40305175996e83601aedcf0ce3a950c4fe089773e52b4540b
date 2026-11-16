# XYFlow Agent Workflow & Reactive Artifact Visualization Pipeline

## 🎯 Purpose & Scope
This reference defines how `@xyflow/react` (v12) operates as the primary visual working desk and interactive mission control for Gerych Prime and specialized DNK OS Swarm Workers.

Instead of lengthy conversational text walls, user goals are dynamically materialized into executable graph topologies connecting context, agents, and live multi-modal deliverables.

---

## 🏗️ 4-Stage Inception-to-Artifact Architecture

```
User Prompt (Goal / Inception)
               │
               ▼
[ 1. SCONES / Context Intake Nodes ]
 ├── BrandDNA / ToneOfVoice Node
 ├── Product Knowledge Base Node
 └── Marketing Playbook / Style Node
               │
               ▼ (SwarmPropagationEngine reactive edges)
[ 2. Swarm Agent & Execution Nodes ]
 ├── SwarmAgentNode (Real-time reasoning, telemetry, HUD)
 ├── TaskNode / ApprovalNode (Gatekeeper)
               │
               ▼ (DataFlowEdge / MilestoneEdge)
[ 3. Multi-Modal Creative Production Nodes ]
 ├── PhotoStudioNode (1:1, 9:16, 16:9 banner synthesis)
 ├── ShopifyBuilderNode / LiveWebPreviewNode (Liquid AST / React sections)
 └── VideoCreatorNode (Remotion composition & reels)
               │
               ▼
[ 4. Deliverable Artifact Nodes & Obsidian Sync ]
 ├── ArtifactNode (Deliverable preview, download, CDN URIs)
 └── JSON Canvas v1.0 (.canvas) bidirectional persistence
```

---

## 🧩 Core Invariants & Implementation Nodes

1. **Reactive Propagation (`SwarmPropagationEngine`)**:
   - Location: `apps/web/src/canvas/swarm/swarmPropagation.ts`
   - Flow: Updates to BrandDNA (colors, `toneOfVoice`, `aiParams`) or upstream strategy payloads automatically cascade downstream across outgoing edges to `DesignGalleryNode`, `ApiDocsCodeNode`, and `SprintKanbanNode`.

2. **Specialized Artifact & Studio Nodes (`apps/web/components/canvas/nodes/`)**:
   - `SwarmAgentNode`: Real-time streaming thoughts, TaskDNA progress, execution logs, and interactive chat.
   - `PhotoStudioNode`: Multi-aspect image synthesis (1:1, 9:16, 16:9), prompt variant generator, and direct export.
   - `VideoCreatorNode`: Remotion-driven storyboard compiler and video renderer for vertical short-form (9:16) and widescreen (16:9).
   - `ShopifyBuilderNode`: Section preview, AST mutation engine, and deployment trigger.
   - `ApprovalNode`: High-risk execution gate requiring human click authorization before executing payments or external deploys.

3. **Bi-Directional JSON Canvas Synchronization**:
   - Location: `apps/web/src/canvas/json-canvas/converter.ts`
   - Translates XYFlow `@xyflow/react` nodes and edges into standard JSON Canvas v1.0 (`.canvas`) files compatible with Obsidian.
