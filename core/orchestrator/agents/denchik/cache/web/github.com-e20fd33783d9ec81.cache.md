# Releases Â· NousResearch/hermes-agent
URL: https://github.com/NousResearch/hermes-agent/releases

Releases Â· NousResearch/hermes-agent

teknium1 released this 

 03 Nov 21:53 

 Immutable release. Only release title and notes can be modified. 

 v0.22.7 

# Hermes Agent v0.22.7

Release Date: November 3, 2026

> Patch release. This tag rolls up the ~174 PRs merged since v0.22.6 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker and Hermes Cloud. Full curated notes for this window ship with v0.23.0.

## About this release

Measured at commit `b200f5bc60e`, the window since v0.22.6 contains 581 non-merge commits across 554 changed files (+24,012 / â3,144), 174 merged PRs and 29 closed issues.

Also in the window, undocumented here on purpose: opt-in lead routing for Desktop Group Chats (with a Lead badge on the room header), cron jobs that post into Group Chats, room purpose and shared notes, group rooms laid out in one chat column with each member's live state, pinned Kanban boards as quick-switch tabs, `$$TeX$$` diagram labels and mermaid diagrams rendered through Pele, a Desktop update error box that shows the failed update's output with a report link, Web Access naming the step Start is on with a running clock, Telegram on Team Gateway set up by linking an account to the shared bot, an opt-in Slack `thread_followup_silence` for unaddressed thread replies, a Daybreak switch for catalog-listed ChatGPT subscription models, and a batch of new plugin-catalog entries.

Full curated release notes for this window ship with v0.23.0, which will document everything from v0.22.0 onward â highlights, feature areas, and complete contributor credits. Nothing in this window is skipped.

## Updating

- Microsoft Store app: updates through the Store.
- Desktop app installed from the installer (.exe / .dmg): no change in this release; it updates with the next bundled release.
- CLI: `hermes update`, or re-run the installer one-liner.
- Docker / Hermes Cloud: `nousresearch/hermes-agent:stable` (or `:latest`).

Full Changelog: v0.22.6...v0.22.7

 Assets 3 

 Loading 

### Uh oh! 

 

There was an error while loading. Please reload this page.

teknium1 released this 

 02 Nov 17:18 

 Immutable release. Only release title and notes can be modified. 

 v0.22.6 

# Hermes Agent v0.22.6

Release Date: November 2, 2026

> Patch release. This tag rolls up the ~776 PRs merged since v0.22.5 into a stable release for the GitHub release (CLI and installers), the Microsoft Store app, Docker and Hermes Cloud. Full curated notes for this window ship with v0.23.0.

## About this release

Measured at commit `f0d94882e89`, the window since v0.22.5 contains 3,448 non-merge commits across 4,316 changed files (+248,579 / â94,077), 776 merged PRs and 385 closed issues.

Also in the window, undocumented here on purpose: the Webapp served from the gateway's own listener (`hermes webapp`, a Desktop Web Access pane to open it on your network or your own URL behind Nous sign-in, and Desktop plugins loading in a browser tab), `/model reset