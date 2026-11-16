# Stormycry-cryp/seecut
- Page: GitHub repository
- URL: https://github.com/Stormycry-cryp/seecut
- License: AGPL-3.0 license
- Default branch: codex/concat-baseline
- Created: 2026-09-19T06:15:29.000Z
- Commits: 3

## Top-level files
- .github/
- assets/
- docs/screenshots/
- models/
- scripts/
- src/
- test/
- .gitattributes
- .gitignore
- CLA.md
- CODE_OF_CONDUCT.md
- CONTRIBUTING.md
- LICENSE
- LICENSE-EXCEPTIONS.md
- README.en.md
- README.md
- ROADMAP.MD
- SECURITY.md
- THIRD_PARTY_NOTICES.md
- TODO.MD
- TRADEMARK.md
- TRANSLATING.md
- flake.lock
- flake.nix

## README.md
[SeeCut Logo](https://github.com/Stormycry-cryp/seecut/blob/codex/concat-baseline/docs/screenshots/seecut-logo.png)

# SeeCut
## 一站式音视频创作应用
说出你的目标，让 Agent 操作 SeeCut，完成从素材到成片的创作。
[Rust](https://github.com/Stormycry-cryp/seecut/tree/codex/seecut-unified-mac-candidate/src) [Slint](https://slint.dev/) [License](https://github.com/Stormycry-cryp/seecut/blob/codex/concat-baseline/LICENSE)

...

SeeCut 把图像、音频和视频创作放进同一个桌面应用，核心目标是让 Agent 贯穿全部功能：用户说明想做什么，Agent 理解当前页面和已有素材，自主安排步骤，直接操作 SeeCut，完成后交付作品和处理结果。
这个目标覆盖生成素材、修改图片、配音、字幕、剪辑和导出，让 Agent 在不同工作区之间持续推进同一项任务。用户可以随时查看进展、补充要求，或直接在界面里接着编辑。

...

## 当前进展
SeeCut 正在开发中，目前主要在 **macOS Apple Silicon** 上构建和验证。其他平台的 SeeCut 版本仍需实机验收，当前仓库尚未提供公开下载包。
Agent 已接入部分工作区读取、编辑和任务工具；全部业务接口的工具覆盖，以及跨全部功能的长程任务验收，仍在推进中。上面的自主创作流程描述产品目标。
最新 SeeCut 源码位于 [`codex/seecut-unified-mac-candidate`](https://github.com/Stormycry-cryp/seecut/tree/codex/seecut-unified-mac-candidate) 。仓库默认分支目前保留 Concat 初始基线，体验和构建 SeeCut 请使用开发分支。
功能验证与已知限制见开发分支的 [实现核对记录](https://github.com/Stormycry-cryp/seecut/blob/codex/seecut-unified-mac-candidate/docs/SEECUT-FIGMA-IMPLEMENTATION-QA.md) 。

## 从源码开始
macOS 原生应用需要 Rust 1.93、Xcode Command Line Tools、CMake、C++ 工具链和 FFmpeg 7+ 开发库。
```shell
git clone --branch codex/seecut-unified-mac-candidate --single-branch https://github.com/Stormycry-cryp/seecut.git
cd seecut/src
cargo run --profile quick -p concat
```

...

## 致谢与许可
本仓库代码沿用 [AGPL-3.0-or-later](https://github.com/Stormycry-cryp/seecut/blob/codex/concat-baseline/LICENSE) 。附加授权见 [LICENSE-EXCEPTIONS.md](https://github.com/Stormycry-cryp/seecut/blob/codex/concat-baseline/LICENSE-EXCEPTIONS.md) ，第三方声明见 [THIRD_PARTY_NOTICES.md](https://github.com/Stormycry-cryp/seecut/blob/codex/concat-baseline/THIRD_PARTY_NOTICES.md) ；Compositor 和 Toonflow 的相关部分保留各自 MIT 许可。