# Code Agent 的 Context：第一至三章资料

> 本文件收录第一章“术语解释与阅读约定”、第二章“不带 Tool Call 的模型 API”和第三章“加入 Tool Call 后的 Agent”。为保证可独立阅读，相关引用资料一并收录在文末。

## 快速索引

- [第一章：术语解释与阅读约定](#一术语解释与阅读约定)
- [第二章：不带-tool-call-的模型-api](#二不带-tool-call-的模型-api)
- [第三章：加入-tool-call-后的-agent](#三加入-tool-call-后的-agent)
- [引用资料](#引用资料)

---

## 一、术语解释与阅读约定

1. 基础软件术语：本文默认 PyCon 听众知道 Python 和 Git；AI 是 Artificial Intelligence（人工智能）；API 是 Application Programming Interface（程序之间的调用接口）；HTTP 是 Web 请求/响应协议；JSON 是结构化数据文本格式；URL 是资源地址；HTML 与 XML 是使用标签表达结构的标记语言；CLI 与 UI 分别是命令行界面和用户界面；ID 是用于关联对象的标识符；KB 在本文表示约 1,024 字节。
2. Model / LLM：本文的“模型”主要指 Large Language Model（大语言模型）；它接收 token 序列并自回归生成后续 token。
3. Token / Tokenizer：token 是模型处理文本的离散单位；tokenizer 负责在文本与 token IDs 之间转换，tokenization 指这个转换过程。
4. Prompt / Instructions / Messages：prompt 泛指送入模型的输入；instructions 是其中用于约束行为的指令；messages 是 Chat API 用 role 和 content 表达输入的外部协议结构。system、developer、user、assistant 和 tool 是本文会用到的角色或消息类型。
5. Context / Context Window：context 是某次模型调用实际可见的完整 token 序列；context window 是该模型单次能够处理的 token 容量上限。第四章会进一步区分 Context、History、State 和 Artifact；第七章再辨析 Knowledge 与 Memory。
6. History / State：History 是运行过程中已经发生的消息和事件记录；State 是宿主持有的全部任务、文件、进程和外部状态。本文默认完整 History 只追加、不就地改写，即 append-only。
7. Tool / Tool Call / Tool Result：Tool 是 Runtime 可以执行的外部能力；Tool Call 是模型提出的调用请求；Tool Result 是 Runtime 执行后返回的结果。Tool definitions 是模型本轮可见的工具名称、描述和参数协议。
8. Agent / Agent Runtime / Agent Loop：Agent 是“模型 + 外部执行闭环”形成的任务执行体；Runtime 是保存状态、调用模型和执行工具的宿主程序；Agent Loop 是“模型提出动作—Runtime 执行—结果返回模型”的循环。
9. Trajectory / Observation：trajectory 是一次任务中按顺序形成的 user message、模型输出、Tool Call 和 Tool Result 等事件序列；observation 是模型从 Tool Result 或外部环境获得的新信息。
10. Schema / JSON Schema：schema 是结构约束；本文的 Tool parameters 通常使用 JSON Schema 说明字段、类型、必填项和嵌套关系。
11. Knowledge / Memory / Artifact：Knowledge 是在一次会话中基本稳定、可被当前或未来任务复用的外部知识，例如项目规则和架构约定；Memory 是随任务推进频繁变化、用于说明当前经历与状态的信息，例如刚做过什么、当前进度和下一步；Artifact 是独立于当前会话 Context 保存、可通过路径或对象 ID 重新读取的数据文件或对象。Knowledge、Memory、日志、测试报告和 patch 都可以使用 Artifact 作为持久化载体。
12. Chat Template / Renderer / Tool Parser：Chat Template 是把结构化 messages、tools 等输入渲染成模型训练时使用的文本和控制标记的规则；renderer 是执行这类输入协议转换的组件；Tool Parser 是在输出侧识别模型生成的调用语法，并把它转换成结构化 Tool Calls 的服务组件。
13. Prefill / Decode：prefill 是模型处理已有输入 token 并建立推理状态的阶段；decode 是模型基于已有状态逐 token 生成输出的阶段。
14. KV Cache / Prompt or Prefix Cache：KV cache 保存 attention 中已处理 token 的 key/value 状态；跨请求的 prompt/prefix cache 通过匹配相同 token 前缀复用这些计算。cache hit 表示命中可复用前缀，cache miss 表示必须重新计算。
15. Compaction / Context Epoch / Checkpoint：compaction 是从长 History 集中构造较短后续 Context 的过程；两次 compaction 之间连续增长的一段 Context 称为一个 context epoch；checkpoint 或 continuation state 是新 epoch 继续任务所需的目标、约束、进度和证据指针。
16. Retrieval / RAG / JIT Retrieval：retrieval 是从 Context 外查找候选信息；RAG 是 Retrieval-Augmented Generation（检索增强生成）；JIT retrieval 是 Just-in-Time Retrieval（即时检索），即根据当前任务在需要时取回信息，而不是预先全量注入。
17. Embedding / Reranker：embedding 把文本或代码映射为用于相似度搜索的向量；reranker 对初步召回的有限候选重新计算相关性并排序。
18. SFT / RLHF / RLAIF：SFT 是 Supervised Fine-Tuning（监督微调）；RLHF 是 Reinforcement Learning from Human Feedback（基于人类反馈的强化学习）；RLAIF 是 Reinforcement Learning from AI Feedback（基于 AI 反馈的强化学习）。
19. Sandbox / Permission / Approval：sandbox 是限制代码和工具可访问资源的执行隔离环境；permission 是允许的能力边界；approval 是在敏感操作前由用户或策略进行的授权。
20. Cache 生命周期术语：TTL（Time to Live）是缓存有效期；eviction 是缓存淘汰；LRU（Least Recently Used）是优先淘汰最久未使用条目的常见策略；prefix break 是输入在某处发生变化、导致该位置之后的旧 KV 无法继续复用。
21. Model-visible / Projection：model-visible 表示“本轮实际对模型可见”；projection（派生视图）表示 Runtime 从完整 History、Memory 和外部状态中选出并组织成本轮 Context 的结果，并不修改原始记录。
22. 本文保留英文术语，是为了对应 API 字段、代码标识、论文或业界常用名称；其余专门概念会在首次出现处解释，不要求听众预先掌握。
23. Transformer / Attention / CPU / GPU：Transformer 是通过多层 attention 处理 token 序列的模型架构；attention（注意力）让每个 token 按权重读取其他可见 token 的信息；CPU 是通用中央处理器；GPU 是 Graphics Processing Unit（图形处理器），适合并行执行模型中的大量矩阵计算。
24. Session / Node / Scope：Session 是一次连续任务或会话的运行边界；Node 是运行 Agent 或工具的某台机器或执行节点；scope 是数据、Memory 或能力允许被哪些用户、项目或 Agent 发现和访问的逻辑范围。

## 二、不带 Tool Call 的模型 API

### 1. Chat Completions 的外部 API 协议

1. 这里的“传统 OpenAI API”指 `POST /v1/chat/completions`：
   - 它以 `messages` 表达多轮对话；
   - 它不是更早期只接收单段 prompt 的 Completions API；
   - 它也不是后来以带类型的输入/输出项（typed items）和 response ID 为核心的 Responses API。
2. 一个不带 Tool Call 的非流式请求：

```http
POST /v1/chat/completions
Authorization: Bearer $OPENAI_API_KEY
Content-Type: application/json
```

```json
{
  "model": "<chat-model>",
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的数学助手。请给出精确结果。"
    },
    {
      "role": "user",
      "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。"
    }
  ]
}
```

3. 请求字段：
   - `model` 选择负责推理的模型；
   - `messages` 是本次请求提供的有序上下文，不是几次彼此独立的调用；
   - 单条 message 至少表达 `role` 和 `content`；
   - `system` 或 `developer` 表达上层指令，`user` 表达用户输入，`assistant` 表达此前模型输出；
   - `content` 可以是字符串，也可能是由文本、图片、音频等组成的内容块（content blocks），具体能力取决于 API 和模型；
   - temperature 和 top-p 调节采样随机性与候选 token 范围，输出长度字段限制生成规模；这些控制字段不等于普通对话文本。
4. 一个对应的非流式返回。以下 ID、时间和 token 数量均为结构示意：

```json
{
  "id": "chatcmpl_...",
  "object": "chat.completion",
  "created": 1787000000,
  "model": "<chat-model>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "满足条件的整数共有 1663 个，总和为 8,318,317。"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 12,
    "total_tokens": 40
  }
}
```

5. 这个返回是代表性样本，不表示无工具模型每次都能算对：
   - 模型可以在内部形成容斥、等差数列或逐项判断等推理表示；
   - 推理过程和最终数字仍由 next-token generation 产生；
   - 相同问题可能因模型、采样和推理路径不同而得到不同结果；
   - API response 只给出模型生成的答案，没有独立执行记录证明数字正确。
6. 返回字段：
   - `choices` 保存候选输出，通常只请求一个并读取 `choices[0]`；
   - `choices[0].message` 是可以追加到下一轮历史中的 assistant message；
   - `finish_reason` 表示正常停止、达到长度上限或进入其他协议分支；
   - `usage` 记录计费和观测所需的输入、输出及总 token；
   - `id`、`created`、`usage` 等是 API 服务层的外层封装（envelope），不是模型逐 token 生成的正文。
7. Streaming 表示分块流式返回；每个 delta 只携带本次新增片段，客户端必须累积这些增量事件，才能得到与非流式 message 对应的完整结果。
8. Chat Completions 的 `messages` 与 Responses API 的 `input/output items` 在概念上都承载会话事件，但外部协议字段不能直接混用。

### 2. 从请求 JSON 到模型输入 Token

1. HTTP 和 JSON 是客户端与服务端之间的传输协议，不是 Transformer 直接读取的数据结构。
2. 服务端首先完成鉴权、字段校验、模型选择、限额和安全检查。
3. 与模型输入有关的 messages 会通过该模型对应的 chat template 或内部协议表示进行序列化。
4. 序列化需要表达：
   - system/developer、user、assistant 等角色；
   - 每条消息的内容；
   - 消息开始、结束和边界；
   - 当前应该由 assistant 继续生成的位置。
5. 概念上的中间表示可能类似：

```text
[SYSTEM]
你是一个回答简洁的数学助手。请给出精确结果。
[END]
[USER]
求 1 到 10,000（含）中满足条件的整数数量与总和：
能被 7 或 11 整除，但不能同时被二者整除，并且不能被 5 整除。
[END]
[ASSISTANT]
```

6. 上述标记只是解释用的伪表示，不能当作所有 OpenAI 模型公开、固定的真实 chat template。下面选两个可以检查的实现：`Qwen/Qwen3-Coder-30B-A3B-Instruct` 与 `deepseek-ai/DeepSeek-V3.1` 都公开了 Jinja 模板；Jinja 是 Python 生态中常用的文本模板引擎。[^qwen3coder-template][^deepseek-v31-template]
7. Qwen 模板先取出第一条 system message，再把其余 messages 逐条展开，最后追加 assistant generation prompt，也就是标记“接下来应由 assistant 生成”的序列结尾。下面只保留与这次普通对话有关的分支：

```jinja
{%- if messages[0]["role"] == "system" %}
    {%- set system_message = messages[0]["content"] %}
    {%- set loop_messages = messages[1:] %}
{%- else %}
    {%- set loop_messages = messages %}
{%- endif %}

{%- if system_message is defined %}
    {{- "<|im_start|>system\n" + system_message }}
    {{- '<|im_end|>\n' }}
{%- endif %}

{%- for message in loop_messages %}
    {{- '<|im_start|>' + message.role + '\n'
        + message.content + '<|im_end|>\n' }}
{%- endfor %}

{%- if add_generation_prompt %}
    {{- '<|im_start|>assistant\n' }}
{%- endif %}
```

8. DeepSeek-V3.1 的对应 Jinja 先合并所有 system messages，再按 role 展开其余 messages；下面保留普通 user message 与 non-thinking generation prompt 的路径：

```jinja
{{ bos_token }}{{ ns.system_prompt }}
{%- for message in messages %}
  {%- if message['role'] == 'user' %}
    {%- set ns.is_tool = false -%}
    {%- set ns.is_last_user = true -%}
    {{'<｜User｜>' + message['content']}}
  {%- endif %}
{%- endfor %}
{%- if add_generation_prompt and ns.is_last_user and not ns.is_tool %}
  {{'<｜Assistant｜>'}}
  {{'</think>'}}
{%- endif %}
```

9. 对第 1 节的 system 和 user messages 执行 Qwen 模板，并设置 `add_generation_prompt=True`，实际得到：

```text
<|im_start|>system
你是一个回答简洁的数学助手。请给出精确结果。<|im_end|>
<|im_start|>user
求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。<|im_end|>
<|im_start|>assistant
```

10. DeepSeek-V3.1 的公开模板处理相同 messages 时，使用另一套 role 与 generation control tokens。固定 `thinking=False` 后，真实结果是：

```text
<｜begin▁of▁sentence｜>你是一个回答简洁的数学助手。请给出精确结果。<｜User｜>求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。<｜Assistant｜></think>
```

11. 两份 Jinja 的输入都是结构化 `messages`，输出都是带有模型专用控制标记的字符串；Tokenizer 随后才把整个字符串转换成 token IDs。Qwen 的 `<|im_start|>` / `<|im_end|>`，以及 DeepSeek 的 `<｜User｜>` / `<｜Assistant｜>` 等，都是各自 tokenizer 中的专门 token，不是供模型按普通字符逐字读取的标签。
12. 这两个真实例子只说明各自固定 revision 的公开格式，不能反推闭源 OpenAI 模型使用相同标记。它们也直接证明：表面相同的 messages 可以被不同模型渲染成不同 token 序列。
13. `model`、temperature、request ID 和 HTTP headers 等字段是控制请求执行方式的 API envelope 内容，不应笼统地说成整个请求 JSON 会原样 tokenization。
14. Context window 限制的是最终送入模型的 token 序列，而不是字符数、JSON 字节数或 message 数量。

### 3. 从模型生成到 API 返回

1. Prefill 处理输入 token，建立本次推理所需的内部表示和 KV cache。
2. 模型在输入末尾预测第一个输出 token 的概率分布。
3. Decode 阶段根据采样或解码策略逐 token 自回归生成后续输出。
4. 每个新 token 都成为后续 token 的条件，直到遇到结束 token、停止标记序列（stop sequence）、长度上限或其他终止条件。
5. 模型生成的本质是 output token 序列，而不是包含 `id`、`usage` 和 `choices` 的完整 HTTP JSON。
6. 服务端将输出 token 解码成文本或协议结构，识别停止原因，再包装为 assistant message、finish reason、usage 和其他元数据。
7. 因而完整链条是：

```text
API request
→ chat template / 内部协议
→ input token IDs
→ prefill + decode
→ output token IDs
→ 解码与协议解析
→ API response
```

### 4. API 如何形成对话系统

1. 单次 Chat Completions 调用本身不等于持续对话，也不意味着模型在两个 HTTP 请求之间自动记住状态。
2. 客户端把返回的 assistant message 追加到本地 `messages`，再追加新的 user message，并在下一轮重新提交。
3. 下一轮请求的 messages 可能变成：

```json
[
  {
    "role": "system",
    "content": "你是一个回答简洁的数学助手。请给出精确结果。"
  },
  {
    "role": "user",
    "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。"
  },
  {
    "role": "assistant",
    "content": "满足条件的整数共有 1663 个，总和为 8,318,317。"
  },
  {
    "role": "user",
    "content": "请解释你是怎样计算的。"
  }
]
```

4. Responses、Threads 或其他服务端状态 API 可以通过 conversation、thread、previous response 等标识引用历史，但这改变的是状态传输和存储方式，不改变模型每次只处理本轮构造 context 的事实。
5. 客户端为了形成连续对话，至少需要保存完整 history，或者保存足以让服务端恢复 history 的会话标识。
6. Chat UI、客服、问答、写作助手等系统还要在模型 API 外增加：
   - 会话存储；
   - 用户身份与权限；
   - 业务数据；
   - 内容审核；
   - 重试和错误处理；
   - 前端交互。
7. 多轮对话使 message history 持续增长，并产生最初的 context 管理问题。

## 三、加入 Tool Call 后的 Agent

### 1. Tools 如何提供给模型

1. 客户端在请求中同时提交 messages 和 `tools`。沿用 1.1 的同一组 instructions 和用户问题，只增加 `tools` 与 `tool_choice`：

```json
{
  "model": "<chat-model>",
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的数学助手。请给出精确结果。"
    },
    {
      "role": "user",
      "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "run_python",
        "description": "在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "需要执行的 Python 3 程序"
            }
          },
          "required": ["code"],
          "additionalProperties": false
        },
        "strict": true
      }
    }
  ],
  "tool_choice": "auto"
}
```

2. Function tool definition 通常包括：
   - `name`：稳定、可分派的工具名；
   - `description`：工具用途、适用条件和重要语义；
   - `parameters`：参数的 JSON Schema；
   - `strict`：是否要求结构严格符合 schema；
   - API 或供应商定义的其他控制字段。
3. 上述具体定义中：
   - 外层 `type: function` 声明这是由客户端实现的函数工具；
   - `name: run_python` 是模型返回调用请求时使用的协议名称，也应映射到客户端 Tool Registry（保存工具定义并把工具名映射到执行实现的注册表）中的执行入口；
   - `description` 告诉模型该工具能执行 Python，并明确返回 exit code、标准输出和标准错误；
   - `parameters` 告诉模型必须提供字符串字段 `code`；
   - `required: ["code"]` 表示程序文本不能省略；
   - `additionalProperties: false` 禁止 schema 之外的字段；
   - `strict: true` 要求生成的调用参数严格符合受支持的 schema。
4. Tool definition 描述的是模型可以请求的能力，不包含执行器实现；模型不知道宿主如何创建进程、限制资源或捕获输出。
5. `tool_choice: auto` 允许模型在普通回答和调用工具之间选择。也可以禁止调用、要求至少调用一个工具或强制指定工具，具体写法取决于 API。
6. 对这次请求，一个代表性的模型输出不再是直接给出数字，而是生成程序并请求执行：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_001",
      "type": "function",
      "function": {
        "name": "run_python",
        "arguments": "{\"code\":\"values = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(values))\\nprint(sum(values))\"}"
      }
    }
  ]
}
```

7. 同一个用户问题因此形成对照：

```text
不提供 tools
→ 模型在内部完成题意理解、推理和算术
→ 直接生成数量与总和，可能正确，也可能因重叠项或算术出错

提供 run_python
→ 模型仍以概率方式理解题目并生成程序
→ 返回 assistant.tool_calls，请求客户端执行程序
→ Python 对给定程序进行确定性执行，并返回可观察结果
```

8. 这个对照表示可用动作空间发生了变化，不表示 `tool_choice: auto` 能保证每次都调用工具；模型仍可能选择直接回答。需要强制调用时应使用相应的 `tool_choice` 设置。
9. “Python 确定性执行”不等于“Agent 确定性正确”：模型仍可能误解异或条件、写错边界或生成逻辑错误；工具消除的是心算和长算术误差，并提供可复现证据。
10. Schema 能约束字段、类型、枚举和嵌套结构，但不能保证程序语义、算法和安全性正确。
11. 工具名称、描述和 schema 会以模型训练过的内部语法编入模型输入，因此占用 context token；工具越多、描述越长，固定输入成本越大。
12. Tool definition、Tool Call 和 Tool Result 是三个不同对象：
   - definition 由客户端提供，说明可以调用什么；
   - call 由模型请求，说明希望调用什么及其参数；
   - result 由客户端执行后提供，说明外部世界返回了什么。
13. Model Context Protocol（MCP）标准化工具发现、参数协议和远程连接；它不替代模型的 Tool Call 能力，也不自动决定或执行模型下一步推理。

### 2. 模型如何学会 Tool Call 与多步工具使用

1. Tool Call 在模型侧仍然是条件生成问题：给定 instructions、messages、tools 和已有 observations（Tool Result 等外部反馈），预测下一段应该是普通 assistant 内容还是某种工具调用结构。
2. 预训练提供基础能力：
   - 理解自然语言目标；
   - 阅读工具描述和 JSON Schema；
   - 生成代码和结构化数据；
   - 根据上下文模仿“请求—响应”模式。
3. 从生成机制看，模型不是切换到一个独立的“代码模块”或“调用模块”，而是在继续书写一份必须精确符合语法和协议的文档：自然语言、代码与 Tool Call 结构最终都由 token 生成。若 Tool Call 的参数本身就是准备写入文件或交给执行器的代码，那么模型把代码写进这份调用文档，本身就是 Agent 的自动代码编写。
4. 仅有预训练通常不足以稳定遵守某家 API 的专用角色、控制 token、工具名和参数协议，需要后训练重塑输出分布。
5. SFT 数据可以包含以下监督轨迹：
   - 不需要工具时直接输出 assistant answer；
   - 需要外部信息时输出正确 tool name 和 arguments；
   - 读取 tool result 后生成最终回答；
   - 参数缺失时先向用户澄清；
   - 工具报错后修正参数、换工具或停止；
   - 多个工具按依赖关系连续调用；
   - 相互独立的工具并行调用。
6. SFT 使用 next-token cross-entropy（逐位置比较“正确下一个 token”与模型概率分布的训练损失）提高示范输出的概率：
   - 在适合直接回答的状态，提高普通文本 token 的概率；
   - 在需要行动的状态，提高 Tool Call 控制结构、工具名和合法参数 token 的概率；
   - 在出现 observation 后，提高正确解读结果并选择下一步的概率。
7. 多步 SFT 样本不是只教一个固定总计划，而是提供完整 trajectory：

```text
用户目标
→ tool call 1
→ observation 1
→ tool call 2
→ observation 2
→ final answer
```

8. 由此学到的是一个反复执行的策略：模型根据当前可见状态选择下一动作，客户端执行后把新 observation 放回 context，模型再重新规划。
9. 多次 Tool Call 的“规划”可以有不同形态：
   - 一次先形成显式计划，再逐项执行；
   - 不输出完整计划，只根据每次 observation 滚动决定下一步；
   - 对互不依赖的调用一次输出多个 parallel tool calls；
   - 对存在数据依赖的调用等待前一个结果后再生成下一个调用。
10. 偏好优化、RLHF 或 RLAIF 可以比较多种回答或轨迹，奖励更有帮助、更安全、更符合用户意图的行为，但不能把所有 Tool Call 能力简单归因于 RLHF。
11. 反馈和奖励覆盖的对象很重要：如果只评价最终文本，模型未必学到正确的中间调用；要优化工具策略，需要评价 Tool Call、完整 trajectory 或环境中的最终任务结果。
12. 面向工具使用的强化学习还可以采用自动或可验证奖励：
    - 调用结构是否可解析并符合 schema；
    - 工具选择和参数是否正确；
    - 代码是否通过测试、搜索是否找到目标、任务是否最终完成；
    - 是否减少无意义调用、重复调用和过长轨迹；
    - 是否遵守权限、安全和停止条件。
13. 与模仿给定轨迹的 SFT 不同，Agentic RL（在工具环境中执行 Agent 任务的强化学习）可以让模型探索多条 trajectory，再依据任务结果强化工具选择、调用顺序、错误恢复和停止策略。
14. 多步强化学习需要在模拟器、sandbox 或真实可控环境中执行 trajectory，并把最终任务结果的奖励分配给之前的工具选择；探索成本、稀疏奖励、环境不稳定、模型钻奖励规则漏洞（reward hacking），以及判断最终奖励应归因于哪些早期动作（credit assignment），都是难点。
15. 推理时的 structured decoding（结构约束解码）、grammar（形式文法约束）或 strict schema 可以提高语法合法率，但不能代替训练，也不能保证工具选择、参数含义和完整计划正确。
16. 模型只生成 Tool Call 请求。真正的执行、权限、错误处理和持久状态始终属于模型外的 Agent runtime。
17. OpenAI 等闭源供应商通常不会公开完整训练语料、SFT 配比、奖励函数和 RL 流程；上述内容应表述为主流通用机制，而不是某一具体模型的已披露内部配方。

### 3. 一次完整的 Tool Call 协议与客户端循环

1. 完整流程包含两次或更多模型请求，而不是一次 API 调用：

```text
客户端 --请求 1: messages + tools--> 模型 API
客户端 <--返回 1: assistant.tool_calls-- 模型 API
客户端 --在本地解析、授权并执行工具
客户端 --请求 2: 从 history 构造的 context + 新 tool result--> 模型 API
客户端 <--返回 2: assistant answer 或更多 tool calls-- 模型 API
```

2. 第一次请求复用 2.1 的同一示例。完整请求再次列出，以便后续逐步追加 Tool Call 和 Tool Result：

```json
{
  "model": "<chat-model>",
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的数学助手。请给出精确结果。"
    },
    {
      "role": "user",
      "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "run_python",
        "description": "在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "需要执行的 Python 3 程序"
            }
          },
          "required": ["code"],
          "additionalProperties": false
        },
        "strict": true
      }
    }
  ],
  "tool_choice": "auto"
}
```

3. 第一次返回。以下 ID 为结构示意：

```json
{
  "id": "chatcmpl_...",
  "object": "chat.completion",
  "model": "<chat-model>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_001",
            "type": "function",
            "function": {
              "name": "run_python",
              "arguments": "{\"code\":\"values = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(values))\\nprint(sum(values))\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

4. 第一次返回的含义：
   - 它仍然是一条 assistant message；
   - `content` 可以为空，因为当前输出不是最终自然语言回答；
   - `tool_calls` 可以包含零个、一个或多个调用；
   - `arguments` 在 Chat Completions 中是 JSON 编码字符串，客户端必须解析；
   - `id` 用于把稍后的 Tool Result 与正确调用关联；
   - `finish_reason: tool_calls` 表示这一轮在工具请求处暂停，不表示整个用户任务已经完成。
5. 客户端执行的概念代码：

```python
tool_call = response["choices"][0]["message"]["tool_calls"][0]
tool_name = tool_call["function"]["name"]
arguments = json.loads(tool_call["function"]["arguments"])

validate(arguments, tool_registry[tool_name].schema)
authorize(tool_name, arguments)
result = tool_registry[tool_name].execute(**arguments)
```

6. `run_python` 执行器在 sandbox 中启动 Python，捕获进程退出状态、标准输出和标准错误。成功结果为：

```json
{
  "exit_code": 0,
  "stdout": "1663\n8318317\n",
  "stderr": ""
}
```

7. 所谓“客户端把结果返回给模型”，在无状态 Chat Completions 中实际是发起第二次 HTTP 请求。客户端需要同时保留原历史、模型刚才的 Tool Call 和带有关联 ID 的 Tool Result：

```json
{
  "model": "<chat-model>",
  "messages": [
    {
      "role": "system",
      "content": "你是一个回答简洁的数学助手。请给出精确结果。"
    },
    {
      "role": "user",
      "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "call_001",
          "type": "function",
          "function": {
            "name": "run_python",
            "arguments": "{\"code\":\"values = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(values))\\nprint(sum(values))\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "call_001",
      "content": "{\"exit_code\":0,\"stdout\":\"1663\\n8318317\\n\",\"stderr\":\"\"}"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "run_python",
        "description": "在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr",
        "parameters": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "需要执行的 Python 3 程序"
            }
          },
          "required": ["code"],
          "additionalProperties": false
        },
        "strict": true
      }
    }
  ],
  "tool_choice": "auto"
}
```

8. 第二次仍提供 tools，模型便可以根据 observation 直接回答、修正参数、调用另一个工具或继续同一工具；如果宿主明确不允许继续调用，也可以改变 Tool Choice 或可用工具集合。
9. 最终返回：

```json
{
  "id": "chatcmpl_...",
  "object": "chat.completion",
  "model": "<chat-model>",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "满足条件的整数共有 1663 个，总和为 8,318,317。"
      },
      "finish_reason": "stop"
    }
  ]
}
```

10. 如果最终返回仍然包含 Tool Call，客户端重复“解析—校验—授权—执行—追加结果—再次请求”，直到得到最终回答或触发终止条件。

### 4. Tool 执行失败后的闭环纠错

1. 上述成功路径说明模型可以把数学问题转换成程序、请求执行并读取结果，但真实 Agent 的第一次代码经常无法运行。进一步使用同一道题，假设模型先生成了变量名不一致的程序：

```python
numbers = [
    n
    for n in range(1, 10_001)
    if (n % 7 == 0) != (n % 11 == 0)
    and n % 5 != 0
]
print(len(values))
print(sum(values))
```

2. 第一次失败调用仍是一个合法的 Tool Call；`strict: true` 只保证 arguments 符合 schema，不能发现 Python 程序中的 `NameError`（引用了未定义名称的异常）：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_101",
      "type": "function",
      "function": {
        "name": "run_python",
        "arguments": "{\"code\":\"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(values))\\nprint(sum(values))\"}"
      }
    }
  ]
}
```

3. 客户端执行失败后不擅自修改程序，而是把结构化错误作为与 `call_101` 对应的 Tool Result 追加回 history。返回中的 `Traceback` 是 Python 异常调用栈记录：

```json
{
  "role": "tool",
  "tool_call_id": "call_101",
  "content": "{\"exit_code\":1,\"stdout\":\"\",\"stderr\":\"Traceback (most recent call last):\\n  File \\\"<string>\\\", line 2, in <module>\\nNameError: name 'values' is not defined\"}"
}
```

   上面只是本轮新追加的 Tool Result message，不是一个可单独提交的完整请求。客户端要让模型读取该错误并生成修正动作，需要再次发出完整请求：

```text
POST /v1/chat/completions
{
  model: <chat-model>,
  messages: [
    system(...原 instructions...),
    user(...原数学问题...),
    assistant(tool_call=call_101, arguments=...失败程序...),
    tool(tool_call_id=call_101, exit_code=1, stderr=...NameError...)
  ],
  tools: [...与首次请求相同的 run_python definition...],
  tool_choice: auto
}
```

   这是压缩过的请求结构，`...` 只省略了前文已展示的值；实际 JSON 中仍需提供完整 messages 和 Tool definitions。

4. 下一次模型请求能看到用户目标、失败代码和 traceback。模型可以据此进行局部重新规划（replanning）：
    - 错误类型是 `NameError`，不是数学条件或 Python 环境失败；
    - 列表已经保存为 `numbers`，输出语句却引用了 `values`；
    - 不必推翻枚举算法，只需统一变量名；
    - 修正后必须重新执行，不能把“看起来正确”当作成功。
5. 模型生成新的 Tool Call，而不是覆盖旧调用：

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_102",
      "type": "function",
      "function": {
        "name": "run_python",
        "arguments": "{\"code\":\"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(numbers))\\nprint(sum(numbers))\"}"
      }
    }
  ]
}
```

