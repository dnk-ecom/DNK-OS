# (no title)
URL: https://raw.githubusercontent.com/pullboard-dev/pullboard/main/SPEC.md

# Pullboard local

The local-first core of Pullboard: a work board, lanes, a spec and git hooks that live in the repo. No account, no network. This file is the spec, in the format `pullboard spec check` lints.

Statuses: approved = decided Â· draft = proposed Â· pending = open question Â· fact = true today Â· wont = won't build, decided and kept Â· retired = no longer applies, kept. Ids are permanent: never delete or renumber a row. Tiers: must Â· aim.

## P Â· Principles
- P1 [approved, must] Nothing ships until a second agent verifies it. | gate: test/board.test.js
- P2 [approved, must] Works offline in any git repo, with no account or network unless you turn on sync. | gate: test/e2e.test.js
- P3 [approved, must] Zero runtime dependencies. Node 22.13 or newer. | gate: test/package.test.js
- P4 [approved, must] Every refusal names its rule, shows what it saw, and gives the next step. | gate: review
- P5 [approved, must] The core names no model or vendor, and opens no connection except the sync you turn on. | gate: test/boundary.test.js
- P6 [approved, must] A person's own moves (approving rows, answering decisions, signing off) come only from the person: their own terminal, the view in their own browser (local or on pullboard.dev), or a signed person move; never through an agent interface such as MCP, the API, or a CLI run in an agent's shell. | gate: test/mcp.test.js

## B Â· Board
- B1 [approved, must] One SQLite file in the git common dir. Every worktree sees it; nothing is committed. | gate: test/e2e.test.js
- B2 [approved, must] Every move is one immediate transaction. Two agents never hold one item. | gate: test/e2e.test.js | serves: P1
- B3 [approved, must] An agent is its worktree. The main checkout is the coordinator. | gate: test/e2e.test.js
- B4 [approved, must] A claim is a lease, 2h by default. Claiming again renews it. | gate: test/board.test.js
- B5 [approved, must] One live claim per agent, besides reworks of its own rejects and child items. | gate: test/board.test.js
- B6 [approved, must] Items cite spec ids that exist. | gate: test/e2e.test.js | serves: S1
- B7 [approved, must] Shouts reach a lane, an agent or all. Inbox marks them read. | gate: test/board.test.js
- B8 [approved, must] An item can wait on others; claiming it is refused until they are verified. | gate: test/board.test.js
- B9 [approved, must] Submit pins the commit under refs/pullboard/items, so submitted work is never lost. | gate: test/e2e.test.js
- B10 [approved, must] An item carries a brief: how to build it. Next and show print it; edit changes it until verified. | gate: test/board.test.js, test/e2e.test.js
- B11 [retired] Items route strong or light; B13 replaced the two routes with three tiers.
- B12 [approved, must] Every item is built in its own lane; the coordinator claims only coordinator-lane items. | gate: test/board.test.js | serves: L3
- B13 [approved, must] Routes are tiers: light, mid, strong. An agent claims and verifies its tier and below, its own fi