#!/usr/bin/env python3
# --- DNK-MRH-HEADER ---
# mrh_id: "scripts/system/new_brick.py"
# purpose: "Scaffold a new sovereign brick according to the 5-element Sovereign Unit Contract."
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-11-15"
# author: "Antigravity & Gerych"
# --- END DNK-MRH-HEADER ---

import sys
from pathlib import Path

def scaffold_brick(name: str):
    base = Path("services") / name
    if base.exists():
        print(f"⚠️ Папка {base} вже існує!")
        return

    (base / "src").mkdir(parents=True, exist_ok=True)
    (base / "contracts").mkdir(parents=True, exist_ok=True)
    (base / "tests").mkdir(parents=True, exist_ok=True)

    # 1. brick.manifest.yaml
    manifest = f"""# --- DNK-MRH-HEADER ---
# mrh_id: "services/{name}/brick.manifest.yaml"
# purpose: "Sovereign Brick Manifest for {name}"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# --- END DNK-MRH-HEADER ---
id: "{name}"
version: "1.0.0"
domain: "services"
paths:
  - "services/{name}/**"
entrypoints:
  in_ram_facade: "services.{name}.src.service"
  standalone_cli: "services.{name}.cli"
  mcp_server: "services.{name}.mcp_server"
contracts:
  schemas: "services.{name}.contracts.schemas"
quality_gate:
  test_command: "uv run pytest services/{name}/tests"
"""
    (base / "brick.manifest.yaml").write_text(manifest)

    # 2. contracts/schemas.py
    schemas = f"""# --- DNK-MRH-HEADER ---
# mrh_id: "services/{name}/contracts/schemas.py"
# purpose: "Strict Pydantic v2 schemas for {name}"
# canonical_source: true
# status: "Active"
# version: "1.0.0"
# --- END DNK-MRH-HEADER ---
from pydantic import BaseModel, ConfigDict

class ServiceInput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    query: str

class ServiceOutput(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    success: bool
    result: str
"""
    (base / "contracts" / "schemas.py").write_text(schemas)

    # 3. src/service.py
    service = f"""# Pure business logic (0 LLM dependency)
def process_data(query: str) -> str:
    return f"Processed: {{query}}"
"""
    (base / "src" / "service.py").write_text(service)

    # 4. cli.py
    cli = f"""import sys
from services.{name}.src.service import process_data

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "default"
    print(process_data(query))
"""
    (base / "cli.py").write_text(cli)

    # 5. mcp_server.py
    mcp_server = f"""from mcp.server.fastmcp import FastMCP
from services.{name}.src.service import process_data

mcp = FastMCP("{name}")

@mcp.tool()
def execute(query: str) -> str:
    return process_data(query)

if __name__ == "__main__":
    mcp.run()
"""
    (base / "mcp_server.py").write_text(mcp_server)

    # 6. tests/test_brick.py
    tests = f"""from services.{name}.src.service import process_data

def test_process_data():
    assert process_data("hello") == "Processed: hello"
"""
    (base / "tests" / "test_brick.py").write_text(tests)

    print(f"✅ Суверенна цеглинка services/{name} успішно створена з 5 стандартними файлами!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Використання: python3 scripts/system/new_brick.py <назва_цеглинки>")
        sys.exit(1)
    scaffold_brick(sys.argv[1])