6. 第二次执行成功，并用新的 call ID 返回结果：

```json
{
  "role": "tool",
  "tool_call_id": "call_102",
  "content": "{\"exit_code\":0,\"stdout\":\"1663\\n8318317\\n\",\"stderr\":\"\"}"
}
```

   这同样只是新追加的 Tool Result message。客户端要让模型读取成功结果并生成最终回答，还要发起第三次完整模型请求：

```text
POST /v1/chat/completions
{
  model: <chat-model>,
  messages: [
    system(...原 instructions...),
    user(...原数学问题...),
    assistant(tool_call=call_101, arguments=...失败程序...),
    tool(tool_call_id=call_101, exit_code=1, stderr=...NameError...),
    assistant(tool_call=call_102, arguments=...修正后程序...),
    tool(tool_call_id=call_102, exit_code=0, stdout="1663\n8318317\n")
  ],
  tools: [...与首次请求相同的 run_python definition...],
  tool_choice: auto
}
```

7. 模型随后生成最终回答。可观察到的完整 trajectory 是：

```text
用户目标
→ 生成计算程序
→ call_101: run_python
→ observation: NameError
→ 保留原算法，修正变量名
→ call_102: run_python
→ observation: exit_code=0, stdout=正确结果
→ final answer
```

8. 这里的“自动规划”不要求模型一开始生成完整且不变的计划，更常见的是闭环规划：根据当前 context 选择下一动作，读取新的 observation，再修正后续动作。
9. 不应声称客户端读取了模型隐藏的 chain of thought（内部逐步推理文本）；外部系统真正能观察和保存的是 Tool Call、Tool Result、可选的计划文本以及最终回答。
10. 失败也是有价值的 observation，但自动纠错没有成功保证：模型可能误读 traceback、引入新错误或无限重试，因此客户端仍需设置步数、时间、费用和失败上限。
11. `exit_code == 0` 只证明程序成功执行，不证明算法符合题意；可靠系统还需要独立实现、断言、性质测试或其他验证器（verifier）检查语义正确性。
12. 失败调用、错误输出、修正调用和成功输出都以新事件追加到 trajectory。这解释了 Agent 越能自主试错，Tool History 越容易快速增长。

