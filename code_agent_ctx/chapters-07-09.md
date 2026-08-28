# Code Agent 的 Context：第七至九章资料

> 本文件收录第七章“Memory”、第八章“Skill”和第九章“Subagent、Context 隔离与协作”。为保证可独立阅读，三章实际使用的引用资料一并收录在文末。

## 快速索引

- [第七章：Memory](#七memory)
- [第八章：Skill](#八skill)
- [第九章：Subagent、Context 隔离与协作](#九subagentcontext-隔离与协作)
- [引用资料](#引用资料)

---

## 七、Memory

### 1. 指定信息如何跨越 Compaction

Compaction 会用摘要替换旧 Context，摘要模型具体保留哪些细节并不容易稳定控制。因此，“请在摘要中记住这件事”不是可靠的跨越机制。要保证指定信息在 Compact 后仍能进入 Context，Runtime 或模型必须再次召回一份不受本次 Compaction 影响的副本。

召回只有三种主导方式：

| 召回方式 | 何时发生 | 可靠性与代价 |
| --- | --- | --- |
| Runtime 确定性加载 | 构造 Context 时，按约定文件、路径条件、scope 或其他固定规则加载 | 最可靠；无条件加载会持续消耗 Context，条件加载则依赖规则命中 |
| Runtime 选择性预取 | 主模型调用前，由 Runtime 的检索或召回机制根据当前请求选择候选 | 节省 Context；预取器未命中时，模型根本看不到该信息 |
| 模型发起 Retrieval | 模型先调用文件、Memory 或 History Search Tool，下一次模型调用再读取 Tool Result | 最灵活；存在“模型已经忘记，所以也想不起应当检索”的召回悲论 |

```text
             不受当前 Compaction 影响的副本
                              |
          +-------------------+-------------------+
          |                   |                   |
          v                   v                   v
  Runtime 确定性加载    Runtime 选择性预取      模型 Tool Retrieval
```

这三种方式描述的是“由谁决定加载以及何时加载”，不规定内容最终位于 Context Head、请求附近还是 Tail；具体位置由 Agent 的 Context 构造方式决定。

这里的“Runtime 选择性预取”特指主模型调用前已经完成的候选选择与注入。凡是需要主模型先读取 description、Catalog 或索引，再决定加载正文的机制，都属于模型发起 Retrieval，不属于选择性预取。

确定性加载不依赖“当前任务看起来是否相关”的语义判断；固定触发条件满足时，它可以保证信息重新进入 Context。但“Session 启动时读过一次”还不够：如果该副本位于会被压缩的 History 中，Runtime 还必须在 Compact 后重新插入，或者从一开始就把它放在压缩范围之外。

### 2. 确定性加载：约定文件与分层注入

当前 Code Agent 最常见的方案是：约定一组 Markdown 文件名和发现顺序，由 Runtime 在构造 Context 时自动加载。除 Cline 尚未找到 nested `AGENTS.md` 的官方证据外，下表其他 Agent 都以某种方式支持根目录与子目录规则；表格因此不再重复“支持分层”，而是展示默认文件约定、模型可见位置和 Compact 后的恢复行为。这里仅讨论无条件加载与 path / glob 等确定性条件加载，不把需要模型判断的 `model-decision` 或 Skill 激活归入其中。

| Agent | 默认约定 | Context 位置与 Compact 后恢复 |
| --- | --- | --- |
| Codex | 全局与项目 `AGENTS.md`；同目录 `AGENTS.override.md` 优先；可配置 fallback 文件名。Run / TUI Session 启动时，沿“项目根目录 → 当前启动目录”每层最多取一份[^codex-agents-memory] | 位于任务 History 之前；准确 API role 未公开。官方说明新 Run / TUI Session 会重建 instruction chain，但未公开同一 Session 内 Compact 后是否及如何重载 |
| Claude Code | `CLAUDE.md`、`.claude/CLAUDE.md`、`CLAUDE.local.md`、`.claude/rules/*.md`；`AGENTS.md` 需由 `CLAUDE.md` 显式 import。启动时合并当前目录与祖先规则，读取子目录文件时再加入 nested 规则[^claude-code-memory] | root / ancestor 规则位于 System Prompt 后的早期 Project Context；nested 规则位于靠近触发点的 History。Compact 后前者从磁盘重载，后者只有再次触达匹配路径时才重新加载 |
| OpenCode | 项目与全局 `AGENTS.md`；没有时 fallback 到 `CLAUDE.md`；还可配置任意 instructions 文件。首次 Read 子目录文件时，向上发现 nested `AGENTS.md`[^opencode-memory][^opencode-memory-source] | root instructions 每个普通 LLM step 从文件重读，位于 Provider base prompt 后的 System 区，不参与摘要。Nested 正文追加到当前 Read Tool Result，参与 Compact 且不保证重载 |
| Gemini CLI | `GEMINI.md`；`context.fileName` 可改成一个或多个名称，例如同时读 `AGENTS.md`、`CONTEXT.md`、`GEMINI.md`。全局、workspace 与 ancestor 先加载，触达子目录时 JIT 发现 nested 文件[^gemini-cli-memory][^gemini-cli-memory-source] | 全局文件在 System，不参与默认 chat compression；workspace / ancestor 在 Initial User，压后重插；nested 文件在 Tool Result，压后只依赖摘要，且已加载路径集合会阻止同 Session 自动重注入 |
| Cursor | 根目录与子目录 `AGENTS.md`，工作涉及子目录时合并父子规则，更近规则优先；`.cursor/rules/*.mdc` 的 always 与 glob 模式也属于确定性加载[^cursor-rules-memory] | 适用的 Rules 位于模型 Context 开头。公开文档未说明 Compaction 后的重建边界，因此不推断具体恢复行为 |
| Windsurf / Devin Desktop | root `AGENTS.md` / `agents.md` 是 always-on；子目录文件自动转成 `<directory>/**` glob；`.devin/rules/` 与兼容的 `.windsurf/rules/` 也支持 always-on 与 glob[^windsurf-agents-memory] | root 正文每条消息都位于 System Prompt；子目录规则在读写匹配路径时由 Rules Engine 注入。公开文档未描述 Compaction 内部边界，但明确说明 root 会在每条消息重新提供 |
| Cline | workspace / global `.clinerules/`，也识别 root `AGENTS.md` 与 `~/.agents/AGENTS.md`。**公开文档没有证据表明 nested `AGENTS.md` 会分层合并**；路径分层使用带 `paths` 条件的 `.clinerules`[^cline-memory][^cline-memory-source] | 无条件 Rules 位于 System Prompt，不参与 messages compaction；条件 Rules 根据用户消息、打开/可见文件和编辑路径重新匹配 |
| GitHub Copilot coding agents | `.github/copilot-instructions.md`、`.github/instructions/*.instructions.md`；也支持仓库内多个 `AGENTS.md`，最近文件优先，或根目录单个 `CLAUDE.md` / `GEMINI.md`[^github-copilot-instructions] | Repository-wide 与命中 `applyTo` glob 的 path-specific 规则会自动加到请求。准确 API role、祖先 `AGENTS.md` 的全量拼接规则与 Compact 后恢复行为均未公开 |

确定性加载能否稳定跨越 Compaction，取决于可见副本位于不参与摘要的 Head，还是位于会被压缩的 History。OpenCode root instructions、Gemini 全局文件与 Cline System Rules 可以明确前者；Claude Code 则明确说明 root / ancestor 规则压后重载。对 Codex、Cursor 和 GitHub Copilot 等未公开精确边界的实现，不因“支持约定文件”就进一步推测 Compaction 行为。

### 3. 渐进式披露：让约定文件成为稳定索引

渐进式披露（Progressive Disclosure）是指：先向模型提供一层稳定、短小、可发现的索引，只有当任务命中某个条件时，才加载对应正文。对约定文件而言，根 `AGENTS.md` / `CLAUDE.md` / `GEMINI.md` 最有价值的用法不是容纳全部项目知识，而是成为 Compact 后仍会出现的召回入口。

```markdown
# 始终有效的最小规则

- 修改代码后运行与变更范围对应的测试。
- 不要把密钥或生产数据写入仓库。

# 按需读取的项目索引

- 修改数据库 schema 前，读取 `docs/agent/database.md`。
- 修改鉴权或权限检查时，读取 `docs/agent/security.md`。
- 处理发布、回滚或生产故障时，读取 `docs/agent/operations.md`。
- 需要追溯架构决定时，先查看 `docs/adr/index.md`。
```

对于未内建文件引用语法的 Agent，上述路径与触发条件是普通自然语言 instructions；模型判断命中后，用 Read Tool 发起 JIT Retrieval。读取结果进入 Tail，以后仍可能被 Compact，但根索引会继续提供再次读取的线索。

要区分两种看起来都像“拆分文件”的行为：

| 写法 | 正文何时进入 Context | 是否真正节省首轮 Context |
| --- | --- | --- |
| `CLAUDE.md` / `GEMINI.md` 中的 `@file` import | Runtime 在加载约定文件时展开正文 | 否；这只是文件组织方式 |
| 索引中写明“什么时候读哪个文件” | 模型命中条件后调用 Read Tool | 是；属于模型发起 Retrieval |

这个索引必须短，每条同时写明触发条件和路径。只写“详情见 `docs/`”会让模型不知道何时该读、读哪份；把所有被引用文件用 import 直接展开，又会退化回全量预加载。

### 4. 除了确定性加载，还有哪些主流方案

下表不再重复根约定文件。Compaction 一列只描述已经进入 Context 的 model-visible copy；位于文件、SQLite、远程数据库或 Store 中的副本本身不会被摘要。

| 实现 | 如何召回 | Context 位置 | Compaction 后 |
| --- | --- | --- | --- |
| Codex Local Memories[^codex-local-memories] | Runtime 从已 idle 的合格旧 Chats 后台抽取；开启 injection 后选择性注入未来 Sessions | 候选算法、role 和相对位置未公开 | 未公开 |
| Claude Code Auto Memory[^claude-code-memory] | 启动时确定性加载 `MEMORY.md` 前 200 行或 25 KB；模型根据该索引用文件 Tool 读取 topic files | 索引在早期 Project Context；topic 正文在 Tail / Tool Result | 索引从磁盘重载；已读 topic 正文不保证重载 |
| Gemini CLI 私有项目 Memory[^gemini-cli-memory][^gemini-cli-memory-source] | Runtime 确定性加载 `MEMORY.md` 索引；目录中的详细文件由模型 JIT 读取 | 索引在 System instruction；详细文件进入 Tool Result | 索引重建；已读正文可能只剩摘要 |
| Cline Memory Bank[^cline-memory][^cline-memory-source] | Rules 提醒模型读写一组项目 Markdown；是否读取由模型判断 | Tail / Tool Result | 已读正文参与 messages compaction，不保证重载 |
| Windsurf Memories[^windsurf-memory] | Cascade 可在会话中自动生成 workspace Memory，也接受用户显式要求；相关内容会被自动召回，但公开资料未说明由 Runtime 还是主模型完成选择 | 未公开；不应假定为固定 System Head | 未公开 |
| GitHub Copilot Memory[^github-copilot-memory] | 与当前工作相关的 repository facts 和 user preferences 会被自动召回；repository fact 在使用前以 citation 对当前 branch 重新验证，但公开资料未说明候选选择机制 | 准确 role、位置和排序算法未公开 | 未公开；未使用的条目 28 天后自动删除，成功验证和使用可重置期限 |
| Devin Knowledge[^devin-knowledge] | 每条对象带 `trigger_description`；当前工作命中 Trigger 时自动召回，也可用 macro 显式召回或绑定 repository 固定使用 | 未公开 | 未公开 |
| Letta Memory Blocks 与 Recall[^letta-searchable-history] | 已挂载 Block 每轮重新进入，模型可用 Memory Tools 修改；被 eviction 的旧 Messages 可用 Retrieval Tools 搜索 | attached blocks 位于 System Prompt；Recall 结果位于近期 History / Tool Result | attached blocks 仍然重载；所有旧 Messages 仍在数据库中可取回 |
| Mem0[^mem0-memory-service] | 每轮前由 Runtime 执行 `search`，或把 Memory Search 暴露为 Tool；可按 user / agent / run 与 metadata 限定 scope | 由接入 Agent 决定：预取块或 Tool Result | 服务内副本不受影响；下一轮是否再召回取决于 Runtime |
| Zep[^zep-memory-service] | Runtime 每轮获取 Context Block，或把 `graph.search()` 作为 Tool；可从 Thread、User Graph 和 standalone graph 组装候选 | 由接入 Agent 决定：预取 Context Block 或 Tool Result | Graph 中副本不受影响；下一轮是否再召回取决于 Runtime |
| Supermemory[^supermemory-service] | 由 wrapper 搜索后自动注入，或由模型显式调用 Tool；`containerTag` 用于 namespace 隔离 | 由 wrapper / Agent 决定 | Store 中副本不受影响；注入副本仍可被 Compact |

Codex Local Memories、Windsurf Memories、Copilot Memory 和 Devin Knowledge 都表现为自动相关性召回，但公开资料没有说明候选选择是否完全由 Runtime 在主模型调用前完成，因此不能直接归类为 Runtime 选择性预取。它们也没有公开候选如何排名、候选被插入哪个 API role，以及与 Compaction 的精确边界。Mem0、Zep 和 Supermemory 只负责保存与返回候选，最终 Context 布局与压后重载策略仍由接入它们的 Agent Runtime 决定。

### 5. 一个完整实例：Gemini CLI

Gemini CLI revision `5411f113` 最适合观察这个问题，因为源码明确把同一种 Markdown 持久层放进三个不同的 Context 区域。下面省略普通 Agent instructions 和无关 History。[^gemini-cli-memory-source][^gemini-cli-compaction]

Compact 前：

```text
systemInstruction:
    ...普通 Gemini CLI instructions...

    <global_context>
      ~/.gemini/GEMINI.md
    </global_context>

    <user_project_memory>
      私有项目 MEMORY.md 索引
    </user_project_memory>

contents:
    user:
      <session_context>
        当前目录、日期、操作系统等环境信息

        <loaded_context>
          <extension_context>Extension GEMINI.md</extension_context>
          <project_context>Workspace / ancestor GEMINI.md</project_context>
        </loaded_context>
      </session_context>

    ...较旧的 user / model / tool History...

    tool:
      原始 Tool Result

      --- Newly Discovered Project Context ---
      首次触达子目录时发现的 nested GEMINI.md
      --- End Project Context ---

    ...近期 user / model / tool History...
```

Compact 后：

```text
systemInstruction:
    ...普通 Gemini CLI instructions...
    <global_context>从 ~/.gemini/GEMINI.md 重新构造</global_context>
    <user_project_memory>从私有项目 MEMORY.md 重新构造</user_project_memory>

contents:
    user:
      <session_context>
        当前环境信息
        <loaded_context>
          <extension_context>从 Extension Context 重新构造</extension_context>
          <project_context>从 Workspace / ancestor GEMINI.md 重新构造</project_context>
        </loaded_context>
      </session_context>

    user:
      <state_snapshot>对较旧 History 的有损 continuation state</state_snapshot>

    model:
      Got it. Thanks for the additional context!

    ...未压缩的近期 raw window...
```

全局 `GEMINI.md` 和私有 `MEMORY.md` 索引位于 System；Workspace / ancestor `GEMINI.md` 位于 Initial User，但压后从文件重建；nested `GEMINI.md` 位于 Tool Result，如果落入被压缩的旧前缀，就只剩 `state_snapshot` 可能保留的内容。

## 八、Skill

### 1. Skill 的两部分：Catalog 与正文

Skill 是一组可按需加载的 instructions、references、scripts 和 assets；它本身不是 Tool，也不会自行执行。Agent Skills 规范采用渐进披露：启动时只提供短目录，激活时才加载完整 `SKILL.md`，其他资源继续按需访问。规范没有规定具体 Message role、去重或 Compaction 生命周期。[^agent-skills-spec]

```text
Skill Catalog
name + description + path
→ 通常进入 Context Head
→ 是正文的稳定召回入口

SKILL.md
完整 instructions
→ 原始文件位于 Context Outside
→ 激活后才进入 Conversation / Tool Result
```

以 Codex 为例，初始 Catalog 最多占 Context Window 的 2%；窗口未知时最多 8,000 字符。超限后会先缩短 descriptions，必要时省略部分 Skills。[^openai-skills] 因此系统里可以保存很多 Skills，但当前作用域只应启用真正相关的部分。

### 2. 激活后发生什么

```text
Runtime 提供 Skill Catalog
→ 用户显式指定，或模型根据 description 选择
→ 模型请求激活 Skill
→ Runtime 读取并返回完整 SKILL.md
→ 模型按正文读取 references、运行 scripts 或调用其他 Tools
```

Catalog 与完整正文有不同的 Compaction 命运：Catalog 通常由 Runtime 在每次 Context 构造时重新放入前部；正文则常作为一次 Conversation message 或 Tool Result 进入 History，可能被摘要或删除。

所以真正需要检查的不是“产品支持 Skill 吗”，而是三个问题：正文进入 Context 的哪里、是否允许重复激活、Compact 后谁负责恢复正文。

### 3. 主流 Agent 的 Skill 实现对照

| Agent | Catalog 位置 | 激活后的正文位置 | 重复激活 | Compact 后恢复 |
| --- | --- | --- | --- | --- |
| Codex[^openai-skills] | 初始 Context；准确 role 未公开 | 未公开 | 未公开 | 未公开 |
| Claude Code[^claude-code-skills] | 早期 Context + `Skill` Tool | Conversation message | 相同正文只加入短提示 | 自动重挂载；每个 Skill 5,000 tokens、合计 25,000 tokens |
| Gemini CLI[^gemini-cli-skills][^gemini-cli-skills-source] | System prompt | `activate_skill` Tool Result | 可重复 | 没有发现 Skill 专用恢复流程 |
| GitHub Copilot CLI[^github-copilot-skills] | Agent Context，准确位置未公开 | Agent Context，准确 role 未公开 | 未公开 | 未公开 |
| OpenCode[^opencode-skills][^opencode-skills-source] | System 的 `<available_skills>` | `skill` Tool Result 中的 `<skill_content>` | 可重复 | 随旧 History 摘要；没有 active Skill 自动重载 |
| OpenHands[^openhands-skills][^openhands-skills-source] | 前部 `<available_skills>` | `invoke_skill` Tool Result | 标准 Skill 可重复 | 没有发现完整正文恢复流程 |
| Cursor[^cursor-skills] | 启动时发现；准确位置未公开 | attaches to one message | 未公开 | 未公开 |

这张表显示，各产品的共同部分只有“Catalog 先进入、正文按需进入”。Claude Code 明确实现了压后重挂载；Gemini CLI、OpenCode 和 OpenHands 没有发现等价机制。任务持续依赖某个 Skill 时，Compaction 后应确认正文是否仍可见，必要时显式重新激活。

### 4. OpenCode + Qwen / DeepSeek Jinja：Compact 前后真实 Context

OpenCode revision `3a31c4ea` 负责构造 System、Skill Catalog、`skill` Tool 和 History；下面再分别使用 Qwen3-Coder 与 DeepSeek-V3.1 的公开格式。两份实现处理的是同一套语义消息，因此 Catalog、Skill 正文、Summary 和 raw tail 是否存在的结论相同，具体控制 token 与 Tool 协议不同。`〔……〕` 是讲义中的省略标记；控制标记、包裹关系和 Compaction 后的 Message 顺序来自公开实现，业务内容则沿用本文的数学示例。[^opencode-skills-source][^opencode-compaction][^qwen3coder-template][^deepseek-v31-template]

Qwen：Skill 已加载、尚未 Compact 时：

```text
<|im_start|>system
〔OpenCode provider instructions、environment、项目 instructions〕

Skills provide specialized instructions and workflows for specific tasks.
Use the skill tool to load a skill when a task matches its description.
<available_skills>
  <skill>
    <name>verified-math</name>
    <description>对有限整数集合进行精确计数与求和；使用 Python 执行并核验结果。</description>
    <location>/workspace/.opencode/skills/verified-math/SKILL.md</location>
  </skill>
</available_skills>

# Tools

You have access to the following functions:

<tools>
<function>
<name>skill</name>
<description>Load a specialized skill when the task at hand matches one of the skills listed in the system prompt.

Use this tool to inject the skill's instructions and resources into current conversation. The output may contain detailed workflow guidance as well as references to scripts, files, etc in the same directory as the skill.

The skill name must match one of the skills listed in your system prompt.</description>
<parameters>
<parameter>
<name>name</name>
<type>string</type>
<description>The name of the skill from available_skills</description>
</parameter>
<required>["name"]</required>
</parameters>
</function>
〔其他 OpenCode Tools〕
</tools>

〔Qwen 模板固定的 Tool Call 格式说明〕<|im_end|>
<|im_start|>user
求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。<|im_end|>
<|im_start|>assistant
<tool_call>
<function=skill>
<parameter=name>
verified-math
</parameter>
</function>
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
<skill_content name="verified-math">
# Skill: verified-math

# Verified Math

1. 将条件编码为可检查的布尔表达式。
2. 使用 Python 枚举有限范围。
3. 同时核验数量与总和。

Base directory for this skill: /workspace/.opencode/skills/verified-math
Relative paths in this skill are relative to this base directory.
Note: file list is sampled.

<skill_files>
<file>/workspace/.opencode/skills/verified-math/scripts/verify.py</file>
</skill_files>
</skill_content>
</tool_response>
<|im_end|>
<|im_start|>assistant
〔使用 Skill 后产生的后续 Tool Calls 与结果〕<|im_end|>
<|im_start|>user
请继续核验并给出最终结果。<|im_end|>
<|im_start|>assistant
```

假设 `skill` 调用和完整 `<skill_content>` 已落入被压缩的 old head，而最后一轮仍作为 raw tail 保留。Qwen 的 Compact 后请求变成：

```text
<|im_start|>system
〔OpenCode 再次构造相同的 provider instructions、environment、项目 instructions〕

Skills provide specialized instructions and workflows for specific tasks.
Use the skill tool to load a skill when a task matches its description.
<available_skills>
  <skill>
    <name>verified-math</name>
    <description>对有限整数集合进行精确计数与求和；使用 Python 执行并核验结果。</description>
    <location>/workspace/.opencode/skills/verified-math/SKILL.md</location>
  </skill>
</available_skills>

# Tools

You have access to the following functions:

<tools>
<function>
<name>skill</name>
〔与 Compact 前相同的 description 与 parameters〕
</function>
〔其他 OpenCode Tools〕
</tools>

〔Qwen 模板固定的 Tool Call 格式说明〕<|im_end|>
<|im_start|>user
What did we do so far?<|im_end|>
<|im_start|>assistant
目标：计算指定整数集合的数量与总和。
已完成：调用 verified-math，并开始用 Python 核验。
下一步：检查枚举结果并回答用户。
〔真实 Summary 由 Compaction 模型生成；它可能保留更多或更少的 Skill 细节〕<|im_end|>
<|im_start|>user
请继续核验并给出最终结果。<|im_end|>
<|im_start|>user
Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed.<|im_end|>
<|im_start|>assistant
```

同一组 messages 使用 DeepSeek-V3.1 non-thinking 协议时，Skill 已加载、尚未 Compact 的格式化结果是：

```text
<｜begin▁of▁sentence｜>〔OpenCode provider instructions、environment、项目 instructions〕

Skills provide specialized instructions and workflows for specific tasks.
Use the skill tool to load a skill when a task matches its description.
<available_skills>
  <skill>
    <name>verified-math</name>
    <description>对有限整数集合进行精确计数与求和；使用 Python 执行并核验结果。</description>
    <location>/workspace/.opencode/skills/verified-math/SKILL.md</location>
  </skill>
</available_skills>

## Tools
You have access to the following tools:

### skill
Description: Load a specialized skill when the task at hand matches one of the skills listed in the system prompt.

Parameters: {"type":"object","properties":{"name":{"type":"string","description":"The name of the skill from available_skills"}},"required":["name"]}

〔其他 OpenCode Tools〕
〔DeepSeek-V3.1 固定的 Tool Call 格式说明〕
<｜User｜>求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。<｜Assistant｜></think><｜tool▁calls▁begin｜><｜tool▁call▁begin｜>skill<｜tool▁sep｜>{"name":"verified-math"}<｜tool▁call▁end｜><｜tool▁calls▁end｜><｜end▁of▁sentence｜><｜tool▁output▁begin｜><skill_content name="verified-math">
# Skill: verified-math

# Verified Math

1. 将条件编码为可检查的布尔表达式。
2. 使用 Python 枚举有限范围。
3. 同时核验数量与总和。

Base directory for this skill: /workspace/.opencode/skills/verified-math
Relative paths in this skill are relative to this base directory.
Note: file list is sampled.

<skill_files>
<file>/workspace/.opencode/skills/verified-math/scripts/verify.py</file>
</skill_files>
</skill_content><｜tool▁output▁end｜>〔使用 Skill 后产生的后续 Tool Calls 与结果〕<｜end▁of▁sentence｜><｜User｜>请继续核验并给出最终结果。<｜Assistant｜></think>
```

同一 History Compact 后，DeepSeek 格式化结果变为：

```text
<｜begin▁of▁sentence｜>〔OpenCode 再次构造相同的 provider instructions、environment、项目 instructions〕

Skills provide specialized instructions and workflows for specific tasks.
Use the skill tool to load a skill when a task matches its description.
<available_skills>
  <skill>
    <name>verified-math</name>
    <description>对有限整数集合进行精确计数与求和；使用 Python 执行并核验结果。</description>
    <location>/workspace/.opencode/skills/verified-math/SKILL.md</location>
  </skill>
</available_skills>

## Tools
You have access to the following tools:

### skill
〔与 Compact 前相同的 description 与 parameters〕
〔其他 OpenCode Tools〕
〔DeepSeek-V3.1 固定的 Tool Call 格式说明〕
<｜User｜>What did we do so far?<｜Assistant｜></think>目标：计算指定整数集合的数量与总和。
已完成：调用 verified-math，并开始用 Python 核验。
下一步：检查枚举结果并回答用户。
〔真实 Summary 由 Compaction 模型生成；它可能保留更多或更少的 Skill 细节〕<｜end▁of▁sentence｜><｜User｜>请继续核验并给出最终结果。<｜User｜>Continue if you have next steps, or stop and ask for clarification if you are unsure how to proceed.<｜Assistant｜></think>
```

对比可以直接看到：

1. Catalog 与 `skill` Tool 属于每次普通 step 重新构造的稳定前部，所以 Compact 后仍在。
2. 完整 `<skill_content>` 属于旧 History；一旦落入 compressed head，Compact 后不会自动出现，只可能有部分内容残留在 Summary。
3. OpenCode 没有根据“已激活 Skill”自动重载正文；Catalog 只让模型重新知道 Skill 存在，不能保证模型一定再次调用。

## 九、Subagent、Context 隔离与协作

### 1. Subagent 是 Context 隔离

1. 主 Agent 为边界明确的子任务创建独立 Agent Loop；每个 Subagent 拥有自己的 history、context window、Tool Loop 和局部计划。
2. Subagent 不等于 Context Compression：它没有把同一份信息变短，而是让不同任务的细节分别停留在不同 Context 中。
3. Subagent 也没有扩大单个模型的 Context Window；它创建了多个窗口，并把问题从“一个窗口如何容纳全部信息”转换成“窗口之间必须传递什么”。
4. 下文把负责分派、等待和汇总的主 Agent 称为 Coordinator（协调者），把执行隔离子任务的 Subagent 称为 Worker（工作 Agent）。
5. 主 Agent 不应复制完整 history；它只交付最小任务包（Task Packet，即目标、约束和证据入口），Subagent 自己读取必要文件和资料，最后返回较短的证据包（Evidence Packet，即结论、验证结果和原始证据指针）。
6. 如果所有 Subagent 都继承主 Agent 的完整 history，或者持续同步彼此的完整 history，隔离收益会消失，只剩重复 input、更多 output 和 cache 分叉。

### 2. 用法一：隔离具体任务产生的大量细节

1. 假设主 Agent 需要读取 10 个 URL，并为每个页面生成摘要。如果主 Agent 自己依次调用抓取工具，10 份 HTML、解析结果、失败重试和中间判断都会进入主 trajectory，并在后续多轮请求中继续占用 Context。
2. 不需要为 10 个 URL 创建 10 个 Subagent。主 Agent 可以只创建一个 Research Subagent，交付 URL 列表和摘要要求；Research Subagent 在一次 assistant 输出中发出 10 个 `fetch_url` Tool Calls，Runtime 并行执行，再把全部结果返回该 Subagent。受支持的模型和 API 可以在一个 turn 中返回多个 Function Calls；实际是否并行执行由 Runtime 决定。[^openai-parallel-functions]

```text
Main Agent
    ↓ 一个 Task Packet：10 个 URL + 摘要要求
Research Subagent
    ↓ 一次输出 10 个 fetch_url Tool Calls
Runtime
    ↓ 并行抓取 URL 1 ... URL 10
Research Subagent
    ↓ 读取 10 份 HTML，生成 summaries + sources
Main Agent
    ↓ 只接收一个 Evidence Packet
```

3. 10 份 HTML、抓取错误和局部分析轨迹只进入 Research Subagent 的 Context 或 artifact；主 Agent 只接收一次汇总结果，避免 10 组 Task Packet、Subagent 初始化和任务交接（Handoff）。
4. 这种设计把主 Agent 与原始 HTML 隔离，但没有把 10 份 HTML 彼此隔离：Research Subagent 的下一次模型请求仍要同时容纳全部 Tool Results。如果总量超过分配给它的 Context 容量（Context budget），才需要分批，或者使用少量多个 Subagent，而不是机械地每个 URL 一个 Agent。
5. 这种用法成立的条件是“Worker 内部产生的信息”远大于“跨边界返回的信息”。如果主 Agent 最后仍必须读取全部 HTML，Context 隔离收益就很小。
6. 同样的模式适用于日志分析、仓库分区搜索、资料核查和大型测试输出：局部细节留在 Worker，结论和证据指针返回 Coordinator。

### 3. 用法二：并发缩短实际经过时间（Wall-clock Time）

1. 必须区分两个并发层级：

```text
Tool-level parallelism：同一个 Agent Context 内，并行执行多个独立 Tool Calls
Agent-level parallelism：多个独立 Agent Context，同时执行不同任务
```

2. 同一 Context 隔离边界内的独立输入/输出操作（I/O），优先使用 Parallel Tool Calls。模型一次返回多个 calls，Runtime 并发执行；它比为每个调用创建 Subagent 少了 Task Packet、独立 Agent Loop 和 Handoff。
3. Parallel Tool Calls 通常采用“分叉—汇合”（fork-join）：先并行启动多个调用，再等待它们全部进入 success、error 或 timeout（超过规定等待时间）终态，才进行下一次模型推理。因此一个 Research Subagent 能并行抓取 10 个 URL，却通常要收齐这一批结果后才开始统一摘要。
4. 多个真正独立的模型任务才需要 Agent-level parallelism：

```text
顺序执行：T ≈ T1 + T2 + ... + Tn
并发执行：T ≈ max(T1, T2, ..., Tn) + 协调开销
```

5. 多个 Subagent 可以让 Tool 执行和各自的摘要生成都并行；一个 Subagent 加 Parallel Tool Calls 只能并行 Tool 执行，最终摘要仍由一条自回归生成序列完成。前者可能更快，后者通常更便宜。
6. Agent-level parallelism 通常减少完成任务的墙上时间，但不会自动减少总模型计算、Token 或工具成本；多个 Subagent 可能使用更多总资源。
7. 最适合 Agent-level parallelism 的是相互独立的只读搜索、分析和验证。多个 Agent 同时修改同一文件、数据库或外部系统时，仍需要任务分区、独立 Git 工作树（worktree）、事务或最终由主 Agent 串行合并。
8. 有强依赖的任务不能因为拆成 Subagent 就真正并发；如果 Worker B 必须等待 Worker A 的完整结果，委派只会增加交接成本。
9. Agent 数量应由 Context 隔离边界决定，而不是由 Tool Call 数量决定：先使用 Tool 并发；只有一个 Context 装不下、摘要阶段也必须并行，或者任务本来就不应共享信息时，才增加 Subagent。

### 4. 用法三：隔离“不应知道彼此”的任务

1. 有些任务不仅不需要共享 Context，刻意隔离还能提高结果可信度。例如实现代码和编写单元测试可以由两个 Agent 分别完成。
2. Code Agent 与 Test Agent 共享同一份需求、公开接口、基线版本和验收条件，但在初次工作时不读取对方的私有 trajectory：

```text
                   同一份 specification
                      /           \
             Code Agent         Test Agent
          实现生产代码          独立设计测试
                      \           /
                    Coordinator 验证
```

3. Test Agent 如果提前看到实现细节，可能只复述实现中的分支和假设，写出“证明当前实现正确”的测试；独立工作更容易发现规格遗漏、边界条件和实现者的错误假设。
4. 两边完成后，Coordinator 才把实现和测试放到同一基线上运行，比较失败证据，并决定接受、修正或重新分配。
5. 隔离必须由 Runtime 的 Context、文件和权限边界实现，不能只依赖一句“请假装没看见”。如果两个 Agent 共享同一工作目录，需要分别限制可见文件，或使用不同状态快照（snapshot）或 Git worktree。
6. 独立 review、红队/蓝队（red-team / blue-team，即一方主动寻找攻击或失败路径、另一方负责防守和验证）、候选方案盲评也属于同一种用法。

### 5. Task Packet、私有 Context 与 Evidence Packet

1. 主 Agent 交付的最小 Task Packet 包括：
   - 子任务目标和明确不在范围内的事项；
   - 必须遵守的硬约束与权限；
   - 可读取的文件、URL、Memory scope 和 artifact pointer；
   - 基线版本或 commit；
   - 成功条件、验证方式和输出格式。
2. Runtime 可以自动附加稳定项目规则、Tools、Workspace、预算和凭据边界，避免主 Agent 用昂贵的 output token 反复生成固定模板文本（boilerplate）。
3. 一个 Worker 的 Context 应接近：

```text
Stable Instructions
+ Small Task Packet
+ Selected Shared Memory
+ On-demand Artifacts
+ Private Local Trajectory
```

4. Subagent 的完整 history、原始网页、搜索过程和失败日志默认不返回主 Agent。
5. Evidence Packet 只需包含：
   - 完成状态与结论；
   - 发现的问题和适用边界；
   - patch、commit、测试日志或其他 artifact ID；
   - 已执行的验证；
   - 未解决问题和建议下一步。
6. 交接摘要（Handoff summary）是导航信息，不是唯一事实来源；重要结论必须能重新读取原始 artifact 验证。
7. 稳定的项目规则由共享约定文件或 Runtime 预取提供；当前任务状态放在任务图（task graph，即记录子任务依赖关系和完成状态的图）或 checkpoint；完整结果放在 Artifact；局部推理过程留在私有 History。

### 6. 启动方式与成本

1. Fork：Subagent 继承主 Agent 在分叉点的 Context。背景交付简单，也可能复用共同 prefix，但会继承无关内容和错误假设。
2. Fresh Context：Subagent 只获得稳定 instructions 和 Task Packet。隔离最好，但需要生成任务说明，并承担遗漏背景的风险。
3. Persistent Specialist：长期保留固定 instructions、Tools 和 scoped Memory，只接收很短的结构化任务；可以摊薄重复背景成本，但必须治理陈旧 Memory 和跨项目污染。
4. 一次委派的额外成本包括：

```text
主 Agent 生成 Task Packet 的 output
+ Subagent 的 input 和完整 Tool Loop
+ Subagent 生成 Evidence Packet 的 output
+ 主 Agent 读取、验证和综合结果
```

5. 由于 output token 通常比 cached input 贵，频繁创建细粒度 Subagent、反复总结背景和来回同步自然语言状态，可能比单 Agent 昂贵得多。
6. 同一个隔离任务中的独立 I/O 应尽量由一个 Subagent 使用 Parallel Tool Calls 完成；这能保留 Context 隔离，同时减少重复 Task Packet、Agent 初始化和 Handoff output。
7. 对 Cache 友好的形式是稳定 Worker prefix、短结构化 Task Packet、按需读取 artifact，以及一次性返回 Evidence Packet；频繁重写共享 Context 或同步完整 history 会破坏这些收益。
8. Subagent 值得使用的判断条件是：

```text
并发收益
+ Context 隔离收益
+ 搜索覆盖或独立验证收益
>
Task Packet
+ 重复计算
+ Handoff
+ Cache 分叉
+ 验证与冲突处理成本
```

9. 边界清晰、内部轨迹很长而输出很短的任务最适合 Subagent；强顺序依赖、需要复制几乎全部背景、频繁共享写入或任务本身很短时，通常不值得委派。


## 引用资料

[^agent-skills-spec]: Agent Skills. [*Specification*](https://agentskills.io/specification). 规范定义 `SKILL.md`、frontmatter 和 progressive disclosure：metadata 在启动时加载，完整 instructions 在激活时加载，其他 resources 按需加载；规范没有定义具体 Message role、去重或 Compaction 生命周期。

[^claude-code-memory]: Anthropic. [*How Claude remembers your project*](https://code.claude.com/docs/en/memory)；[*Prompt caching*](https://code.claude.com/docs/en/prompt-caching#how-the-cache-is-organized)；[*Context windows and compaction*](https://code.claude.com/docs/en/context-window#what-survives-compaction). Claude Code 把 root `CLAUDE.md` 与 Auto Memory 放在早期 Project Context；`MEMORY.md` 启动时加载前 200 行或 25 KB，topic files 使用普通文件工具按需读取。Compact 后 root instructions 与 Auto Memory 从磁盘重注入，nested/path-scoped instructions 则要再次触发才重新加载。

[^claude-code-skills]: Anthropic. [*Extend Claude with skills — Skill content lifecycle*](https://code.claude.com/docs/en/skills#skill-content-lifecycle)；另见 [*Live change detection*](https://code.claude.com/docs/en/skills#live-change-detection). 文档明确说明 rendered `SKILL.md` 作为一条 message 留在 Session 中、相同正文再次调用只产生短提示，以及 Auto-compaction 按每个 5,000 tokens、合计 25,000 tokens 的预算重新挂载最近调用内容。

[^cline-memory]: Cline. [*Memory Bank*](https://docs.cline.bot/features/memory-bank)；[*Cline Rules*](https://docs.cline.bot/customization/cline-rules)；[*Auto Compact*](https://docs.cline.bot/features/auto-compact). Memory Bank 是由 rules 驱动模型读写普通 Markdown 文件的方法，不是独立 Memory Store 或自动检索引擎。

[^cline-memory-source]: Cline, revision [`09ee9026`](https://github.com/cline/cline/tree/09ee9026393e681a4834d8acbf4d9d5fdfa8664a). [`rules.ts`](https://github.com/cline/cline/blob/09ee9026393e681a4834d8acbf4d9d5fdfa8664a/sdk/packages/core/src/runtime/safety/rules.ts#L10-L48) 把 rules 放入 system prompt；[`compaction.ts`](https://github.com/cline/cline/blob/09ee9026393e681a4834d8acbf4d9d5fdfa8664a/sdk/packages/core/src/extensions/context/compaction.ts#L292-L320) 区分 system overhead 与 messages；[`agentic-compaction.ts`](https://github.com/cline/cline/blob/09ee9026393e681a4834d8acbf4d9d5fdfa8664a/sdk/packages/core/src/extensions/context/agentic-compaction.ts#L116-L153) 只总结旧 messages。

[^codex-agents-memory]: OpenAI Docs. [*Custom instructions with AGENTS.md*](https://learn.chatgpt.com/docs/agent-configuration/agents-md)；[*Customization*](https://learn.chatgpt.com/docs/customization/overview). Codex 每个 Run / TUI Session 启动时构造一次 instruction chain：先取全局文件，再从项目根目录走到当前启动目录，每层按 `AGENTS.override.md` 、`AGENTS.md` 和可配置 fallback 的顺序最多取一份，默认合计上限 32 KiB。它不会继续扫描启动目录之下的子目录；官方没有公开其实际 API role 或 Compaction 内部重建方式。

[^codex-local-memories]: OpenAI Docs. [*Memories*](https://learn.chatgpt.com/docs/customization/memories). Local Codex Memories 默认关闭；Codex 从已经 idle 的合格旧 chats 后台抽取内容，保存在 `~/.codex/memories/`，并分别提供 generation 与 injection 开关。该页没有公开候选选择、Context 位置或 Compaction 行为。

[^cursor-rules-memory]: Cursor. [*Rules*](https://cursor.com/docs/context/rules), accessed 2026-08-27. 文档说明 root 与 nested `AGENTS.md` 会按当前工作路径自动适用，子目录规则与父规则合并且更具体的规则优先；`.cursor/rules/*.mdc` 另支持 always、glob、model decision 和 manual 四种激活方式。

[^cursor-skills]: Cursor. [*Agent Skills*](https://cursor.com/docs/skills.md). 文档说明自动与 `/skill-name` 显式调用、显式 Skill attaches to one message、Custom Mode 可用于 Session 级持续启用，以及 references、scripts 与 assets 按需加载；内部 Message role、去重和 Compaction 行为没有公开。

[^deepseek-v31-template]: DeepSeek AI. [`deepseek-ai/DeepSeek-V3.1` 原始 `assets/chat_template.jinja`](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/assets/chat_template.jinja), revision `c0781d039fb7a1ba2abc4add0bdc293e92d2b8db`；同一 revision 的 [ToolCall 说明](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/README.md#toolcall) 规定 `{tool_description}` 的 Markdown 格式和 `<｜tool▁calls▁begin｜>` 协议，[`tokenizer.json`](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/tokenizer.json) 定义本文复现的 control-token IDs。模型 Jinja 本身处理 messages、历史 Tool Calls 和 Tool Results，但不遍历独立的 `tools` 参数。

[^devin-knowledge]: Cognition. [*Devin Knowledge*](https://docs.devin.ai/product-guides/knowledge), accessed 2026-08-27. Knowledge Item 包含正文和必填的 `trigger_description`，Devin 在当前工作相关时自动召回，也支持 macro、repository pin、organization / enterprise scope 与从会话反馈中生成新建或更新建议。公开的 [Knowledge API](https://docs.devin.ai/api-reference/v1/knowledge/create-knowledge) 也把它作为带 ID、body、trigger、folder 和 repository scope 的托管对象，而不是仓库内约定文件。

[^gemini-cli-compaction]: Google Gemini CLI, revision [`5411f113`](https://github.com/google-gemini/gemini-cli/tree/5411f113cafae26161b4969b0237b8e1e024e2c2). [`chatCompressionService.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/context/chatCompressionService.ts#L37-L121) 定义阈值、Head/Tail 切分和 Compression Model 映射；[首次摘要与校验调用](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/context/chatCompressionService.ts#L342-L411)；[压缩后 History 构造](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/context/chatCompressionService.ts#L431-L480)；[完整 Compression System Prompt](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/prompts/snippets.ts#L882-L963)。

[^gemini-cli-memory]: Gemini CLI. [*Provide context with GEMINI.md files*](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/docs/cli/gemini-md.md)；[*Memory tool*](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/docs/tools/memory.md)；[*Auto Memory*](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/docs/cli/auto-memory.md). 文档说明层级化 `GEMINI.md`、私有项目 Memory 与需要用户审核的实验性 Auto Memory。

[^gemini-cli-memory-source]: Gemini CLI, revision [`5411f113`](https://github.com/google-gemini/gemini-cli/tree/5411f113cafae26161b4969b0237b8e1e024e2c2). [`config.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/config/config.ts#L2572-L2615) 区分 system 与 initial-user tiers；[`environmentContext.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/utils/environmentContext.ts#L50-L110) 构造首条 user context；[`jit-context.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/tools/jit-context.ts#L10-L85) 把子目录 Context 追加到 Tool Result；[`chatCompressionService.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/context/chatCompressionService.ts#L239-L292) 只压缩 chat history。

[^gemini-cli-skills]: Google. [*Gemini CLI — Agent Skills*](https://geminicli.com/docs/cli/skills/). 文档给出 `system prompt Catalog → activate_skill → consent → SKILL.md body 与 folder structure 加入 conversation history` 的完整流程，以及 `/skills reload` / `/skills refresh`。

[^gemini-cli-skills-source]: Google Gemini CLI, revision [`5411f113`](https://github.com/google-gemini/gemini-cli/tree/5411f113cafae26161b4969b0237b8e1e024e2c2). [`activate-skill.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/tools/activate-skill.ts) 返回 `<activated_skill>` Tool Result；[`skillManager.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/skills/skillManager.ts) 保存 Session 级 active names；[`chatCompressionService.ts`](https://github.com/google-gemini/gemini-cli/blob/5411f113cafae26161b4969b0237b8e1e024e2c2/packages/core/src/context/chatCompressionService.ts) 展示通用 History 摘要和后缀保留流程，未包含 Skill 专用重新挂载分支。

[^github-copilot-instructions]: GitHub Docs. [*Adding repository custom instructions for GitHub Copilot*](https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot), accessed 2026-08-27. GitHub Copilot coding agents 支持 repository-wide `.github/copilot-instructions.md`、带 `applyTo` glob 的 `.github/instructions/*.instructions.md`、仓库内多个 `AGENTS.md`，以及根目录单个 `CLAUDE.md` 或 `GEMINI.md`。官方明确说最近的 `AGENTS.md` 优先，但未公开最终 API role、全部祖先文件的精确拼接规则或 Compaction 行为。

[^github-copilot-memory]: GitHub Docs. [*Copilot Memory*](https://docs.github.com/en/copilot/concepts/agents/copilot-memory), accessed 2026-08-27. Copilot Memory 保存 repository-level facts 和 user-level preferences；repository facts 带代码 citation，在当前 branch 重新验证后才使用，并可在 Copilot cloud agent、code review 与 CLI 之间共享。未使用条目默认 28 天后删除；官方未公开最终 Context 位置与 Compaction 行为。

[^github-copilot-skills]: GitHub. [*Adding agent skills for GitHub Copilot CLI*](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills). 文档说明 Copilot 根据 Prompt 与 description 选择 Skill，将 `SKILL.md` 注入 Agent Context，并提供 `/skills reload`；没有公开去重和 Compaction 细节。

[^letta-searchable-history]: Letta. [*Stateful agents*](https://docs.letta.com/guides/agents/memory) 说明 Memory Blocks 可由 Agent 通过 Memory Tools 编辑，而所有 Messages 在 Compaction / eviction 后仍被 API 保存，开发者可通过 API、Agent 可通过 Retrieval Tools 取回。Letta Code revision [`0521b230`](https://github.com/letta-ai/letta-code/tree/0521b230fe0f4fbed00ceab40c66a2ae55d3be7e) 的 [`recall_subagent.md`](https://github.com/letta-ai/letta-code/blob/0521b230fe0f4fbed00ceab40c66a2ae55d3be7e/src/agent/prompts/recall_subagent.md#L1-L97) 进一步公开了对 Agent Messages 执行混合、向量或全文搜索，再按时间邻域展开原文的 Recall 流程。

[^mem0-memory-service]: Mem0. [*Platform Quickstart*](https://docs.mem0.ai/platform/quickstart)；[*How Mem0 Works*](https://docs.mem0.ai/core-concepts/how-it-works)；[*Entity-Scoped Memory*](https://docs.mem0.ai/platform/features/entity-scoped-memory)；[*Mem0 MCP*](https://docs.mem0.ai/platform/mem0-mcp). Mem0 接收带 entity scope 的写入，在服务端抽取、索引和持久化，再通过受 scope/filter 限制的搜索返回候选；MCP 是可选的模型 Tool 接口。

[^openai-parallel-functions]: OpenAI. [*Function calling: Parallel function calling*](https://developers.openai.com/api/docs/guides/function-calling#parallel-function-calling). 受支持的模型可以在一次 turn 中选择调用多个 functions；`parallel_tool_calls: false` 可以把一次输出限制为零个或一个 Tool Call。模型负责提出调用，实际并发、超时和副作用调度由 Agent Runtime 执行。

[^openai-skills]: OpenAI. [*Build skills*](https://learn.chatgpt.com/docs/build-skills). 文档说明 Skill 使用 progressive disclosure：初始目录提供 name、description 和路径，显式或隐式选择后再读取完整 `SKILL.md`；Codex 的初始 Skill Catalog 最多占 context window 的 2%，窗口未知时最多 8,000 字符，超出预算时会先缩短 description，必要时省略部分 Skills。

[^opencode-compaction]: OpenCode, revision [`03bba464`](https://github.com/anomalyco/opencode/tree/03bba464d46f3eddf74195919b1344aa937f7b11). [`packages/opencode/src/session/compaction.ts`](https://github.com/anomalyco/opencode/blob/03bba464d46f3eddf74195919b1344aa937f7b11/packages/opencode/src/session/compaction.ts#L54) 处理转录、Tail 选择、模型调用与摘要保存；[摘要请求构造](https://github.com/anomalyco/opencode/blob/03bba464d46f3eddf74195919b1344aa937f7b11/packages/opencode/src/session/compaction.ts#L319)；[Compaction Agent Prompt](https://github.com/anomalyco/opencode/blob/03bba464d46f3eddf74195919b1344aa937f7b11/packages/opencode/src/agent/prompt/compaction.txt)；[`message-v2.ts`](https://github.com/anomalyco/opencode/blob/03bba464d46f3eddf74195919b1344aa937f7b11/packages/opencode/src/session/message-v2.ts#L521) 重排 Compaction 问题、Summary 与保留的近期 Turns；[`compaction.ts`](https://github.com/anomalyco/opencode/blob/03bba464d46f3eddf74195919b1344aa937f7b11/packages/opencode/src/session/compaction.ts#L500-L547) 追加 synthetic continue user message。同一仓库的 V2 Core 仍在建设，内部表示不同。

[^opencode-memory]: OpenCode. [*Rules*](https://opencode.ai/docs/rules)；[*Config: Compaction*](https://opencode.ai/docs/config#compaction)；[*Ecosystem*](https://opencode.ai/docs/ecosystem). OpenCode 官方文档公开 `AGENTS.md` / `CLAUDE.md` fallback、custom instructions 和自动 Compaction；Supermemory 只作为第三方 plugin 出现在生态页，不是内建 Auto Memory。

[^opencode-memory-source]: OpenCode, revision [`105b398c`](https://github.com/anomalyco/opencode/tree/105b398c2a9ff2f16eaae409836e1dbc4d37671a). [`instruction.ts`](https://github.com/anomalyco/opencode/blob/105b398c2a9ff2f16eaae409836e1dbc4d37671a/packages/opencode/src/session/instruction.ts#L60-L220) 发现根规则与惰性子目录规则；[`prompt.ts`](https://github.com/anomalyco/opencode/blob/105b398c2a9ff2f16eaae409836e1dbc4d37671a/packages/opencode/src/session/prompt.ts#L1257-L1283) 每个普通 step 重读 system instructions；[`request.ts`](https://github.com/anomalyco/opencode/blob/105b398c2a9ff2f16eaae409836e1dbc4d37671a/packages/opencode/src/session/llm/request.ts#L56-L112) 把它们放在 messages 前；[`read.ts`](https://github.com/anomalyco/opencode/blob/105b398c2a9ff2f16eaae409836e1dbc4d37671a/packages/opencode/src/tool/read.ts#L300-L365) 把惰性规则追加到 Tool Result；[`compaction.ts`](https://github.com/anomalyco/opencode/blob/105b398c2a9ff2f16eaae409836e1dbc4d37671a/packages/opencode/src/session/compaction.ts#L358-L448) 以空 system 摘要 messages。

[^opencode-skills]: OpenCode. [*Agent Skills*](https://opencode.ai/docs/skills/). 文档说明模型用统一的 `skill({name})` 按需加载正文，并给出 `<available_skills>` Catalog 的公开格式。

[^opencode-skills-source]: OpenCode, revision [`3a31c4ea`](https://github.com/anomalyco/opencode/tree/3a31c4ea801915c0b050df4b3842997ea62b6e93). [`system.ts`](https://github.com/anomalyco/opencode/blob/3a31c4ea801915c0b050df4b3842997ea62b6e93/packages/opencode/src/session/system.ts) 把详细 Catalog 加入 System Prompt；[`skill.ts`](https://github.com/anomalyco/opencode/blob/3a31c4ea801915c0b050df4b3842997ea62b6e93/packages/opencode/src/tool/skill.ts) 返回 Skill 正文、位置和资源列表；[`compaction.ts`](https://github.com/anomalyco/opencode/blob/3a31c4ea801915c0b050df4b3842997ea62b6e93/packages/opencode/src/session/compaction.ts) 将 `skill` 列为普通 pruning 的 protected Tool，但没有 active Skill rehydration。

[^openhands-skills]: OpenHands. [*Skills Overview*](https://docs.openhands.dev/overview/skills.md)；[*Agent Skills & Context*](https://docs.openhands.dev/sdk/guides/skill.md). 文档分别说明标准 Agent Skill、关键词触发 Skill、路径触发 Rule 的 Catalog、调用与 Context 注入位置，并要求修改 Skill 文件后新建 Conversation。

[^openhands-skills-source]: OpenHands Software Agent SDK, revision [`94211495`](https://github.com/OpenHands/software-agent-sdk/tree/9421149592da215066f58cb68cb04599d896ae74). [`invoke_skill.py`](https://github.com/OpenHands/software-agent-sdk/blob/9421149592da215066f58cb68cb04599d896ae74/openhands-sdk/openhands/sdk/tool/builtins/invoke_skill.py) 返回标准 Skill 正文；[`agent_context.py`](https://github.com/OpenHands/software-agent-sdk/blob/9421149592da215066f58cb68cb04599d896ae74/openhands-sdk/openhands/sdk/context/agent_context.py) 处理关键词与路径触发；[`state.py`](https://github.com/OpenHands/software-agent-sdk/blob/9421149592da215066f58cb68cb04599d896ae74/openhands-sdk/openhands/sdk/conversation/state.py) 保存已调用或已触发集合。

[^qwen3coder-template]: Qwen Team. [`Qwen/Qwen3-Coder-30B-A3B-Instruct` 原始 `chat_template.jinja`](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/resolve/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/chat_template.jinja), revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Hugging Face. [可读源码页面；格式说明位于第 66 行](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/chat_template.jinja#L66)；同 revision 的 [`tokenizer.json`](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/tokenizer.json) 定义本文复现的 control-token IDs。

[^supermemory-service]: Supermemory. [*How Supermemory Works*](https://supermemory.ai/docs/concepts/how-it-works)；[*Multi-tenancy*](https://supermemory.ai/docs/concepts/multi-tenancy)；[*Container Tags*](https://supermemory.ai/docs/concepts/container-tags)；[*OpenAI SDK integration*](https://supermemory.ai/docs/integrations/openai). Supermemory 对文档执行 chunking、embedding 和索引，以 `containerTag` 隔离 namespace，并支持自动注入 wrapper 或显式 Tool 两种接入方式。

[^windsurf-agents-memory]: Windsurf / Devin Desktop. [*AGENTS.md*](https://docs.windsurf.com/windsurf/cascade/agents-md), accessed 2026-08-27. Runtime 扫描 workspace 与 Git root 以内的祖先目录；root `AGENTS.md` 是 always-on，子目录文件被转成路径 glob 规则，并在 Cascade 读写对应目录时进入 Context。

[^windsurf-memory]: Windsurf / Devin Desktop. [*Memories & Rules*](https://docs.windsurf.com/windsurf/cascade/memories), accessed 2026-08-27. Cascade 会自动生成 workspace-scoped Memories，也允许用户要求创建；它会在认为相关时自动召回，本地副本位于 `~/.codeium/windsurf/memories/`。官方未公开召回算法、API role 与 Compaction 行为。

[^zep-memory-service]: Zep. [*Architecture patterns*](https://help.getzep.com/architecture-patterns)；[*Adding context*](https://help.getzep.com/adding-context)；[*Searching the graph*](https://help.getzep.com/searching-the-graph)；[*Share context across users using graphs*](https://help.getzep.com/how-to-share-context-across-users-using-graphs). Zep 以 User Graph 或 standalone graph 组织远程 Memory，摄取对话、文本、JSON 和文档，并结合向量、全文与图检索生成 Context Block。

