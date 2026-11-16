# (no title)
URL: https://raw.githubusercontent.com/pullboard-dev/pullboard/main/DOCTRINE.md

# Practice

How pullboard itself is built: the house rules, as rows. SPEC.md says what to build; this file says how. A row whose gate names a check fails the build when broken; a row gated by review guides agents and reviewers.

Statuses: approved = in force Â· draft = proposed Â· wont = considered and declined, id kept Â· retired = dropped, id kept. Ids are permanent: never delete or renumber a row. Tiers: must Â· aim.

## W Â· Writing
- W1 [approved, must] Numbers over adjectives. No hedges, no filler. | gate: review
- W2 [approved, must] Headers: type(scope): subject [ids], 72 characters, no emojis. A body only for a non-obvious why, three sentences at most. | gate: commit-msg hook, review
- W3 [approved, must] Spec ids go in commits, code headers and test names, never in words meant for people. | gate: review
- W4 [approved, must] A refusal names its rule as a code and says the next step. | gate: review
- W5 [draft, must] Tracked files and commit bodies never quote the owner or report what they said, chose or wanted, and never name private infrastructure: machine names, hostnames, LAN addresses or home paths. A commit is a subject line, then at most `Pullboard-Item: #N`. | gate: review

## C Â· Code
- C1 [approved, must] Plain JavaScript ES modules; no build step. | gate: package test
- C2 [approved, must] Zero runtime dependencies: every import is a node: built-in or a file in this repo. | gate: test/package.test.js
- C3 [approved, must] Every function has a JSDoc block: what it does, then why when that is not obvious. | gate: review
- C4 [approved, must] Refusals throw Refused(code, message); nothing else exits the process except the bin. | gate: review
- C5 [approved, must] Text from files or users is escaped before it reaches a page. | gate: test/view.test.js
- C6 [draft, aim] Functions under 60 lines and files under 1,000. | gate: review
- C9 [approved, must] Source and test files stay under 1500 lines; existing excess can only fall. Why: bounded files keep changes and reviews manageable. | gate: check node bin/checks/file-size.js | count: 38
- C8 [approved, must] No bare empty catch hides a failure; existing cases can only fall. Why: failures need handling or an explicit reason to ignore them. | gate: check node bin/checks/empty-catch.js | count: 11
- C10 [draft, must] No silent catch or fallback: each one logs a specific line that names its subject. Rigor names each catch clause and .catch handler a change adds to a source file that neither throws nor writes a line; a fallback written with a default operator is review. | gate: check node bin/pullboard.js rigor quality --rule silent-catch | count: 0 | source: rigor-quality:silent-catch
- C11 [draft, must] A file over the 1500-line cap, or a change that grows code past its 400-line budget, is named. Rigor names each changed source file that ends over 1500 lines and grew, and a change whose non-test code grows by more than 400 lines net, or the board's rigor.budget setting, at the file that gre