### 5. Tool Call 如何进入和离开 Token 序列

1. 服务端不会把整个 HTTP JSON 原样交给模型，而是提取 messages、tools 和与生成有关的控制信息。
2. Tool definitions 会使用模型训练过的专用语法被注入或编入输入；OpenAI 官方文档将其概括为注入 system message，但真实模板和控制 token 可能随模型变化。
3. 第一次请求的概念表示：

```text
[SYSTEM]
你是一个回答简洁的数学助手。请给出精确结果。
[END]
[AVAILABLE_TOOLS]
run_python(code: string, required)
用途：在隔离环境中执行 Python 3 代码，并返回 exit_code、stdout 和 stderr
[END]
[USER]
求 1 到 10,000（含）中满足条件的整数数量与总和：
能被 7 或 11 整除，但不能同时被二者整除，并且不能被 5 整除。
[END]
[ASSISTANT]
```

4. 上述伪表示展示的是当前常见布局，不是 OpenAI API、开源推理服务引擎 vLLM、SGLang 或所有模型公开保证的统一 Token 顺序；`[AVAILABLE_TOOLS]` 也只是教学标记，不是 API 中的真实 message role。
5. Tool definitions 最终放在 system、developer、第一条 user message 还是其他位置，由模型训练时采用的协议、供应商的 renderer 和当前 chat template 共同决定；闭源 API 若未公开真实 template，就不能从外部 JSON 字段顺序推断底层 Token 顺序。
6. vLLM 和 SGLang 接入 Hugging Face 模型与 tokenizer 的通用路径，都把 messages 和 tools 作为独立参数交给 `tokenizer.apply_chat_template(...)`；推理引擎本身不固定 Tools 在序列中的位置，具体由选中的 Jinja template 或模型专用 renderer 渲染。
7. 多数当前主流 tool-use templates 与本例的布局近似：先渲染 system/developer-level instructions 和 Tool definitions，再渲染 user/assistant/tool history。具体模型仍有差异：有的把 Tools 放在用户 system content 之后，有的放在其之前，也有的放入第一条 user block。
8. 不能为了下游优化就由推理引擎随意把 Tools 移到 model-visible trajectory 尾部；模型是按训练时的 template 学会理解工具协议的，改变位置可能降低 Tool Call 的正确率。
9. Tools 通常位于 trajectory 之前，这会让动态 Tool definitions 与 prefix cache 发生冲突；具体机制和权衡放到 Cache 章统一讨论。
10. 经过 tokenizer 后，普通消息、工具名、工具描述、参数 schema、分隔符和特殊控制标记都形成 input tokens，因此 Tool Schema 会消耗 context 和 input token。
11. 模型生成的 Tool Call 在底层仍来自 output tokens，概念上类似：

