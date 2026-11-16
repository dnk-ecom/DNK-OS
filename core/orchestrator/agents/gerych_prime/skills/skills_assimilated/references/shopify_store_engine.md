# Level-of-Detail (LOD) Reference: SHOPIFY_STORE_ENGINE
# Synthesized per ADR-089 & ADR-007 (Zero Standing Context Bloat)
## 🎯 Core Champion: `flyrank-bih/harness-engineering-playbook`
- **Determinism Score**: 0.7
- **State Space Score**: 0.7
- **Token Diet Score**: 0.65
- **Autonomy Score**: 0.75
- **Self-Healing Score**: 0.8
- **Composite Score**: **0.815/1.0**

## 🧬 Absorbed Donor Capabilities
- **`NikoCartin/shopify-dynamic-pdp-playbook`**: Strict static typing and validation, Permissive license enables direct autonomous compilation
- **`Saabbir/shopify-theme-handbook`**: Strict static typing and validation, Permissive license enables direct autonomous compilation
- **`movictor99/shopify-theme-builder`**: Permissive license enables direct autonomous compilation
- **`shopify/cli`**: Permissive license enables direct autonomous compilation
- **`topics/shopify`**: Complementary pattern: shopify
- **`metabase/agent-skills`**: Permissive license enables direct autonomous compilation
- **`orgs/shopify`**: Complementary pattern: shopify
- **`0ddlab/shopify-hermes-skill`**: Permissive license enables direct autonomous compilation
- **`11ty/eleventy`**: Permissive license enables direct autonomous compilation
- **`40rty-ai/shopify-admin-skills`**: Permissive license enables direct autonomous compilation
- **`6161shaurya/malware-deobfuscator`**: Permissive license enables direct autonomous compilation

## 🛠️ Canonical Usage via Swarm Coordinator
```python
from core.orchestrator.cross_repo_synthesizer import CrossRepoSynthesizer

# JIT Execution by worker 'dnk_shopify'
result = dnk_swarm_dispatch(
    agent="dnk_shopify",
    task_description="Execute shopify_store_engine synthesized pipeline slice"
)
```
