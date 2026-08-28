# Code Agent Context

这是 PyCon 2026 演讲“Code Agent 的 Context——从 API、Agent Loop 到缓存与协作”的源文件、公开资料和静态托管成品。本项目使用 AI 制作，由人类确定内容、审查事实并负责最终发布；AI 参与研究、整理、幻灯片设计、讲解词生成和构建链路维护。

项目有三个目标：

1. 以 Reveal.js 幻灯片解释模型 API、Agent Loop、Context Management、Compaction、Cache、Memory、Skill 和 Subagent。
2. 为每页幻灯片提供普通话 TTS，使成品能够自动播放讲解。
3. 通过 `llms.txt` 和章节资料，为现场听众的 Agent 提供可引用的信息入口。

托管入口：

- Slides：<https://shell909090.github.io/slides/code_agent_ctx/>
- Agent 资料：<https://shell909090.github.io/slides/code_agent_ctx/llms.txt>

## 文件分布

### 内容源文件

- `pycon2026-slide.md`：幻灯片的唯一内容源，包含每页主旨、QMD 展示内容和 TTS 演讲词。
- `talk.css`：幻灯片视觉样式。
- `header.html`：Reveal.js 页面行为，包括音频自动播放逻辑。
- `favicon.svg`：站点图标。
- `scripts/`：生成 QMD、TTS、音频清单和二维码的脚本。
- `Makefile`：完整构建入口。

### 公开资料

- `llms.txt`：听众 Agent 的索引、阅读说明和作者联系方式。
- `chapters-01-03.md`：模型 API、渲染链路和 Tool Call。
- `chapters-04-06.md`：Context Management、Compaction 和 Cache。
- `chapters-07-09.md`：Memory、Skill 和 Subagent。

### 内部归档

- `pycon2026.md`：完整研究母稿，只用于 Git 归档和后续修订，不参与构建，也不得从 `index.html`、`llms.txt` 或其他公开资料入口链接。

### 托管成品

- `index.html`：演示入口。
- `talk_files/`：Quarto/Reveal.js 的本地运行依赖。
- `assets/llms-qr.svg`：指向公开 `llms.txt` 的二维码。
- `audio/*.mp3`：逐页讲解音频。

这些成品必须保留在 Git 中，GitHub Pages 才能直接访问。不要只提交 `index.html`。

### 构建中间文件

以下文件只在构建过程中出现，既不是源文件，也不需要托管：

- `talk.qmd`
- `audio/tts-manifest.json`
- `audio/tts-state.json`
- `scripts/__pycache__/`

`make` 成功结束后会自动删除它们。

## 构建过程

依赖：Python 3、`uvx`、Quarto。`uvx` 用于运行固定版本的 `segno` 和 `edge-tts`。

```bash
make
```

如果 `quarto` 不在 `PATH`：

```bash
make QUARTO=/path/to/quarto
```

`make` 按以下顺序执行：

1. `scripts/generate_qr.py` 读取 `pycon2026-slide.md` 中的 `llms_url`，生成 `assets/llms-qr.svg`。
2. `scripts/generate.py` 从 `pycon2026-slide.md` 生成临时 `talk.qmd` 和 TTS manifest。
3. `scripts/generate_audio.py` 使用 Edge TTS 生成发生变化的 `audio/*.mp3`。
4. 再次运行 `scripts/generate.py`，把音频路径、时长和 speaker notes 写入临时 QMD。
5. Quarto 把 `talk.qmd` 渲染为 `index.html` 和 `talk_files/`。
6. `prune-output` 删除 Quarto 附带、但页面未加载的 source map、备用模块、插件源码和字体。
7. `clean-intermediate` 删除 QMD、TTS manifest/state 和 Python 缓存，只留下源文件与托管成品。

## 编辑约定

- 修改页面内容或演讲词时，只编辑 `pycon2026-slide.md`，不要手工修改 `index.html` 或临时 `talk.qmd`。
- 修改版式时编辑 `talk.css`；修改页面行为时编辑 `header.html`。
- 修改公开资料时同步维护 `llms.txt` 和对应章节文件。
- 修改 `llms_url` 后必须重新生成二维码和 `index.html`。
- 构建完成后仍需保留生成的 HTML、Reveal.js 依赖、二维码和 MP3，供 GitHub Pages 托管。

## TTS

TTS 使用 `edge-tts 7.2.8`、男性普通话 `zh-CN-YunyangNeural` 和 `+10%` 语速。发音替换配置位于 `pycon2026-slide.md` 头部，例如将独立的 `JSON` 替换为同音英文名 `Jason`，但页面文字和 speaker notes 仍保留原始拼写。

封面的“开始演讲 · 启用声音”按钮用于取得浏览器播放授权。之后进入带音频的页面会自动播放，离开页面时停止并复位。