```text
[TOOL_CALL]
name=run_python
arguments={"code":"values = [...]\nprint(len(values))\nprint(sum(values))"}
[END]
```

12. 服务端识别并解析该协议结构，将工具名和参数包装为 `assistant.tool_calls`；call ID、response ID、usage 和其他 envelope 字段由 API 协议层提供，不能一概说成全部由模型正文生成。
13. 在本例的无状态 Chat Completions 中，第二次 HTTP 请求仍需提供原 system instructions、Tool definitions 和原 user message，然后再追加此前的 assistant Tool Call 与客户端产生的 Tool Result。完整逻辑输入如下；`...` 只是省略本文已经展示的内容，不表示请求中没有这些 Token：

```text
[SYSTEM]
...与第一次请求相同的 system instructions...
[END]
[AVAILABLE_TOOLS]
run_python(code: string, required)
...与第一次请求相同的 description 和参数 schema...
[END]
[USER]
...与第一次请求相同的数学问题...
[END]
[ASSISTANT_TOOL_CALL id=call_001]
run_python({"code":"values = [...]\nprint(len(values))\nprint(sum(values))"})
[END]
[TOOL_RESULT id=call_001]
{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}
[END]
[ASSISTANT]
```

14. `call_001` 在真实模板中是否以何种 token 形式出现属于实现细节；API 层要求客户端可靠保存关联关系。
15. 模型读取 Tool Result 后生成普通文本或下一组 Tool Call，服务端再按对应分支解析和包装。
16. `strict`、grammar 或 constrained decoding 可以限制某段输出的合法结构；具体采用 prompt、控制 token、约束采样还是组合机制，由模型和服务实现决定。
17. 两次模型请求意味着两次独立的推理过程；新 Tool Call 和 Tool Result 必须进入下一次请求的 input，不能在第一次生成过程中动态插入。
18. 失败重试不是向一个仍在运行的模型进程单独发送新片段，而是客户端每获得一个 Tool Result 就把它追加到 history，再发起一次完整模型请求。`call_101` 失败后，用于生成修正动作的第二次请求的逻辑输入是：

