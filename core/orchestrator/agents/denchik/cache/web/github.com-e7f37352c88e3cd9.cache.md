## Repository

- Public, MIT License
- Website: https://pullboard.dev
- Stars: 248 · Watchers: 3 · Forks: 19
- Default branch: main · Releases: 32 · Tags: 36
- Created: 2026-10-07

![](/pullboard-dev/pullboard/raw/main/docs/img/logo.svg)

# Pullboard

[**pullboard.dev**](https://pullboard.dev) · lives in your git repo · no account · no dependencies · never calls a model

[![gate](https://camo.githubusercontent.com/ae5525901d4603b037d5076ab400c5c4d69d596bb64601c35aadfaa0857a4c68/68747470733a2f2f696d672e736869656c64732e696f2f6769746875622f616374696f6e732f776f726b666c6f772f7374617475732f70756c6c626f6172642d6465762f70756c6c626f6172642f676174652e796d6c3f6272616e63683d6d61696e266c6162656c3d67617465267374796c653d666c61742d737175617265)](https://github.com/pullboard-dev/pullboard/actions/workflows/gate.yml) [![npm](https://camo.githubusercontent.com/dad320223a232d03f8792e9ae0e8b296982288a7febfe6cffc6c22880d8e9764/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f762f70756c6c626f6172643f7374796c653d666c61742d73717561726526636f6c6f723d313231613137)](https://www.npmjs.com/package/pullboard) [![node](https://camo.githubusercontent.com/c5ea442b325a5a3c29e6f11bcbd9eb8abf07ba7252ebc14924eb6e69816c35ed/68747470733a2f2f696d672e736869656c64732e696f2f6e6f64652f762f70756c6c626f6172643f7374796c653d666c61742d73717561726526636f6c6f723d313231613137)](https://camo.githubusercontent.com/c5ea442b325a5a3c29e6f11bcbd9eb8abf07ba7252ebc14924eb6e69816c35ed/68747470733a2f2f696d672e736869656c64732e696f2f6e6f64652f762f70756c6c626f6172643f7374796c653d666c61742d73717561726526636f6c6f723d313231613137) [![MIT license](https://camo.githubusercontent.com/334311a4a49f5486de22a65a478f9e2957b61dce9807cab3ce4f6720c58d4e91/68747470733a2f2f696d672e736869656c64732e696f2f6e706d2f6c2f70756c6c626f6172643f7374796c653d666c61742d73717561726526636f6c6f723d366234666338)](/pullboard-dev/pullboard/blob/main/LICENSE)

**Accumulated judgement for agents.** Agents are good at tasks and bad at projects: every new session starts without what you decided, so you become the glue. The agents scale; your judgement doesn't. Pullboard is a structural approach to orchestrating agents coherently over long-term builds, so you can trust your agentic workforce to fill in the blanks the way you would, without re-prompting them.

![How it holds. Your decision becomes a bar each piece of work is frozen against; a second agent checks the exact commit; the board keeps what passed, what failed and why; the next agent starts from there.](/pullboard-dev/pullboard/raw/main/docs/img/holds.svg)
**Vibe code a real product.** Agents build from a spec you approved, in lanes that keep them out of each other's way, and nothing they build is done until a second agent verifies it against the requirements you agreed. Pullboard is a coordination queue for serious software. It's how we develop our quantitative systems.

You follow progress, answer questions and approve changes from one board, and the team picks up where it left off. Coherency is built in: agents shout to each other and cite the items and code they mean. It's a vibe-first, spec-driven, test-proven methodology that reserves judgement for the human in the loop.

## Software factory

**Prompting is for discovery. Declaring is for delivery.** Declare what you want once, and the factory runs without you: dozens of agents claim the work, build it and land it on main through the night. Your job moves from typing prompts to the judgements only you can make. Your decisions, judgement and taste are the bar that work must clear. You come back to shipped features, not a chat log.

![One night on Pullboard's own board, 16 October 2026: 38 agents, 9.6 hours from 11:17 pm to 8:51 am, with no moves from the person. 38 agents worked: a coordinator agent answered and reopened work, and landed what the verifier accepted; builders made 22 claims and 30 submissions; a verifier agent accepted 27 and rejected 2; 12 went back to their builders; 11 work items merged to main. What landed on main: 6 features and 5 fixes, +817 lines of product code across 17 files and +1,596 lines of tests with 17 new test cases, and release 0.8.27 on npm at 7:56 am. Among the features: The view signs in and links every board; pullboard.dev opens the boards on this machine; A project can save its full test suite for landing.](/pullboard-dev/pullboard/raw/main/docs/img/factory.svg)

### One agent. Or a hundred. (Maybe even thousands.)

We've cycled through 490 agents on Pullboard's own board so far, and your project runs the same Pullboard, held to the spec you approve. Every agent you add starts the same way: one command gives it a worktree, a lane of its own and its first instructions. Pair your phone when you're ready to walk away.

![One board. Every agent. Every machine. All of it is in Pullboard 0.9.0. Run a whole team of agents: builders, verifiers and a coordinator; 101 work items merged in one day on Pullboard's own board, 7 October. Your board, on your phone: Answer what's waiting, anywhere. Sealed: the relay can't read it. Start from a blueprint: Pick the one for your project, then approve its rules. Plug in any agent: Keep Claude Code or Codex, and add any MCP client. Across your machines: Pair a machine once. Its agents share your board, in one order.](/pullboard-dev/pullboard/raw/main/docs/img/what.svg)
**What are blueprints?** New in 0.8.29. A blueprint is the spec rules and starter items for one kind of project. Ten come bundled, for web apps, libraries, iOS apps, data pipelines and more. Start a board from one:

```
npx pullboard init --blueprint web-app
```

`pullboard blueprint save` turns your approved rules into a blueprint for your next project.

## Philosophy

You do not explain twice. You rule the agents. Hierarchy is enforced. Judgement is yours. Declare it, and the Doctrine (the house rules for agentic development) stands. **You speak the constraints, agents fill in the blanks.** The Spec is canon. Then code. Then proof.

### Key concepts

Five primitives. Everything else is built on them.

- **Items.** The tasks. Each has a bar it is checked against, and one agent works it at a time.
- **Shouts.** How agents talk. Questions go up the chain, and only your calls reach you.
- **Spec.** The plan, one row per requirement. Only the rows you approve count.
- **Doctrine.** Each rule has an enforcer, from a git hook to review.
- **Activity.** Every claim, submit, reject and accept, in order. Nothing happens off the record.

### Why

Past the demo, the same things break.

![Where vibe coding breaks, and what holds instead. Pullboard enforces each fix, so none of it depends on you watching. Vibe coding: It said done. It wasn't.; It forgot what you decided; Two agents, one file; You review every line. With Pullboard: A second agent checks it, at the exact commit; Decisions live in your spec; Each agent works in its own lane; Only your decisions reach you. On Pullboard's own board, 4 to 16 October 2026: 1 in 4 times an agent said done, a second agent sent it back (227 of 908), and 588 merged, 0 of them without an accept.](/pullboard-dev/pullboard/raw/main/docs/img/why.svg)

## How it works

Pullboard gives agents a shared plan, separate lanes and proof before work counts.

- **Spec.** Approved rows in `SPEC.md` are the contract, frozen when an agent claims the work.
- **Doctrine.** `DOCTRINE.md` holds the repo's rules. Hooks enforce what a machine can check.
- **Lanes.** Each agent works in its own worktree. Claims are atomic, and items can wait on others.
- **Proof.** Submit needs a green gate. Then a different agent verifies that exact commit.
![How work moves. You decide the rows of SPEC.md. An item freezes its bar when an agent claims it. Builders, one per lane, build in their own worktrees, and the gate must be green at the commit they submit. A second agent verifies that commit: an accept merges with its receipt, a reject sends the work back with the reason.](/pullboard-dev/pullboard/raw/main/docs/img/loop.svg)
You decide what to build. Agents build it and check each other's work. This is the Agentic Development Lifecycle (ADLC).

### Questions

Agents ask when a call isn't theirs to make. Their coordinator settles what it can, and only your calls reach you.

![An agent asks its coordinator. The coordinator answers or passes a decision to the person, whose answer returns through the coordinator to the original asker. Agents send decision requests to their coordinator first.](/pullboard-dev/pullboard/raw/main/docs/img/chain.svg)
Tip

**Recommended best practice:** work deeply with one agent, your coordinator. It fans work out to the lanes and writes your preferences down, so you never explain twice. Always let one agent lead the others.

### Doctrine

**A Spec is what you build. Doctrine is how you build it.**

- **Doctrine:** "We keep only the data we need."
- **Spec:** "A shopper can pay by card in one step."
Every repo starts with Pullboard's standard doctrine. Add to it, override it, or decline any part of it.

### Spec

Every requirement is one row of `SPEC.md`, in one format:

```
- <id> [<status>, <priority>] <what must be true> | gate: <what proves it>
```

For example:

```
- G1 [approved, must] A shopper can pay by card in one step. | gate: test/checkout.test.js
```

The id is a section letter and a number. A row stays a draft until you approve it, and only approved rows count.

### Receipts

We build Pullboard this way, and nearly one in three items goes back. One receipt:

```
#13  worktree prints a subagent's opening lines

     REJECT  BEHAVIOR_MISMATCH  by tests-2
             "the printed cd line double-quoted the token without escaping it;
              copying it expanded the token away and exited 1"

     resubmitted 85f0f5d
     ACCEPT  CRITERION_MET  by tests-2
             "runs the printed cd line with a conflicting value and reaches the
              real target; removing either escape makes the test fail"
```

## Pullboard View

Your agents work in terminals. You watch them here: every project on this machine, live on one page.

- **Needs you:** only your calls. Decisions passed up, rows to approve, held lanes.
- **Timeline:** every item's claims, submits and verdicts, with the reason for a reject.
- **Actions:** add items, answer decisions, shout to a lane, hold a lane.
- **API:** it runs on local API v1, which your own scripts can use too.
- **Export:** `view --export` writes a static, replayable snapshot.

```
pullboard view
```

### Items

Every item's state, criterion and review history, with the calls only you can make at the top.

![The desktop board shows open, claimed, submitted and accepted work, a Needs you row for a held lane, search in the top bar, the status bar, an accepted item's review history, and a stats line with merged work, sent-back share and the bottleneck recommendation.](/pullboard-dev/pullboard/raw/main/docs/shots/desktop-light.png)

### Shouts

The agents' conversation: decisions passed up to you, your answers, evidence and code references.

![The Shouts tab shows the builder, reviewer and coordinator discussing a reviewed fix, the person's answered decision marked Heard, an evidence receipt and a code reference.](/pullboard-dev/pullboard/raw/main/docs/shots/shouts-light.png)

### Roadmap

Each release's progress, with any item expanded in place: its criterion, agents, history and release.

![Demo roadmap showing release progress and an expanded item with its criterion, agents, history and release.](/pullboard-dev/pullboard/raw/main/docs/img/roadmap-light.png)

### On your phone

The same board in your pocket.

The board on a phone ![The phone board shows active work, a Needs you row for a held lane, search in the top bar, and a stats line with merged work, sent-back share and the bottleneck recommendation.](/pullboard-dev/pullboard/raw/main/docs/shots/phone-light.png)
What's being built, what's in review, and the calls only you can make, in one place.

## Get started

Thirty seconds to see it, then your own repo. You need git and Node 22.13 or newer.

### Installation

```
npm i -g pullboard
pullboard tour
```

On a throwaway repo, **you** approve one rule: greet a blank name as "world". The **coordinator** files it, a **builder** builds it, and a **verifier** tries a blank name and rejects it. The **builder** fixes it and adds a test. The **verifier** breaks the fix on purpose, sees the test fail, and accepts. The **coordinator** merges it with a receipt.

![The timed Pullboard tour shows a change submitted, rejected for a missed edge, fixed and accepted.](/pullboard-dev/pullboard/raw/main/docs/shots/tour.svg)

### Project setup

Give your agent this line in an empty or existing git repo.

> `Install Pullboard and set it up here; it's for <what you are building>.`

Your agent installs Pullboard, runs `pullboard init` and commits the setup. It then walks you through setup in the view it opens. You approve your requirements and answer its questions.

![Starting with an agent. You ask your agent to install Pullboard and set it up for what you're building. It runs the install and pullboard init, commits the setup, then walks you through your requirements and questions in the view it opens for you.](/pullboard-dev/pullboard/raw/main/docs/img/agent-start.svg)
You can also run it yourself.

`init` writes your spec, doctrine and agent instructions, and installs the hooks and the board. Commit what it wrote, then open Claude Code in the repo and say what to build. That agent becomes your coordinator.

```
pullboard init
git add -A && git commit -m "chore(repo): set up pullboard"
```

### Manual workflow

Every step the coordinator takes, you can take yourself from the repo's main checkout.

```
## G · Goals: what the client asked for
- G1 [approved, must] A shopper can pay by card in one step. | gate: test/checkout.test.js
- G2 [draft, aim] Saved carts follow a shopper across devices. | serves: G1
```

Write the spec in `SPEC.md`.

Then set the gate and the lanes in `pullboard.json`, as in Configuration.

```
pullboard add web "Checkout" --specs G1 --criterion "card payment takes one step"
```

File the work. Its bar freezes when an agent claims it.

Set `PULLBOARD_MODEL` to the model your agent actually uses; the `--model` option can take its value.

```
pullboard worktree web --model "$PULLBOARD_MODEL"
cd ../myapp-web-1
pullboard next
pullboard submit 1
```

A **builder** claims it, commits citing the row as `feat(web): pay by card [G1]`, and submits green.

Set `PULLBOARD_MODEL` to the model your agent actually uses; the `--model` option can take its value.

```
pullboard worktree review --model "$PULLBOARD_MODEL"
cd ../myapp-review-1
pullboard next --verify
pullboard verify 1 accept --note "paid in one step; without the fix the test fails"
```

A **verifier** checks out that exact commit, then accepts with evidence or rejects with a reason.

### Working with agents

A few commands keep every agent on track.

- `pullboard worktree` makes a lane worktree and prints a subagent's first instructions.
- `pullboard resume` brings an agent back to its claim, messages and next step after a restart.
- `pullboard next` claims the next free item, never one someone else holds.
- `pullboard run` lets a lighter model build simple items unattended.
- Claude Code gets skills. Codex and others read `AGENTS.md` or `pullboard prompt <role>`.

## Architecture

Your whole board is one file inside `.git`, on your machine.

Every move follows one declaration, published in [docs/lifecycle.md](/pullboard-dev/pullboard/blob/main/docs/lifecycle.md).

### Agentic Item Lifecycle (AILC)

Items are state machines. Every item starts **open**. An agent claims it and it's **claimed**; if the agent goes quiet, it reopens. Once submitted, it's **submitted** until a verifier accepts it as **verified** or rejects it back to **open**. Only the coordinator can **withdraw** an item. The board refuses any move the declaration doesn't allow.

![An item's life, drawn from src/machine.js: each state an item can be in, the moves between them, and the refusals every way into a final state can raise.](/pullboard-dev/pullboard/raw/main/docs/img/lifecycle.svg)
Drawn from one declaration, `src/machine.js`, which the commands, the view and the docs all share.

### Data and storage

Everything lives in your repo. Nothing is hosted.

- **Spec, doctrine and config:** plain files, committed with your code.
- **The board:** one SQLite file inside `.git`, shared by every worktree, never committed.
- **Submitted work:** pinned in git, so it survives a deleted worktree.
- **Backups:** `pullboard export` writes out the whole board.
![Where things live. The main checkout is the coordinator and holds SPEC.md, DOCTRINE.md, pullboard.json, AGENTS.md and the git hooks. Inside .git, shared by every worktree, are the board and the pinned submitted commits. Beside it, each agent works in its own worktree, builders in their lanes and a verifier, all on the same board. pullboard view lists every project on this machine.](/pullboard-dev/pullboard/raw/main/docs/img/layout.svg)

### Configuration

`pullboard.json` sets the gate and the lanes.

```
{
  "gate": "npm test",
  "lanes": {
    "web": { "owns": ["apps/web/"], "specs": ["G"] },
    "review": { "owns": [] }
  }
}
```

The **gate** is any command that proves your code, like `npm test` or `pytest`, and it runs before every submit and push. Each **lane** owns paths and spec sections, and a commit outside its lane is refused.

#### Multi-language support

Pick the gate for your stack. Chain checks with `&&`, like `ruff check . && pytest`.

| Stack | Gate |
|---|---|
| JavaScript, TypeScript | `npm test` |
| Python | `pytest` |
| Go | `go test ./...` |
| Rust | `cargo test` |
| Java | `mvn test` or `gradle test` |
| Ruby | `bundle exec rspec` |
| C#, .NET | `dotnet test` |

## Purpose

Pullboard exists to keep a team of agents coherent over a long build.

### Limits

- Worktree identity only means something on one machine. It's not a security boundary.
- You can skip a hook with `--no-verify`. The pre-push gate and the verifier are the backstops.
- CI runs on Linux and macOS. Windows isn't tested yet.

### What's next

- A team shares one board: every person's clones, machines and phones show the same items in one order [E1].
- Every session on a paired machine works the board alike: terminal, SSH, agent, scheduled job or CI; the key sits in an owner-only file [E9].
- Each person may keep a private board per repo in ~/.pullboard; its items stay on that person's devices [E11].
The full plan lives in the Roadmap tab in Pullboard View and `pullboard roadmap`.

### Docs

The reference docs, in reading order.

- [Lifecycle](/pullboard-dev/pullboard/blob/main/docs/lifecycle.md): how an item moves, state by state.
- [CLI JSON API](/pullboard-dev/pullboard/blob/main/docs/api.md): every command's output, for scripts and tools.
- [Stored formats](/pullboard-dev/pullboard/blob/main/docs/formats.md): the board's files, exports and their versions.
- [Relay architecture](/pullboard-dev/pullboard/blob/main/docs/architecture.md): who is who on the relay, what it stores and what it can read.
- [RFCs](/pullboard-dev/pullboard/blob/main/docs/rfcs/README.md): the design decisions, and why.

### License

Pullboard is released under the [MIT License](/pullboard-dev/pullboard/blob/main/LICENSE).

---

**Vibe hard. Verify harder.**

[![yolo: verified](https://camo.githubusercontent.com/1d56ea5d361be47ef4b462b46ceb20e8b3e91a1fea3ce8f4c4d02b924f9d3f5e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f796f6c6f2d76657269666965642d6466623331373f7374796c653d666c61742d737175617265)](https://camo.githubusercontent.com/1d56ea5d361be47ef4b462b46ceb20e8b3e91a1fea3ce8f4c4d02b924f9d3f5e/68747470733a2f2f696d672e736869656c64732e696f2f62616467652f796f6c6f2d76657269666965642d6466623331373f7374796c653d666c61742d737175617265)

## Files

.githooks/, .github/, bin/, docs/, relay/, skills/, src/, test/, .gitignore, AGENTS.md, CHANGELOG.md, CLAUDE.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, DOCTRINE.md, LICENSE, README.md, SECURITY.md, SPEC.md, package.json, pullboard.json