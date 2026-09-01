# Project Instructions

## Project

- 本项目是使用 AI 制作的 PyCon 2026 幻灯片；人类负责选题、事实判断、逐页审稿和最终发布。
- 项目目标、托管入口、依赖和完整编译过程见 `README.md`。
- 项目是静态 GitHub Pages 内容。生成后的 `index.html`、`talk_files/`、二维码和音频必须保留在目录中。

## Paths

- `pycon2026-slide.md`：幻灯片可见内容与 TTS 演讲词的唯一内容源。
- `chapters-01-03.md`、`chapters-04-06.md`、`chapters-07-09.md`：公开演讲资料。
- `llms.txt`：现场听众 Agent 的公开索引。
- `talk.css`、`header.html`、`favicon.svg`：页面样式、行为和图标源文件。
- `scripts/`：二维码、QMD 和 TTS 生成器。
- `audio/*.mp3`、`assets/llms-qr.svg`、`index.html`、`talk_files/`：需要提交的托管成品。
- `audio/tts-state.json`：需要提交的 TTS 构建缓存，用于避免重复生成未变化的 MP3。
- `talk.qmd`、`audio/tts-manifest.json`、`scripts/__pycache__/`：构建中间文件，不应提交。

## Editing

- 页面内容和演讲词只改 `pycon2026-slide.md`；不要直接修改生成的 `index.html`。
- 视觉样式改 `talk.css`，页面播放行为改 `header.html`。
- 保持 `llms.txt`、章节资料与页面内容一致，但不得把内部母稿加入公开索引。
- 不要删除托管成品，除非同一次任务会重新生成它们。
- 不要自行 commit 或 push，除非用户明确要求。

## Build

- 编译过程、依赖和参数见 `README.md`；标准入口是 `make`。
- 构建结束后确认中间文件已清理，TTS state、最终 HTML、Reveal.js 依赖、二维码和全部音频仍然存在。
- 使用浏览器检查时，结束后必须关闭 Playwright session、停止临时 HTTP 服务，并删除 `.playwright-cli/` 快照目录。