```text
[SYSTEM]
...原 system instructions...
[END]
[AVAILABLE_TOOLS]
...原 run_python definition...
[END]
[USER]
...原数学问题...
[END]
[ASSISTANT_TOOL_CALL id=call_101]
run_python({"code":"...print(len(values))..."})
[END]
[TOOL_RESULT id=call_101]
{"exit_code":1,"stderr":"NameError: name 'values' is not defined"}
[END]
[ASSISTANT]
```

   该请求的输出是新的 `call_102`。客户端执行它并获得成功结果后，用于生成最终回答的第三次请求会累计包含两组 Tool Call/Tool Result：

```text
[SYSTEM]
...原 system instructions...
[END]
[AVAILABLE_TOOLS]
...原 run_python definition...
[END]
[USER]
...原数学问题...
[END]
[ASSISTANT_TOOL_CALL id=call_101]
run_python({"code":"...print(len(values))..."})
[END]
[TOOL_RESULT id=call_101]
{"exit_code":1,"stderr":"NameError: name 'values' is not defined"}
[END]
[ASSISTANT_TOOL_CALL id=call_102]
run_python({"code":"...print(len(numbers))..."})
[END]
[TOOL_RESULT id=call_102]
{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}
[END]
[ASSISTANT]
```

19. 失败事件不会从 history 中被就地改掉；正常的 append-only loop 保留失败轨迹，并在后面追加修正调用。这既支持查证和因果理解，也使 history 继续增长。
20. 同一套完整样本在外部与内部的映射是：

```text
messages + tools JSON
→ 内部协议与 input tokens
→ Tool Call output tokens
→ assistant.tool_calls JSON
→ 客户端执行并产生 Tool Result
→ 下一轮内部协议与 input tokens
→ answer 或更多 Tool Call output tokens
```

### 6. 与概念表示对应的两份真实 Jinja 样本

1. 上面的 `[SYSTEM]`、`[AVAILABLE_TOOLS]`、`[TOOL_CALL]` 和 `[TOOL_RESULT]` 保留为概念表示；下面把同一组 `messages + tools` 分别按 Qwen3-Coder 与 DeepSeek-V3.1 的公开协议格式化。两者都采用 Jinja，但并不共享控制 token、Tool description 语法或 Tool Call 语法。[^qwen3coder-template][^deepseek-v31-template]
2. Qwen 原始模板中，决定 Tool definitions、assistant Tool Call 和 Tool Result 位置的关键 Jinja 分支包括：

```jinja
{%- if tools is iterable and tools | length > 0 %}
    {{- "\n\n# Tools\n\nYou have access to the following functions:\n\n" }}
    {{- "<tools>" }}
    {%- for tool in tools %}
        {%- if tool.function is defined %}
            {%- set tool = tool.function %}
        {%- endif %}
        {{- "\n<function>\n<name>" ~ tool.name ~ "</name>" }}
        {# 原模板继续逐项展开 description、parameters 和其他字段 #}
        {{- '\n</function>' }}
    {%- endfor %}
    {{- "\n</tools>" }}
    {{- '\n\nIf you choose to call a function ONLY reply in the following format with NO suffix:\n\n<tool_call>\n...' }}
{%- endif %}
```

```jinja
{%- if message.role == "assistant"
      and message.tool_calls is defined
      and message.tool_calls | length > 0 %}
    {# 原模板把每个调用展开为 <tool_call><function=...>...</function> #}
{%- elif message.role == "tool" %}
    {{- '<|im_start|>user\n' }}
    {{- '<tool_response>\n' }}
    {{- message.content }}
    {{- '\n</tool_response>\n' }}
    {{- '<|im_end|>\n' }}
{%- endif %}
```

3. DeepSeek-V3.1 的模型仓库把协议分成两部分：公开 Jinja 负责 messages、assistant Tool Calls 和 Tool Results；模型说明另行规定把 `{tool_description}` 以 Markdown 拼入 system prompt，并明确该 ToolCall 协议用于 non-thinking 模式。模型仓库中的 Jinja 本身不遍历 API 的 `tools=` 参数。vLLM 与 SGLang 提供的 `tool_chat_template_deepseekv31.jinja` 才把“从 `tools` 生成说明”与官方 message template 合并成一个可直接服务 OpenAI-compatible 请求的模板；本文使用的可见格式与 DeepSeek 官方 ToolCall 说明一致。[^deepseek-v31-template][^deepseek-v31-serving-template]

DeepSeek Jinja 中处理历史 Tool Call 与 Tool Result 的核心分支是：

```jinja
{%- if message['role'] == 'assistant'
      and message['tool_calls'] is defined
      and message['tool_calls'] is not none %}
  {# 展开为 <｜tool▁calls▁begin｜> ... <｜tool▁calls▁end｜> #}
{%- endif %}
{%- if message['role'] == 'tool' %}
  {{- '<｜tool▁output▁begin｜>'
      + message['content']
      + '<｜tool▁output▁end｜>' }}
{%- endif %}
```

4. Qwen 的 `If you choose to call a function ONLY reply ...` 就是固定 revision 的 Jinja 字符串字面量，不是 vLLM 或 SGLang 事后插入；DeepSeek 的 `IMPORTANT: ALWAYS adhere ...` 则来自官方模型说明，并被 vLLM/SGLang 的服务模板写入 system。两者都只规定模型应该怎样书写输出，不负责判定输出类型。底层 Transformer 始终只续写 output token IDs；Jinja 在生成开始前已经执行完毕，不会读取模型输出。
5. Parser 是协议的另一端。Qwen 对应 vLLM 的 `qwen3_xml` 与 SGLang 的 `qwen3_coder`；DeepSeek-V3.1 对应两者的 `deepseek_v31` / `deepseekv31` Parser。Parser 检测各自的开始、结束与分隔标记，再把函数名和 JSON arguments 构造成 API 的结构化 `tool_calls`；它不是模型内部的 typed output，也不是权限检查器。[^qwen3coder-parser][^deepseek-v31-parser]
6. 因而，这里不是“后训练已经知道格式，所以无需 Prompt”与“只靠模板临时教会模型”二选一，而是三层配合：

```text
后训练：让模型学会工具选择和约定语法
Chat Template：在本轮输入中提供当前 Tools，并明确要求输出语法
Tool Parser：按同一语法把生成文本转换成 API 的 content / tool_calls
```

   如果只用裸 Hugging Face `generate()` 再 `decode()`，而不接模型专用 Parser，得到的就是原始字符串，不会天然变成一种 Transformer 内部的“typed Tool Call”。模板本身也不能证明提示语是否逐字出现在训练数据中；能确认的事实只是，它属于模型发布物规定的推理协议。[^hf-tool-template]
7. Qwen 的模型模板直接接收结构化 `messages` 和 `tools`：

```python
rendered = tokenizer.apply_chat_template(
    messages,
    tools=tools,
    tokenize=False,
    add_generation_prompt=True,
)

token_ids = tokenizer.apply_chat_template(
    messages,
    tools=tools,
    tokenize=True,
    add_generation_prompt=True,
)
```

   DeepSeek-V3.1 官方 Jinja 的调用则是先按模型说明把 Tool description 拼进 system content，再格式化 messages；也可以直接使用 vLLM/SGLang 已完成这一步的服务模板：

```python
messages[0]["content"] += "\n\n" + render_deepseek_tool_description(tools)
token_ids = tokenizer.apply_chat_template(
    messages,
    tokenize=True,
    thinking=False,
    add_generation_prompt=True,
)
```

8. 对本节第一次请求执行 Qwen 模板，得到下面的真实 model-visible 字符串。可以直接看到，JSON 中独立的 `tools` 参数被 Jinja 展开成尖括号标签结构；模板自己的英文说明把它称为 XML tags。整个 Tools block 位于 user message 之前：

```text
<|im_start|>system
你是一个回答简洁的数学助手。请给出精确结果。

# Tools

You have access to the following functions:

<tools>
<function>
<name>run_python</name>
<description>在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr</description>
<parameters>
<parameter>
<name>code</name>
<type>string</type>
<description>需要执行的 Python 3 程序</description>

</parameter>
        
<required>["code"]</required>
<additionalProperties>False</additionalProperties>

</parameters>
<strict>True</strict>

</function>
</tools>

If you choose to call a function ONLY reply in the following format with NO suffix:

<tool_call>
<function=example_function_name>
<parameter=example_parameter_1>
value_1
</parameter>
<parameter=example_parameter_2>
This is the value for the second parameter
that can span
multiple lines
</parameter>
</function>
</tool_call>

<IMPORTANT>
Reminder:
- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags
- Required parameters MUST be specified
- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after
- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls
</IMPORTANT><|im_end|>
<|im_start|>user
求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。<|im_end|>
<|im_start|>assistant
```

9. 同一请求按 DeepSeek-V3.1 non-thinking 协议渲染如下。Tool descriptions 同样位于 user trajectory 之前，但使用 Markdown；`<｜begin▁of▁sentence｜>`、`<｜User｜>`、`<｜Assistant｜>` 和 `</think>` 是这套协议的真实控制标记：

```text
<｜begin▁of▁sentence｜>你是一个回答简洁的数学助手。请给出精确结果。

## Tools
You have access to the following tools:

### run_python
Description: 在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr

Parameters: {"type": "object", "properties": {"code": {"type": "string", "description": "需要执行的 Python 3 程序"}}, "required": ["code"], "additionalProperties": false}

IMPORTANT: ALWAYS adhere to this exact format for tool use:
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>tool_call_name<｜tool▁sep｜>tool_call_arguments<｜tool▁call▁end｜>{{additional_tool_calls}}<｜tool▁calls▁end｜>

Where:

- `tool_call_name` must be an exact match to one of the available tools
- `tool_call_arguments` must be valid JSON that strictly follows the tool's Parameters Schema
- For multiple tool calls, chain them directly without separators or spaces
<｜User｜>求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。  <｜Assistant｜>    </think>
```

10. 模型从最后的 assistant marker 后继续生成。符合两套协议的 Tool Call output token 序列，解码后分别是：

Qwen：

```text
<tool_call>
<function=run_python>
<parameter=code>
numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]
print(len(numbers))
print(sum(numbers))
</parameter>
</function>
</tool_call>
```

DeepSeek：

```text
<｜tool▁calls▁begin｜><｜tool▁call▁begin｜>run_python<｜tool▁sep｜>{"code":"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\nprint(len(numbers))\nprint(sum(numbers))"}<｜tool▁call▁end｜><｜tool▁calls▁end｜>
```

11. 使用 OpenAI-compatible 服务时，所配置的 Tool Parser 把模型输出解析成 `assistant.tool_calls`；客户端执行后，再把该 assistant message 和 `role: "tool"` 的结果追加到完整 messages。第二次调用仍传入相同的完整 `messages + tools`，不是只发送 Tool Result。
12. Qwen 的第二次完整渲染会重现第 8 点的全部 system、Tool definitions 和原 user message，然后在共同前缀之后追加以下真实后缀：

```text
<|im_start|>assistant
<tool_call>
<function=run_python>
<parameter=code>
numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]
print(len(numbers))
print(sum(numbers))
</parameter>
</function>
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}
</tool_response>
<|im_end|>
<|im_start|>assistant
```

13. DeepSeek 的第二次完整渲染同样重现第 9 点的共同前缀，后缀则是：

```text
      <｜Assistant｜></think>          <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>run_python<｜tool▁sep｜>{"code":"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\nprint(len(numbers))\nprint(sum(numbers))"}<｜tool▁call▁end｜>    <｜tool▁calls▁end｜><｜end▁of▁sentence｜><｜tool▁output▁begin｜>{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}<｜tool▁output▁end｜>
```

DeepSeek 的 Tool Result 不另起 `<｜User｜>` turn；`<｜tool▁output▁end｜>` 后就是模型继续生成的位置，因此模板不会再补一个 `<｜Assistant｜>`。

14. 失败重试不会切换成另一套格式。若第一次程序错误、第二次修正成功，Qwen 完整请求的共同前缀之后会依次累积下面这些真实模板块；旧错误仍然保留，新的调用和结果继续追加：

```text
<|im_start|>assistant
<tool_call>
<function=run_python>
<parameter=code>
numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]
print(len(values))
print(sum(values))
</parameter>
</function>
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"exit_code":1,"stdout":"","stderr":"NameError: name 'values' is not defined"}
</tool_response>
<|im_end|>
<|im_start|>assistant
<tool_call>
<function=run_python>
<parameter=code>
numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]
print(len(numbers))
print(sum(numbers))
</parameter>
</function>
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}
</tool_response>
<|im_end|>
<|im_start|>assistant
```

15. 同一失败与修正 History 经 DeepSeek 模板得到：

```text
      <｜Assistant｜></think>          <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>run_python<｜tool▁sep｜>{"code":"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\nprint(len(values))\nprint(sum(values))"}<｜tool▁call▁end｜>    <｜tool▁calls▁end｜><｜end▁of▁sentence｜><｜tool▁output▁begin｜>{"exit_code":1,"stdout":"","stderr":"NameError: name 'values' is not defined"}<｜tool▁output▁end｜>          <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>run_python<｜tool▁sep｜>{"code":"numbers = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\nprint(len(numbers))\nprint(sum(numbers))"}<｜tool▁call▁end｜>    <｜tool▁calls▁end｜><｜end▁of▁sentence｜><｜tool▁output▁begin｜>{"exit_code":0,"stdout":"1663\n8318317\n","stderr":""}<｜tool▁output▁end｜>
```

16. 两份事实样本都揭示了外部 API 与模型可见协议的非一一映射：
   - 外部 `tools` 是独立请求字段；Qwen Jinja 直接展开它，DeepSeek 服务层则先把它变成 system 中的 Markdown Tool descriptions；
   - 外部 `assistant.tool_calls` 在 Qwen 中成为 XML-like 文本，在 DeepSeek 中成为一组专用 Tool Call tokens；
   - 外部 `role: "tool"` 在 Qwen 中成为 user block 内的 `<tool_response>`，在 DeepSeek 中成为 `<｜tool▁output▁begin｜>...`；
   - API 的 call ID 都没有出现在这两份渲染文本中，宿主仍须保存它来关联调用与结果；
   - generation cursor 的表示不同：Qwen 在 Tool Result 后追加 assistant marker，DeepSeek 直接从 Tool Output 末尾继续。
17. 两种实现都把 Tool definitions 放在 trajectory 之前；修改工具名、description 或 schema 会从 system block 的对应位置开始改变 token prefix，后续对话即使不变也不能继续命中原来的完整前缀。

### 7. 最小 Agent Runtime

1. 一个能够完成单步或多步 Tool Call 闭环的最小 Agent runtime 只需要三类数据与能力：
   - API client：向模型发送请求并接收 assistant message；
   - 固定工具集：包含发给模型的 Tool definitions，以及客户端可按名称调用的对应实现；
   - `messages`：保存 system/user messages、assistant 文本、Tool Calls 和 Tool Results。
2. 在这个不做 compaction 的最小实现中，同一份 append-only `messages` 可以同时充当完整 history 和下一轮 context 的主要来源；进入一般系统以后，两者才需要明确分离。
3. 最小闭环的控制流可以只是：

```text
用 messages + 固定 Tool definitions 调用模型
→ 把 assistant message 追加到 messages
→ 如果没有 Tool Call，返回最终回答
→ 否则在固定工具集中按名称执行
→ 把 Tool Result 追加到 messages
→ 再次调用模型
```

4. 这个最小定义假设任务较短、工具集不变、进程不会中途崩溃，也不考虑恶意输入和工具副作用。
5. 因此最小系统不需要 compaction、动态 Tool Registry、schema 版本管理、sandbox、权限审批、持久化、artifact store 或完整状态机；这些都是从最小演示走向一般或生产系统时才出现的需求。

## 引用资料

[^deepseek-v31-parser]: SGLang revision [`af39ad93` 的 `DeepSeekV31Detector`](https://github.com/sgl-project/sglang/blob/af39ad93493c3c9ca8cdd50ac42fcce3a4ed7e2b/python/sglang/srt/function_call/deepseekv31_detector.py) 在非流式路径中抽取 Tool Call 标记、函数名与 JSON arguments，流式路径维护 buffer 与增量状态；vLLM revision [`7ca49fbe` 的对应 Parser](https://github.com/vllm-project/vllm/blob/7ca49fbe4bab019e55d57cdc4b7fd3d55c67c1a6/vllm/tool_parsers/deepseekv31_tool_parser.py) 使用同一模型协议。

[^deepseek-v31-serving-template]: DeepSeek-V3.1 的 OpenAI-compatible Tool-aware Jinja 适配：SGLang revision [`af39ad93`](https://github.com/sgl-project/sglang/blob/af39ad93493c3c9ca8cdd50ac42fcce3a4ed7e2b/examples/chat_template/tool_chat_template_deepseekv31.jinja) 与 vLLM revision [`7ca49fbe`](https://github.com/vllm-project/vllm/blob/7ca49fbe4bab019e55d57cdc4b7fd3d55c67c1a6/examples/tool_chat_template_deepseekv31.jinja)。两者把 API `tools` 展开为 DeepSeek 官方说明中的 Markdown，再追加到 system content；SGLang 直接兼容 arguments 为 JSON string 的 History，vLLM 在套模板前将其规范化为对象。

[^deepseek-v31-template]: DeepSeek AI. [`deepseek-ai/DeepSeek-V3.1` 原始 `assets/chat_template.jinja`](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/assets/chat_template.jinja), revision `c0781d039fb7a1ba2abc4add0bdc293e92d2b8db`；同一 revision 的 [ToolCall 说明](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/README.md#toolcall) 规定 `{tool_description}` 的 Markdown 格式和 `<｜tool▁calls▁begin｜>` 协议，[`tokenizer.json`](https://huggingface.co/deepseek-ai/DeepSeek-V3.1/blob/c0781d039fb7a1ba2abc4add0bdc293e92d2b8db/tokenizer.json) 定义本文复现的 control-token IDs。模型 Jinja 本身处理 messages、历史 Tool Calls 和 Tool Results，但不遍历独立的 `tools` 参数。

[^hf-tool-template]: Hugging Face Transformers. [*Writing a chat template: Templates for tools*](https://huggingface.co/docs/transformers/en/chat_templating_writing#templates-for-tools). 文档说明 Tool template 没有统一格式，渲染结果必须匹配模型训练时使用的 whitespace、特殊 token 和布局。

[^qwen3coder-parser]: Qwen Team. [`Qwen3-Coder-30B-A3B-Instruct` 同一固定 revision 附带的 `qwen3coder_tool_parser.py`](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/qwen3coder_tool_parser.py)，其中非流式路径使用正则提取 Tool Call，流式路径维护增量解析状态。vLLM 官方文档在 revision [`185cada3`](https://github.com/vllm-project/vllm/blob/185cada36bb25aa55f762d004d54c5ca1e3fc753/docs/features/tool_calling.md#L431-L440) 将两个 Qwen3-Coder 模型对应到 `--tool-call-parser qwen3_xml`；[`qwen3_coder` 是同一 Parser 的兼容别名](https://github.com/vllm-project/vllm/blob/185cada36bb25aa55f762d004d54c5ca1e3fc753/vllm/tool_parsers/__init__.py#L173-L181)。SGLang revision [`d1af3c89`](https://github.com/sgl-project/sglang/blob/d1af3c89233c475fc1bf11939d86787e6cddd58c/docs/cookbook/autoregressive/Qwen/Qwen3-Coder.mdx#L215-L283) 使用名称 `qwen3_coder`，其 [`Qwen3CoderDetector`](https://github.com/sgl-project/sglang/blob/d1af3c89233c475fc1bf11939d86787e6cddd58c/python/sglang/srt/function_call/qwen3_coder_detector.py#L21-L41) 也把 XML-like 生成文本解析成结构化调用。

[^qwen3coder-template]: Qwen Team. [`Qwen/Qwen3-Coder-30B-A3B-Instruct` 原始 `chat_template.jinja`](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/resolve/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/chat_template.jinja), revision `b2cff646eb4bb1d68355c01b18ae02e7cf42d120`. Hugging Face. [可读源码页面；格式说明位于第 66 行](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/chat_template.jinja#L66)；同 revision 的 [`tokenizer.json`](https://huggingface.co/Qwen/Qwen3-Coder-30B-A3B-Instruct/blob/b2cff646eb4bb1d68355c01b18ae02e7cf42d120/tokenizer.json) 定义本文复现的 control-token IDs。
