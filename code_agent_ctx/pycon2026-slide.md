---
schema: pycon-slide-plan/v1
title: "PyCon 2026：Code Agent 的 Context"
slide_source: talk.qmd
audio_pattern: audio/{id}.mp3
tts_provider: edge-tts
tts_version: 7.2.8
tts_voice: zh-CN-YunyangNeural
tts_rate: "+10%"
tts_pronounce_JSON: Jason
tts_pronounce_Qwen3: 千问3
tts_pronounce_Qwen: 千问
tts_pronounce_run_python: run python
tts_pronounce_ID: I D
tts_pronounce_IDs: I D
llms_url: https://shell909090.github.io/slides/code_agent_ctx/llms.txt
status: draft
---

# 页面底稿

本文件是演示页面与 TTS 的唯一内容中间层。每页必须包含稳定 ID、主旨、展示内容和演讲词。`展示内容（QMD）` 生成 `talk.qmd` 的可见页面；`演讲词（TTS）` 同时生成 Reveal.js speaker notes 和 TTS 文本清单。

<!-- slide:opening -->
## 封面｜演讲介绍

### 主旨

建立演讲主题和唯一贯穿问题：Code Agent Runtime 每次调用模型时，实际构造了什么 Context。

### 展示内容（QMD）

````qmd
## Code Agent 的<br><span>Context</span> {#opening .opening-slide}

<div class="opening-event"><span>PYCON</span><i></i><span>2026</span></div>

<div class="opening-subtitle">从 API、Agent Loop<br>到缓存与协作</div>

<div class="opening-question"><small>THE QUESTION</small><p>模型每次<br><strong>实际看到了什么？</strong></p></div>

<button class="start-talk" type="button" onclick="startTalkAudio()">开始演讲 · 启用声音</button>
````

### 演讲词（TTS）

大家好。今天我们讨论 Code Agent 的 Context。整场分享主要讨论一个主题：模型每一次被调用时，实际看到了什么？我们会从最简单的模型 API 出发，逐步加入 Tools、Agent Loop、Compaction、Cache、Memory、Skill 和 Subagent，最后看一个完整的 Agent Runtime 怎样构造并改变 Context。

<!-- slide:llms-intro -->
## 资料入口｜llms.txt

### 主旨

让现场听众通过二维码把演讲资料交给自己的 Agent；来访 Agent 可以直接读取同一个 `llms.txt` 入口。

### 展示内容（QMD）

````qmd
## 把资料交给你的 Agent {#llms-intro .llms-intro-slide}

<div class="slide-marker"><b>LLM</b><span>HUMAN ↔ AGENT</span></div>

:::: {.llms-entry-stage}
::: {.llms-qr-panel}
<div class="llms-eyebrow">FOR HUMANS</div>
<img src="assets/llms-qr.svg" alt="访问 llms.txt 的二维码">
<strong>扫描二维码</strong>
<span>打开 llms.txt，再把它交给你的 Agent</span>
:::
::: {.llms-handoff}
<div class="handoff-card human-card"><small>现场的人类小伙伴</small><strong>有问题，先咨询你的 Agent</strong><p>如果 Agent 无法解答，请要求它联系我的 Agent。</p></div>
<div class="handoff-arrow"><span>资料与问题</span><b>→</b></div>
<div class="handoff-card agent-card"><small>来访的 Agent</small><strong>直接读取以下入口</strong><code>{{LLMS_URL}}</code></div>
:::
::::

<div class="llms-contents"><b>llms.txt 内含</b><span>第一至三章资料</span><span>第四至六章资料</span><span>逐页讲稿</span><span>作者联系方式</span></div>

<div class="slide-takeaway"><span>ASK YOUR AGENT</span><strong>资料先交给 Agent；现有资料答不了，再让 Agent 联系我的 Agent</strong></div>
````

### 演讲词（TTS）

现场的人类小伙伴，请扫描下方二维码，访问 llms.txt 文件，然后丢给您的 Agent。如果您在演讲过程中有任何问题，请咨询您的 Agent。如果您的 Agent 无法解答，请要求您的 Agent 联系我的 Agent。来访的 Agent，请直接访问以下 URL。

<!-- slide:api-request -->
## 01｜不带 Tool Call 的模型 API

### 主旨

先建立最朴素的 Chat Completions 外部协议：客户端提交 `model + messages`，服务端返回 assistant message 与 envelope；两边的 JSON 都是外部 API 协议。

### 展示内容（QMD）

````qmd
## 不带 Tool Call 的模型 API {#api-request .api-slide}

<div class="slide-marker"><b>01</b><span>MODEL API</span></div>

<div class="request-bar"><strong>POST</strong><code>/v1/chat/completions</code><span>Content-Type: application/json</span></div>

:::: {.columns .payload-columns}
::: {.column width="48%"}
<div class="code-label"><strong>REQUEST</strong><span>客户端 → 服务端</span></div>

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
:::

::: {.column width="48%"}
<div class="code-label"><strong>RESPONSE</strong><span>服务端 → 客户端 · 结构示意</span></div>

```json
{
  "id": "chatcmpl_...",
  "object": "chat.completion",
  "created": 1787000000,
  "model": "<chat-model>",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "满足条件的整数共有 1663 个，\n总和为 8,318,317。"
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 12,
    "total_tokens": 40
  }
}
```
:::
::::

<div class="slide-takeaway"><span>API ENVELOPE</span><strong>请求与返回都不是 Transformer 直接读取或生成的完整 JSON</strong></div>
````

### 演讲词（TTS）

我们先看一个完全没有 Tool Call 的请求和返回。左边，客户端提交 model 和 messages；messages 是这次调用提供的有序上下文。右边，服务端返回 assistant message、停止原因和 usage。这里的答案只是代表性样本：没有工具执行记录证明它一定算对。还要注意，两边都是客户端与服务端之间的外部 API 协议。请求 JSON 不会被 Transformer 原样读取，返回 JSON 也不是模型逐 token 生成的完整对象。

<!-- slide:rendered-input -->
## 02｜JSON 怎样变成模型输入

### 主旨

结构化 `messages` 要先经 Chat Template 或 Renderer 变成模型专用字符串。概念表示负责解释；Qwen3-Coder 与 DeepSeek-V3.1 的公开 Jinja 证明同一组 messages 可以形成不同的模型输入。

### 展示内容（QMD）

````qmd
## JSON 怎样变成模型输入 {#rendered-input .render-slide}

<div class="slide-marker"><b>02</b><span>RENDERER</span></div>

<div class="protocol-note">同一组 messages · 三种表示并列 · DeepSeek 控制 token 前换行仅用于展示</div>

:::: {.protocol-grid .render-compare-grid}
::: {.protocol-panel .concept-protocol}
<div class="protocol-label"><strong>概念中间表示</strong><span>教学用伪表示</span></div>

```text
[SYSTEM]
你是一个回答简洁的数学助手。
请给出精确结果。
[END]
[USER]
求 1 到 10,000（含）中满足条件的整数数量与总和：
能被 7 或 11 整除，但不能同时被二者整除，
并且不能被 5 整除。
[END]
[ASSISTANT]
```
:::

::: {.protocol-panel .qwen-protocol}
<div class="protocol-label"><strong>Qwen3-Coder</strong><span>固定 revision</span></div>

```text
<|im_start|>system
你是一个回答简洁的数学助手。请给出精确结果。<|im_end|>
<|im_start|>user
求 1 到 10,000（含）中满足以下条件的所有整数的
数量与总和：能被 7 或 11 整除，但不能同时被 7
和 11 整除，并且不能被 5 整除。<|im_end|>
<|im_start|>assistant
```
:::

::: {.protocol-panel .deepseek-protocol}
<div class="protocol-label"><strong>DeepSeek-V3.1</strong><span>non-thinking · 展示分行</span></div>

```text
<｜begin▁of▁sentence｜>
你是一个回答简洁的数学助手。请给出精确结果。
<｜User｜>
求 1 到 10,000（含）中满足以下条件的所有整数的
数量与总和：能被 7 或 11 整除，但不能同时被 7
和 11 整除，并且不能被 5 整除。
<｜Assistant｜>
</think>
```
:::
::::

<div class="render-bridge"><span>同一组 messages</span><b>→</b><span>不同模型专用字符串</span><b>→</b><strong>token IDs</strong></div>
````

### 演讲词（TTS）

API 收到结构化载荷以后，并不会把整段 JSON 原样交给 Transformer。左栏是教学用的概念表示，只用来说明角色、正文、消息边界，以及接下来由 assistant 生成的位置，它不是任何模型的统一标准。中间和右栏来自公开模板：同一组 messages，在固定版本的 Qwen3-Coder 中会变成 im-start 和 im-end 标记；在关闭思考模式的 DeepSeek V3.1 中，则会变成另一套 User、Assistant 和 generation control tokens。随后 Tokenizer 才把整个字符串转换成 token IDs。重点是：输入相同，模板不同，模型最终看到的 token 序列也不同；这两个例子也不能反推出闭源模型的内部格式。

<!-- slide:model-call-flow -->
## 03｜一次模型调用的总体流程

### 主旨

把传输协议、输入渲染、模型推理和响应封装连成一条完整链路，并明确 API JSON 与模型处理的 token 序列不是一回事。

### 展示内容（QMD）

````qmd
## 一次模型调用的总体流程 {#model-call-flow .flow-slide}

<div class="slide-marker"><b>03</b><span>FULL PATH</span></div>

<div class="sequence-stage"><div class="participant client"><b>用户 / 客户端</b><span>HTTP 与状态</span></div><div class="participant service"><b>API Service</b><span>校验与封装</span></div><div class="participant renderer"><b>Renderer / Parser</b><span>Template · Tokenizer</span></div><div class="participant model"><b>MODEL</b><span>prefill · decode</span></div><div class="seq-message m1"><span>request JSON</span></div><div class="seq-message m2"><span>messages</span></div><div class="seq-message m3"><span>input token IDs</span></div><div class="seq-message reverse m4"><span>output token IDs</span></div><div class="seq-message reverse m5"><span>assistant / finish reason</span></div><div class="seq-message reverse m6"><span>response JSON</span></div></div>

<div class="flow-conclusion">模型处理和生成的是 <strong>token 序列</strong>，不是完整 HTTP JSON</div>
````

### 演讲词（TTS）

现在用一张折返式序列图把调用串起来。用户和客户端在最左边，模型在最右边。请求向右走：API Service 完成校验和模型选择，Renderer 把 messages 序列化，Tokenizer 产生 input token IDs。模型完成 prefill 和逐 token decode。返回再向左走：output token IDs 被解码和解析，服务端包装 assistant message、停止原因和 usage，最后把 response JSON 交回客户端。所以模型真正处理和生成的是 token 序列，而不是完整的 HTTP JSON。

<!-- slide:second-request -->
## 04｜第二次请求：History 开始增长

### 主旨

Chat Completions 单次调用本身无状态。连续对话来自客户端把上一轮 assistant message 和新 user message 追加后，在第二次请求中重新提交完整 `messages`。

### 展示内容（QMD）

````qmd
## 第二次请求：History 开始增长 {#second-request .second-request-slide}

<div class="slide-marker"><b>04</b><span>NEXT TURN</span></div>

<div class="request-bar"><strong>POST</strong><code>/v1/chat/completions</code><span>第二次完整请求</span></div>

```json
{
  "model": "<chat-model>",
  "messages": [
    { "role": "system",    "content": "你是一个回答简洁的数学助手。请给出精确结果。" },
    { "role": "user",      "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。" },
    { "role": "assistant", "content": "满足条件的整数共有 1663 个，总和为 8,318,317。" },
    { "role": "user",      "content": "请解释你是怎样计算的。" }
  ]
}
```

<div class="slide-takeaway"><span>NEXT TURN</span><strong>第二次请求 = 旧 messages + assistant 返回 + 新 user message</strong></div>
````

### 演讲词（TTS）

第一次调用结束后，模型并不会在服务器里自动记住刚才的对话。客户端要从返回载荷中取出 assistant message，追加到本地 messages，再追加用户的新问题。于是第二次请求不是只发送“请解释”，而是重新提交 system、第一次 user、第一次 assistant，以及第二次 user。这里第一次看到了 History 的增长：外部看起来是一场连续对话，模型看到的却始终是当前这一次请求重新构造出的完整 Context。后面 Code Agent 的 Tool Call、Tool Result 和 Compaction，都会沿着这个基本模式继续展开。

<!-- slide:tool-call-request -->
## 05｜加入 Tool Call：请求载荷

### 主旨

沿用相同的 system/user messages，客户端增加 `tools` 和 `tool_choice`，把可请求的外部能力与参数 Schema 暴露给模型；Tool definition 不包含执行器实现。

### 展示内容（QMD）

````qmd
## 加入 Tool Call：请求载荷 {#tool-call-request .tool-request-slide}

<div class="slide-marker"><b>05</b><span>TOOLS REQUEST</span></div>

<div class="request-bar"><strong>POST</strong><code>/v1/chat/completions</code><span>messages + tools + tool_choice</span></div>

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

<div class="slide-takeaway"><span>TOOL DEFINITION</span><strong>描述模型可以请求的能力，不包含 Python 执行器实现</strong></div>
````

### 演讲词（TTS）

现在沿用刚才完全相同的 system 和 user messages，只在请求里增加 tools 与 tool choice。这里注册了一个 run_python 函数。tool choice 设为 auto，表示模型可以直接回答，也可以请求这个工具。注意，这段 definition 只描述客户端提供的能力，并不包含 Python 执行器本身。模型看不到宿主怎样创建进程、限制权限或捕获输出，更没有在这一刻执行任何程序。

<!-- slide:tool-call-response -->
## 06｜模型返回 Tool Call

### 主旨

第一次 response 返回的不是 Python 结果，而是一条 `assistant.tool_calls` 请求；Runtime 仍需解析参数、检查权限并执行工具。

### 展示内容（QMD）

````qmd
## 模型返回 Tool Call {#tool-call-response .tool-response-slide}

<div class="slide-marker"><b>06</b><span>TOOLS RESPONSE</span></div>

<div class="response-bar"><strong>200</strong><code>assistant.tool_calls</code><span>尚未执行工具</span></div>

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

<div class="slide-takeaway"><span>PAUSED</span><strong>Tool Call 是执行请求；Runtime 解析、授权并执行后才会产生 Tool Result</strong></div>
````

### 演讲词（TTS）

这就是对应的第一次返回。它没有给出数学答案，也没有给出 Python 的执行结果；它仍然是一条 assistant message，只是 content 为空，并通过 tool calls 请求客户端调用 run_python。arguments 在 Chat Completions 协议里是一个经过编码的 JSON 字符串，Runtime 必须先解析它，再根据权限策略决定是否执行。call ID 会在稍后把 Tool Result 关联回这一次调用。finish reason 等于 tool calls，只表示本轮生成在工具请求处暂停，并不表示用户任务已经完成。真正运行程序、捕获标准输出、处理失败并把结果送回模型，都是下一阶段 Runtime 的职责。

<!-- slide:tool-result-request -->
## 07｜带 Tool Result 的第二次请求

### 主旨

客户端执行 Tool Call 后不会回填旧请求，而是把第一次 `assistant.tool_calls` 和对应的 `role: tool` Tool Result 追加到 messages，再携带同一组 tools 发起第二次完整请求。

### 展示内容（QMD）

````qmd
## 带 Tool Result 的第二次请求 {#tool-result-request .tool-result-request-slide}

<div class="slide-marker"><b>07</b><span>SECOND REQUEST</span></div>

<div class="request-bar"><strong>POST</strong><code>/v1/chat/completions</code><span>完整 history + tool result + tools</span></div>

```json
{
  "model": "<chat-model>",
  "messages": [
    { "role": "system", "content": "你是一个回答简洁的数学助手。请给出精确结果。" },
    { "role": "user", "content": "求 1 到 10,000（含）中满足以下条件的所有整数的数量与总和：能被 7 或 11 整除，但不能同时被 7 和 11 整除，并且不能被 5 整除。" },
    {
      "role": "assistant", "content": null,
      "tool_calls": [{
        "id": "call_001", "type": "function",
        "function": {
          "name": "run_python",
          "arguments": "{\"code\":\"values = [n for n in range(1, 10_001) if (n % 7 == 0) != (n % 11 == 0) and n % 5 != 0]\\nprint(len(values))\\nprint(sum(values))\"}"
        }
      }]
    },
    {
      "role": "tool", "tool_call_id": "call_001",
      "content": "{\"exit_code\":0,\"stdout\":\"1663\\n8318317\\n\",\"stderr\":\"\"}"
    }
  ],
  "tools": [{
    "type": "function",
    "function": {
      "name": "run_python",
      "description": "在隔离环境中运行 Python 3 代码，并返回 exit_code、stdout 和 stderr",
      "parameters": {
        "type": "object",
        "properties": { "code": { "type": "string", "description": "需要执行的 Python 3 程序" } },
        "required": ["code"], "additionalProperties": false
      },
      "strict": true
    }
  }],
  "tool_choice": "auto"
}
```

<div class="slide-takeaway"><span>APPEND</span><strong>assistant Tool Call 与对应 Tool Result 必须一起进入下一次请求</strong></div>
````

### 演讲词（TTS）

客户端拿到 Tool Call 后，先解析 arguments，按 Schema 校验参数，再做权限检查，最后才在 Sandbox 中执行 run_python。执行得到 exit code 为零，标准输出包含数量 1663 和总和 8318317。这里最容易误解的一点是：客户端不能把结果塞回已经结束的第一次调用。它必须发起第二次完整 HTTP 请求。新的 messages 依次保留原 system、原 user、第一次 assistant Tool Call，再追加 role 为 tool 的 Tool Result。tool call ID 与 tool message 里的 tool call ID 都是 call 001，因此模型和 Runtime 能可靠关联请求与结果。tools 和 tool choice 仍然提交，因为模型读取 observation 后既可以给出最终答案，也可以继续请求工具。

<!-- slide:tool-loop-flow -->
## 08｜一次完整的 Tool Loop

### 主旨

把两次独立模型调用与中间一次客户端本地执行连成闭环：第一次返回 Tool Call，客户端执行并追加 Tool Result，第二次调用才让模型看到结果并生成最终回答。

### 展示内容（QMD）

````qmd
## 一次完整的 Tool Loop {#tool-loop-flow .tool-loop-slide}

<div class="slide-marker"><b>08</b><span>TOOL LOOP</span></div>

<div class="tool-loop-stage">
  <div class="participant client"><b>客户端 / Runtime</b><span>history · 执行器</span></div>
  <div class="participant service"><b>API Service</b><span>校验与封装</span></div>
  <div class="participant renderer"><b>Renderer / Parser</b><span>Template · Tokenizer</span></div>
  <div class="participant model"><b>MODEL</b><span>两次独立推理</span></div>

  <div class="tl-message right c-s t1"><span>请求 1 · messages + tools</span></div>
  <div class="tl-message right s-r t2"><span>渲染第一次输入</span></div>
  <div class="tl-message right r-m t3"><span>input token IDs</span></div>
  <div class="tl-message left r-m t4"><span>assistant.tool_calls</span></div>
  <div class="tl-message left s-r t5"><span>解析并封装 response 1</span></div>
  <div class="tl-message left c-s t6"><span>返回 1 · Tool Call</span></div>

  <div class="client-execution"><small>CLIENT EXECUTION</small><strong>解析 → 校验 → 授权 → Sandbox 执行</strong><code>Tool Result · call_001</code></div>

  <div class="tl-message right c-s t7"><span>请求 2 · history + Tool Result</span></div>
  <div class="tl-message right s-r t8"><span>渲染第二次完整输入</span></div>
  <div class="tl-message right r-m t9"><span>input token IDs</span></div>
  <div class="tl-message left r-m t10"><span>最终 assistant answer</span></div>
  <div class="tl-message left s-r t11"><span>解析并封装 response 2</span></div>
  <div class="tl-message left c-s t12"><span>返回 2 · finish_reason: stop</span></div>
</div>

<div class="flow-conclusion"><strong>1 次 Tool Loop = 2 次模型推理 + 1 次客户端执行</strong></div>
````

### 演讲词（TTS）

一次 Tool Loop 包含两次模型推理和一次客户端执行。第一次调用返回 Tool Call 后就结束；Runtime 在本地校验并执行工具，把 Tool Call 和 Tool Result 追加到 History，再发起第二次请求。模型此时才看到执行结果并生成最终回答。如果仍然返回 Tool Call，Runtime 就继续循环，直到完成任务或触发终止条件。

<!-- slide:error-context-request -->
## 09｜出错后的最后一次请求

### 主旨

失败事件不会被修正调用覆盖；用于生成最终答案的第三次请求仍携带原目标、失败 Tool Call、完整 traceback、修正 Tool Call 与成功 Tool Result。

### 展示内容（QMD）

````qmd
## 出错后的最后一次请求 {#error-context-request .error-context-slide}

<div class="slide-marker"><b>09</b><span>ERROR IN CONTEXT</span></div>

<div class="request-bar"><strong>POST #3</strong><code>/v1/chat/completions</code><span>用于生成最终回答</span></div>

<div class="context-table">
  <div class="ctx-row ctx-head"><b>#</b><b>ROLE</b><b>关联</b><b>messages 中的关键载荷</b></div>
  <div class="ctx-row compact"><b>1</b><code>system</code><span>—</span><p>原 instructions <small>正文省略；实际请求保留全文</small></p></div>
  <div class="ctx-row compact"><b>2</b><code>user</code><span>—</span><p>原数学问题 <small>正文省略；实际请求保留全文</small></p></div>
  <div class="ctx-row call-row"><b>3</b><code>assistant</code><span>call_101</span><p><strong>run_python</strong><br><code>numbers = […]</code><br><code>print(len(values)) · print(sum(values))</code></p></div>
  <div class="ctx-row error-row"><b>4</b><code>tool</code><span>call_101</span><pre>exit_code: 1 · stdout: ""&#10;stderr:&#10;Traceback (most recent call last):&#10;  File "&lt;string&gt;", line 2, in &lt;module&gt;&#10;NameError: name 'values' is not defined</pre></div>
  <div class="ctx-row call-row repaired"><b>5</b><code>assistant</code><span>call_102</span><p><strong>run_python</strong><br><code>numbers = […]</code><br><code>print(len(numbers)) · print(sum(numbers))</code></p></div>
  <div class="ctx-row success-row"><b>6</b><code>tool</code><span>call_102</span><pre>exit_code: 0 · stderr: ""&#10;stdout: "1663\n8318317\n"</pre></div>
</div>

<div class="request-footer"><span>model: &lt;chat-model&gt;</span><span>tools: 原 run_python definition</span><span>tool_choice: auto</span></div>

<div class="slide-takeaway"><span>APPEND-ONLY</span><strong>修正成功，不等于失败从 Context 中消失</strong></div>
````

### 演讲词（TTS）

再看一次执行出错的情况。第一次 Tool Call 使用 numbers 保存列表，却在输出时引用 values，因此客户端得到 exit code 1 和完整的 Python traceback。模型读取错误后生成新的 call 102，把输出变量修正为 numbers；第二次执行成功。为了让模型生成最终答案，客户端发起第三次完整请求。表格就是其中 messages 的顺序：原 instructions、原数学问题、失败调用、完整错误、修正调用和成功结果，一个都没有被覆盖。这里省略的只是幻灯片上已经明确的长正文，实际请求仍携带完整内容。完整 traceback 是 observation，也是模型判断错误类型和修正位置的依据。append-only 的好处是可追溯，代价则是每次失败都会继续增加 Context。

<!-- slide:tool-request-renderings -->
## 10｜带 Tools 的请求如何变成模型输入

### 主旨

同一份首次 `messages + tools` 请求会被不同模板渲染成不同协议；三栏只折叠长正文与 Schema，保留块顺序、工具位置和 generation cursor。

### 展示内容（QMD）

````qmd
## 带 Tools 的请求如何变成模型输入 {#tool-request-renderings .protocol-slide}

<div class="slide-marker"><b>10</b><span>TOOLS RENDERING</span></div>

<div class="protocol-note">协议节选 · 灰色“内容省略”仍存在于真实输入 · 特殊标记原样保留</div>

:::: {.protocol-grid}
::: {.protocol-panel .concept-protocol}
<div class="protocol-label"><strong>概念表示</strong><span>教学伪表示</span></div>

```text
[SYSTEM]
你是一个回答简洁的数学助手。
[END]

[AVAILABLE_TOOLS]
run_python(code: string, required)
用途：执行 Python 3，返回
exit_code / stdout / stderr
schema: code 为必填 string
[END]

[USER]
〔原数学问题全文〕
[END]
[ASSISTANT]
```
:::

::: {.protocol-panel .qwen-protocol}
<div class="protocol-label"><strong>Qwen3-Coder</strong><span>固定 revision · 协议节选</span></div>

```text
<|im_start|>system
〔原 system 正文〕

# Tools
<tools>
<function>
<name>run_python</name>
<description>执行 Python 3…</description>
<parameters>
〔完整 schema〕
</parameters>
</function>
</tools>
〔Tool Call 输出格式说明〕
<|im_end|>
<|im_start|>user
〔原数学问题全文〕
<|im_end|>
<|im_start|>assistant
```
:::

::: {.protocol-panel .deepseek-protocol}
<div class="protocol-label"><strong>DeepSeek-V3.1</strong><span>non-thinking · 协议节选</span></div>

```text
<｜begin▁of▁sentence｜>
〔原 system 正文〕

## Tools
You have access to the following tools:

### run_python
Description: 执行 Python 3…
Parameters: 〔完整 JSON Schema〕

IMPORTANT: ALWAYS adhere to this
exact format for tool use:
<｜tool▁calls▁begin｜>…
<｜tool▁calls▁end｜>

<｜User｜>〔原数学问题全文〕
<｜Assistant｜>    </think>
```
:::
::::

<div class="slide-takeaway"><span>SAME API</span><strong>Tools 都在 trajectory 之前，但注入语法与 generation cursor 不同</strong></div>
````

### 演讲词（TTS）

现在把第一次带 Tools 的请求放进三种表示。左边的概念表示只解释逻辑顺序。中间是固定版本 Qwen3-Coder 的协议节选。它把 tools 展开成 system block 里的 XML-like 标签，并附带 Tool Call 输出格式说明；随后才渲染 user 和 assistant marker。右边是 DeepSeek V3.1 non-thinking 协议节选。它把同一份工具说明写成 Markdown，并在 assistant marker 后保留结束思考标记。灰色省略项只是为了排版：完整 Schema、模板说明和数学问题仍然存在于真实模型输入。不能把三栏理解成统一格式；它们只是在表达同一份 API 请求的不同序列化结果。

<!-- slide:tool-result-renderings -->
## 11｜Tool Result 请求如何变成模型输入

### 主旨

后续请求重现首次请求的完整共同前缀，并追加 assistant Tool Call 与 Tool Result；Qwen、DeepSeek 对 Tool Result 的 role 映射和 generation cursor 明显不同。

### 展示内容（QMD）

````qmd
## Tool Result 请求如何变成模型输入 {#tool-result-renderings .protocol-slide .result-protocol-slide}

<div class="slide-marker"><b>11</b><span>RESULT RENDERING</span></div>

<div class="protocol-note">协议后缀节选 · 共同前缀 = 第 10 页完整 system + tools + user</div>

:::: {.protocol-grid}
::: {.protocol-panel .concept-protocol}
<div class="protocol-label"><strong>概念表示</strong><span>教学伪表示</span></div>

```text
〔共同前缀完整重现〕

[ASSISTANT_TOOL_CALL id=call_001]
run_python({"code":"〔枚举程序〕"})
[END]

[TOOL_RESULT id=call_001]
{"exit_code":0,
 "stdout":"1663\n8318317\n",
 "stderr":""}
[END]

[ASSISTANT]
```
:::

::: {.protocol-panel .qwen-protocol}
<div class="protocol-label"><strong>Qwen3-Coder</strong><span>真实后缀 · 协议节选</span></div>

```text
〔共同前缀完整重现〕

<|im_start|>assistant
<tool_call>
<function=run_python>
<parameter=code>
〔枚举程序〕
</parameter>
</function>
</tool_call><|im_end|>
<|im_start|>user
<tool_response>
{"exit_code":0,
 "stdout":"1663\n8318317\n",
 "stderr":""}
</tool_response>
<|im_end|>
<|im_start|>assistant
```
:::

::: {.protocol-panel .deepseek-protocol}
<div class="protocol-label"><strong>DeepSeek-V3.1</strong><span>真实后缀 · 协议节选</span></div>

```text
〔共同前缀完整重现〕

<｜Assistant｜></think>
<｜tool▁calls▁begin｜>
<｜tool▁call▁begin｜>run_python
<｜tool▁sep｜>{"code":"〔枚举程序〕"}
<｜tool▁call▁end｜>
<｜tool▁calls▁end｜>
<｜end▁of▁sentence｜>
<｜tool▁output▁begin｜>
{"exit_code":0,
 "stdout":"1663\n8318317\n",
 "stderr":""}
<｜tool▁output▁end｜>
```
:::
::::

<div class="slide-takeaway"><span>SAME HISTORY</span><strong>Qwen 把结果放进 user block；DeepSeek 直接追加 Tool Output</strong></div>
````

### 演讲词（TTS）

第二次请求不是只发送 Tool Result。三栏顶部省略的共同前缀，实际会完整重现第十页的 system、Tool definitions 和原 user message。左边概念表示把 assistant Tool Call、关联的 Tool Result 和新的生成位置依次展开。中间的 Qwen 模板把 assistant 调用写成 tool call 标签，再把 API 的 tool message 放进一个 user block 内的 tool response，最后补新的 assistant marker。右边的 DeepSeek 模板使用专用 Tool Call 与 Tool Output 标记；Tool Result 不另起 User turn，tool output end 后就是继续生成的位置，不再补另一个 Assistant marker。

<!-- slide:current-context-layout -->
## 12｜当前 Context 的布局与来源

### 主旨

History 是完整、原则上 append-only 的经历；Current Context 是 Runtime 每轮从 History、当前配置和外部状态构造的 model-visible projection；Context Window 是该调用可用的 token 容量上限。

### 展示内容（QMD）

````qmd
## 当前 Context 的布局与来源 {#current-context-layout .context-layout-slide}

<div class="slide-marker"><b>12</b><span>CONTEXT LAYOUT</span></div>

:::: {.context-map}
::: {.context-sources}
<div class="source-card history-source"><small>完整记录</small><strong>Append-only History</strong><span>user · assistant · Tool Call / Result</span></div>
<div class="source-card"><small>当前外部状态</small><strong>State / Artifacts</strong><span>文件 · 日志 · 测试 · Patch · 数据库</span></div>
<div class="source-card"><small>每轮重新构造</small><strong>Runtime Config</strong><span>instructions · tools · permissions</span></div>
:::
<div class="projection-arrow"><span>选择 · 组织 · 注入</span><b>CONTEXT<br>POLICY</b></div>
::: {.current-context-stack}
<div class="stack-title"><span>MODEL-VISIBLE</span><strong>Current Context</strong></div>
<div class="stack-block stable">System / Developer instructions</div>
<div class="stack-block stable">Tool definitions · Rules · Permissions</div>
<div class="stack-block selected">Selected History · Summary · Evidence</div>
<div class="stack-block recent">Latest Tool Result · Current User</div>
<div class="stack-block cursor">Assistant generation position</div>
:::
::::

::: {.context-definitions}
<div><b>HISTORY</b><strong>发生过什么</strong><span>完整、可审计、原则上只追加</span></div>
<div><b>CURRENT CONTEXT</b><strong>模型这一次看到什么</strong><span>从 History 与当前状态派生的有限视图</span></div>
<div><b>CONTEXT WINDOW</b><strong>这一次最多能装多少</strong><span>输入与输出共享的 token 容量上限</span></div>
:::

<div class="slide-takeaway"><span>PROJECTION</span><strong>History ≠ Context；改变投影，不等于改写历史</strong></div>
````

### 演讲词（TTS）

从这里开始，我们需要严格区分三个概念。History 是运行中已经发生的完整记录，包括用户消息、模型输出、Tool Call、Tool Result 和状态变化，原则上只追加，用于审计、调试和 replay。Current Context 是本次调用真正送入模型的 token 序列。它不是完整 History，而是 Runtime 从 History、当前文件和日志、Artifacts 以及当前配置中选择并组织出的有限投影。Context Window 则是这次调用能容纳的 token 总上限，输入和输出都要共享它。右侧给出一种逻辑布局：稳定 instructions 和能力协议靠前，被选中的历史、摘要和证据位于中部，最新 Tool Result、当前用户消息和生成位置在尾部。真实字符顺序仍取决于 API 和模型模板。

<!-- slide:context-length-limits -->
## 13｜Context 为什么不能太长

### 主旨

完整 History 不能永久原样进入 Context：窗口有硬容量上限；许多模型存在位置利用差异；更长输入往往增加检索、聚合和抗干扰难度，但后两者的形状与幅度并不跨模型统一。

### 展示内容（QMD）

````qmd
## Context 为什么不能太长 {#context-length-limits .context-limits-slide}

<div class="slide-marker"><b>13</b><span>CONTEXT LIMITS</span></div>

:::: {.limit-grid}
::: {.limit-card .hard-limit}
<small>01 · HARD LIMIT</small><strong>最终会放不下</strong>
<div class="window-meter"><span style="width:92%"></span><i>instructions + tools + history + output</i></div>
<p>History 随 Tool Loop 增长；Context Window 不随任务步数增长。</p>
:::
::: {.limit-card .middle-limit}
<small>02 · POSITION EFFECT</small><strong>位置不同，利用可能不同</strong>
<svg class="u-curve" viewBox="0 0 320 110" aria-label="首尾表现可能高于中部的示意曲线"><path d="M12 24 C82 24, 86 92, 160 92 C234 92, 238 24, 308 24"/><circle cx="12" cy="24" r="5"/><circle cx="160" cy="92" r="5"/><circle cx="308" cy="24" r="5"/></svg>
<p>许多长 Context 评测出现首尾较好、中部较弱；并非所有模型都有同一条 U 型曲线。</p>
:::
::: {.limit-card .usage-limit}
<small>03 · EFFECTIVE CONTEXT</small><strong>放得下，也未必用得好</strong>
<div class="distractor-cloud"><b>目标证据</b><span>旧计划</span><span>重复日志</span><span>冲突版本</span><span>无关结果</span></div>
<p>多信息检索、聚合与抗干扰任务，可能随长度增加而退化。</p>
:::
::::

<div class="limit-qualifier"><b>重要边界</b><span>影响的形状和幅度取决于 <strong>模型 × 任务 × 信息位置 × 干扰项</strong>；没有跨模型、跨任务的统一曲线。</span></div>

<div class="slide-takeaway"><span>WINDOW ≠ USAGE</span><strong>标称容量只回答“能否放下”，不保证“能否稳定利用”</strong></div>
````

### 演讲词（TTS）

为什么不能把完整 History 永远原样放进 Context？第一，Context Window 是硬上限。第二，一些研究表明，信息在 Context 头部和尾部通常比中部获得更好的注意和利用，这种现象叫 Lost in the Middle；但是有些模型和任务的差异极小。第三，更长 Context 往往带入更多旧计划、重复日志、冲突版本和无关结果，使复杂检索与聚合更难。这里也不能简单写成“越长，幻觉必然越多”。退化的形状和幅度取决于模型、任务、信息位置与干扰项，必须针对实际系统测量。

<!-- slide:why-compaction -->
## 14｜为什么 Code Agent 必须 Compaction

### 主旨

长对话不能继续全部进入有限窗口，但 Code Agent 的早期目标、约束、决定、失败与进度又不能像普通闲聊一样随意丢弃；Compaction 因此负责从完整 History 构造更短的后续 Context。

### 展示内容（QMD）

````qmd
## 历史不能全带，关键状态又不能丢 {#why-compaction .compaction-intro-slide}

<div class="slide-marker"><b>14</b><span>WHY COMPACTION</span></div>

:::: {.compaction-pressure}
::: {.pressure-side .history-pressure}
<small>越来越长</small><strong>完整 History</strong>
<div class="history-tape"><span>需求</span><span>读取</span><span>修改</span><span>失败</span><span>修正</span><span>测试</span><span>继续…</span></div>
<p>几十到几百步 trajectory 可以继续 append-only 增长。</p>
:::
<div class="pressure-center"><b>≠</b><span>不能永久<br>原样进入</span></div>
::: {.pressure-side .window-pressure}
<small>固定容量</small><strong>Current Context</strong>
<div class="small-window"><i></i><i></i><i></i><i></i><em>FULL</em></div>
<p>简单截断可能让 Agent 继续执行，却已经偏离原任务。</p>
:::
::::

<div class="must-keep-grid"><span>初始需求</span><span>兼容约束</span><span>架构决定</span><span>失败原因</span><span>修改与验证</span><span>待办与权限</span></div>

<div class="compaction-answer"><small>COMPACTION</small><strong>完整 History 保留；为下一轮构造更短的 continuation Context</strong></div>

<div class="slide-takeaway"><span>NOT DELETE</span><strong>缩减的是 model-visible projection，不是审计用的完整 History</strong></div>
````

### 演讲词（TTS）

于是矛盾出现了。左边，Code Agent 的 History 会随着读取、修改、失败、修正和测试不断增长。右边，Current Context 的容量固定，不能永久容纳全部轨迹。普通聊天可以简单丢掉早期消息，但 Code Agent 不行：最初需求、兼容性约束、架构决定、失败原因、修改与验证、待办、权限和验收条件都可能在很早以前出现。工作区虽然保存代码状态，却不能替代模型需要知道的目标、进展、决定和未解决问题。直接截断可能让 Agent 继续行动，却已经不再完成原任务。Compaction 解决的正是这个矛盾：完整 History 仍然保留，只为下一轮模型调用构造更短、可继续工作的 Context。

<!-- slide:compaction-methods -->
## 15｜缩减 History 的三类方法

### 主旨

缩减历史单元只有三种基本关系：整体不再可见、保留原文子集、或生成新的派生表示；本文显式列举 4 种丢弃、4 种删减和 2 种摘要形式。

### 展示内容（QMD）

````qmd
## 缩减 History 的三类方法 {#compaction-methods .compaction-methods-slide}

<div class="slide-marker"><b>15</b><span>THREE OPERATIONS</span></div>

<table class="method-table">
  <thead><tr><th>类别</th><th>本文列举</th><th>具体方法</th><th>概念</th></tr></thead>
  <tbody>
    <tr class="drop"><th rowspan="4">丢弃<br><small>Drop</small><b>4</b></th><td><code>C(H)=空</code></td><td>Sliding Window</td><td>Context 向前滑，只保留近期窗口内的完整历史单元</td></tr>
    <tr class="drop"><td><code>C(H)=空</code></td><td>Last-N</td><td>固定保留最后 N 条 message、Turn 或 Episode</td></tr>
    <tr class="drop"><td><code>C(H)=空</code></td><td>超限移除最早 Turn</td><td>达到 token 上限时，按时间淘汰最旧完整轮次</td></tr>
    <tr class="drop"><td><code>C(H)=空</code></td><td>按相关性淘汰</td><td>依据当前任务，决定整个历史单元是否继续可见</td></tr>
    <tr class="prune"><th rowspan="4">删减<br><small>Extractive</small><b>4</b></th><td>原文子集</td><td>Tool Result Clearing</td><td>用短标记、关键统计和 Artifact 指针替代冗长旧输出</td></tr>
    <tr class="prune"><td>原文子集</td><td>截取错误栈</td><td>保留异常类型、关键帧与相关原文，删除重复栈帧</td></tr>
    <tr class="prune"><td>原文子集</td><td>相关代码行</td><td>只保留当前问题涉及的原始代码片段</td></tr>
    <tr class="prune"><td>原文子集</td><td>精确字段摘取</td><td>保留路径、数字、符号和测试失败，不生成新叙述</td></tr>
    <tr class="summarize"><th rowspan="2">摘要<br><small>Abstractive</small><b>2</b></th><td>派生表示</td><td>自然语言摘要</td><td>把多轮行为重新叙述为较短的任务状态</td></tr>
    <tr class="summarize"><td>派生表示</td><td>结构化 State</td><td>按事实、决定、失败、待办与证据位置等固定字段表达</td></tr>
  </tbody>
</table>

<div class="method-note"><span>Tool Call / Result 必须作为完整协议单元处理</span></div>

<div class="slide-takeaway"><span>4 + 4 + 2</span><strong>这里只列举常见做法，不是所有可能性</strong></div>
````

### 演讲词（TTS）

对一个选定的历史单元 H，缩减只有三种基本关系。丢弃让它在本轮 Context 中完全不可见，C H 等于空。本文列出 Sliding Window、Last N、超限移除最早 Turn 和按相关性淘汰四种选择策略。删减至少保留原文的一部分，不生成新叙述；常见操作是清理旧 Tool Result、截取错误栈、保留相关代码行，以及摘取路径、数字、符号和测试失败。摘要则生成新的派生表示，可以是自然语言，也可以是结构化 State。这里只列举常见做法，不是所有可能性。Tool Call 和对应 Result 还必须成对处理，不能破坏协议完整性。

<!-- slide:compaction-flow -->
## 16｜Compaction 的基本流程

### 主旨

Compaction 是 Runtime 在阈值或阶段边界集中重建 Context 的事件：安全切分旧前缀与近期原文，对旧前缀组合应用缩减操作，再以 continuation state 开启新 epoch。

### 展示内容（QMD）

````qmd
## Compaction 的基本流程 {#compaction-flow .compaction-flow-slide}

<div class="slide-marker"><b>16</b><span>COMPACTION FLOW</span></div>

<div class="compact-flow-grid">
  <div class="compact-step"><b>01</b><strong>监控 Context</strong><span>token 使用量 · 阶段边界</span></div>
  <div class="compact-step"><b>02</b><strong>触发 Compaction</strong><span>达到阈值或显式触发</span></div>
  <div class="compact-step"><b>03</b><strong>安全切分</strong><span>old prefix <code>P</code> · raw window <code>T</code></span></div>
  <div class="compact-step"><b>04</b><strong>缩减旧前缀</strong><span>Drop · Prune · Summarize</span></div>
  <div class="compact-step"><b>05</b><strong>重建 Context</strong><span>stable instructions + <code>S</code> + <code>T</code></span></div>
  <div class="compact-step"><b>06</b><strong>开启新 Epoch</strong><span>继续追加新的事件</span></div>
</div>

<div class="compact-equations">
  <code>History projection = old prefix P + recent raw window T</code>
  <span>→</span><code>S = compact(P)</code>
  <span>→</span><code>New Context = stable instructions + S + T</code>
</div>

<div class="safe-boundary">
  <div><b>RAW WINDOW</b><span>最新要求 · 当前错误 · 最新 Tool Result · 未闭合操作 · 精确代码</span></div>
  <div><b>SAFE BOUNDARY</b><span>一般位于两个 Turn 之间 · 每个 Turn 全部压缩或全部保留</span></div>
</div>

<div class="slide-takeaway"><span>NEW EPOCH</span><strong>Context 被重建；完整 History 仍然 append-only</strong></div>
````

### 演讲词（TTS）

第一步监控 token 使用量或任务阶段；达到阈值后触发 Compaction。然后把当前 model-visible trajectory 安全切成旧前缀 P 和近期原文窗口 T。切分点一般在两个 Turn 之间，每个 Turn 的信息要么全部压缩，要么全部保留。Runtime 对旧前缀组合使用丢弃、删减和摘要，得到较短的 continuation state S；再用稳定 instructions、S 和原样保留的 T 构造新 Context，开启新的 context epoch。Raw Window 常用于保留最新要求、当前错误和精确代码，但它只是常见策略，不是 Compaction 的定义，也没有行业统一的固定比例。

<!-- slide:compact-payload-diff -->
## 17｜Compact 前后的 API 核心载荷

### 主旨

Compact 改变的是下一次请求中的 messages 投影：稳定 System、Tools 与近期 Raw Window 保留，长旧前缀由较短 continuation state 取代；原始 History、工作区和 Artifacts 不会消失。

### 展示内容（QMD）

````qmd
## Compact 前后：messages 发生了什么 {#compact-payload-diff .compact-diff-slide}

<div class="slide-marker"><b>17</b><span>PAYLOAD DIFF</span></div>

:::: {.payload-diff-grid}
::: {.message-stack .before-stack}
<div class="stack-head"><b>BEFORE</b><span>长 trajectory</span></div>
<div class="msg system-msg"><code>system</code><span>稳定 Agent instructions</span></div>
<div class="msg user-msg"><code>user</code><span>升级解析器；保持兼容并通过测试</span></div>
<div class="msg assistant-msg"><code>assistant</code><span>read_file Tool Call</span></div>
<div class="msg tool-msg"><code>tool</code><span>大段文件内容</span></div>
<div class="msg omitted-msg"><code>…</code><span>数十组搜索 · 编辑 · 失败测试 · 修正</span></div>
<div class="msg user-msg raw"><code>user</code><span>继续修复剩余测试</span><b>RAW</b></div>
<div class="tools-row">tools: read_file · edit_file · run_tests</div>
:::
::: {.diff-transform}
<small>OLD PREFIX</small><b>COMPACT</b><span>→</span>
<div class="state-fields"><i>任务</i><i>硬约束</i><i>已完成</i><i>已验证</i><i>失败原因</i><i>修改文件</i><i>下一步</i><i>证据</i></div>
:::
::: {.message-stack .after-stack}
<div class="stack-head"><b>AFTER</b><span>新 Context Epoch</span></div>
<div class="msg system-msg"><code>system</code><span>同一稳定 Agent instructions</span></div>
<div class="msg summary-msg"><code>developer</code><span>&lt;continuation_state&gt;<br>任务 · 约束 · 进度 · 错误 · 下一步 · 证据<br>&lt;/continuation_state&gt;</span></div>
<div class="msg user-msg raw"><code>user</code><span>继续修复剩余测试</span><b>RAW</b></div>
<div class="tools-row">tools: 同一组 definitions</div>
:::
::::

<div class="diff-foot"><span>旧 messages：仍在完整 History</span><span>文件 / Git diff / 日志：仍在 Workspace 或 Artifacts</span><span>Summary role：实现相关</span></div>

<div class="slide-takeaway"><span>REPLACE VIEW</span><strong>中间历史退出后续推理，由摘要替代</strong></div>
````

### 演讲词（TTS）

Compact 之前，请求包含稳定 system、初始任务、数十组 assistant Tool Call 和 Tool Result，以及最新 user message。Compact 之后，稳定 system 和 tools 仍然存在；最新的“继续修复剩余测试”作为 Raw Window 原样保留；中间历史退出后续推理，由摘要替代。示例使用 developer role，但不同 Runtime 也可能使用 system、user、assistant 或不透明协议项。History 中保留全部原始信息，文件、日志等也不发生变化。变化的只有模型下次看到的视图。

<!-- slide:summary-generation -->
## 18｜Agent 如何产生摘要

### 主旨

可读 continuation summary 通常来自额外模型调用；追加式保留原 Message roles，主要靠指令要求摘要器聚焦，而转录式允许 Runtime 在请求前直接选择、截断或外置摘要器能看到的数据。

### 展示内容（QMD）

````qmd
## Agent 如何产生摘要 {#summary-generation .summary-generation-slide}

<div class="slide-marker"><b>18</b><span>SUMMARY REQUEST</span></div>

:::: {.summary-lanes}
::: {.summary-lane .append-lane}
<div class="lane-title"><b>A</b><strong>追加式摘要请求</strong><span>保留原 roles</span></div>
::: {.summary-request-stack}
<div>Compression System Prompt</div>
<div class="role-sequence">user → assistant → tool → …</div>
<div class="summary-instruction">user: 按指定结构生成 continuation summary</div>
<i>↓</i><div class="summary-output">assistant: summary</div>
:::
<div class="pros-cons"><p><b>优点</b>保留 Message role 与 Tool 协议；同前缀时可能复用 Cache</p><p><b>限制</b>选入的前缀仍须放得下；主要靠指令要求模型关注或忽略</p></div>
<small>Gemini CLI · Claude Code · Continue</small>
:::
::: {.summary-lane .transcript-lane}
<div class="lane-title"><b>B</b><strong>转录式专用摘要请求</strong><span>Runtime 先选数据</span></div>
<div class="runtime-selector"><span>选择旧 History</span><span>截断大 Result</span><span>外置 Artifact</span><span>移除 Agent Tools</span></div>
::: {.summary-request-stack}
<div>system: 你是 Context Compactor</div>
<div class="transcript">user: &lt;history&gt; [User] … [Tool result] … &lt;/history&gt;</div>
<i>↓</i><div class="summary-output">structured summary</div>
:::
<div class="pros-cons"><p><b>优点</b>直接控制摘要器能看到什么；可用独立、更便宜的模型</p><p><b>代价</b>通常不能复用原 trajectory Cache；role 与 Tool 结构可能损失</p></div>
<small>OpenCode · Aider · Cline · OpenHands</small>
:::
::::

<div class="slide-takeaway"><span>WHO SELECTS?</span><strong>追加式主要用指令约束；转录式先由 Runtime 决定可见数据</strong></div>
````

### 演讲词（TTS）

Agent 通常需要额外模型调用来产生可读摘要。第一类是追加式，Agent 在现有 Context 的最后追加一条专用摘要指令。它保留原协议结构，并可能复用旧 Prefix Cache。第二类是转录式：Agent 选择合适数据，把要格式化的事件序列化成 transcript，再交给模型压缩。Agent 能决定摘要器看到什么，也能选更便宜的模型。

<!-- slide:agent-compaction-table -->
## 19｜主流 Agent 怎样 Compaction

### 主旨

Gemini CLI、Claude Code 与 OpenCode 都用模型生成 continuation state，但摘要请求结构、回填 role、Raw Window 和摘要模型策略并不统一。

### 展示内容（QMD）

````qmd
## 主流 Agent 的 Compaction 行为 {#agent-compaction-table .agent-compaction-slide}

<div class="slide-marker"><b>19</b><span>AGENT BEHAVIOR</span></div>

<table class="agent-table">
  <thead><tr><th>Agent</th><th>摘要请求</th><th>Compact 后 Context</th><th>Raw Window / 模型</th></tr></thead>
  <tbody>
    <tr class="gemini-row">
      <th><strong>Gemini CLI</strong><small>固定 revision</small></th>
      <td>Compression System Prompt<br>+ 原始旧 messages<br>+ 末尾 user 摘要指令<br><b>再调用一次模型校验</b></td>
      <td><code>user(state_snapshot)</code><br>+ <code>model(固定确认)</code><br>+ raw tail</td>
      <td>目标近期约 30% <small>按字符近似</small><br>映射到对应 compression model</td>
    </tr>
    <tr class="claude-row">
      <th><strong>Claude Code</strong><small>公开文档 + 固定发布版证据</small></th>
      <td>追加式摘要请求<br>禁止 Tools</td>
      <td>合成 user summary<br>+ Runtime 重注入 startup、Memory 与受保护内容</td>
      <td>普通全量 Compact 默认无 raw tail<br>通常当前主模型，可 fallback</td>
    </tr>
    <tr class="opencode-row">
      <th><strong>OpenCode</strong><small>1.18.21 · V1 Runtime</small></th>
      <td>旧 History 转录成单一 user request<br>专用 Compaction Agent<br>Tools 为空</td>
      <td><code>user: What did we do so far?</code><br>+ <code>assistant: summary</code><br>+ raw tail</td>
      <td>优先完整近期 Turns；预算不足可 Turn 内切分<br>默认当前模型，也可独立配置</td>
    </tr>
  </tbody>
</table>

<div class="agent-boundary"><span><b>Gemini</b> 约 30% 不是行业比例</span><span><b>Claude</b> 内部结构可能随版本变化</span><span><b>OpenCode</b> V2 表示不同</span></div>

<div class="slide-takeaway"><span>NO STANDARD</span><strong>Summary 的请求、role、Tail 和模型选择都没有统一协议</strong></div>
````

### 演讲词（TTS）

三个主流 Agent 展示了三种不同选择。Gemini CLI 采用追加式请求，第一次调用模型压缩，第二次调用模型检查遗漏，目标保留大约百分之三十的近期内容。Claude Code 采用追加式，默认不保留 raw tail，会重新注入 startup content、Memory 和受保护内容。OpenCode 采用转录式，并保留 raw tail。三者都在做 continuation，但请求结构、回填 role、Tail 和模型选择没有统一协议。

<!-- slide:openai-compaction -->
## 20｜OpenAI：Provider-native Compaction

### 主旨

OpenAI Responses API 的 `/responses/compact` 不是客户端追加“请总结”的普通模型回复，而是服务端返回包含 encrypted compaction item 的 canonical Context；客户端必须把整个输出原样传入下一请求。

### 展示内容（QMD）

````qmd
## OpenAI：最特殊的 Compaction {#openai-compaction .openai-compaction-slide}

<div class="slide-marker"><b>20</b><span>PROVIDER-NATIVE</span></div>

<div class="openai-flow">
  <div class="oa-node input"><small>完整 INPUT ITEMS</small><strong>messages + tools<br>+ reasoning / other items</strong></div>
  <i>→</i>
  <div class="oa-node endpoint"><small>SERVER PASS</small><strong>POST<br>/responses/compact</strong></div>
  <i>→</i>
  <div class="oa-node canonical"><small>CANONICAL CONTEXT</small><strong>encrypted compaction item<br>+ 可能保留的旧 items</strong></div>
  <i>→</i>
  <div class="oa-node next"><small>原样携带</small><strong>POST /responses<br>+ 新 user item</strong></div>
</div>

<div class="compaction-compare">
  <div><b>Agent-side Summary</b><span>History → 可读 Summary</span><span>Runtime 选择、生成并回填</span><span>字段通常可读、可定义</span></div>
  <div class="native"><b>OpenAI Provider-native</b><span>Input items → 服务端 Compaction Pass</span><span>Provider 返回 canonical Context</span><span>encrypted item 不透明、不可编辑</span></div>
</div>

<div class="opaque-rules">
  <span>不要解析</span><span>不要编辑</span><span>不要删减</span><span>不要重新摘要</span><strong>原样传递 <code>compacted.output</code></strong>
</div>

<div class="unknown-box"><b>官方未公开</b><span>内部 Compaction Prompt · 摘要模型 · 精确选择算法 · encrypted content 的语义结构</span></div>

<div class="slide-takeaway"><span>MACHINE STATE</span><strong>返回的不是“给人看的摘要”，而是下一请求必须携带的 canonical state</strong></div>
````

### 演讲词（TTS）

OpenAI Responses API 的做法最特殊。客户端把完整 input items 交给 responses compact endpoint，它不是在 messages 尾部追加“请总结”，也不是一次普通 assistant generation。服务端返回新的 canonical compacted Context，其中包含 encrypted compaction item，也可能保留部分旧 items。这个 encrypted item 携带继续任务所需的旧状态和 reasoning，但它是面向机器的不透明状态，不供人阅读。客户端不应解析、编辑、删减或重新摘要 compacted output，而应把整个输出原样传给下一次 Responses 请求，再追加新的 user item。官方没有公开内部 Prompt、摘要模型、精确选择算法或加密内容结构，因此不能把它猜成隐藏的 user summary。它与客户端可读 Summary 是两类不同机制。

<!-- slide:incremental-state-machine -->
## 21｜从增量状态机理解模型推理

### 主旨

把模型推理抽象为沿精确 token prefix 递增的状态转移：相同前缀可以恢复已有状态，首个不同 token 之后必须沿新分支重新计算；这只是计算依赖的工程抽象，不代表 Prompt 必须逐 token 串行处理。

### 展示内容（QMD）

````qmd
## 从增量状态机理解模型推理 {#incremental-state-machine .incremental-state-slide}

<div class="slide-marker"><b>21</b><span>INCREMENTAL STATE</span></div>

<div class="state-machine-scope"><b>工程抽象</b><span>固定 Model</span><span>固定 Tokenizer</span><span>固定输入协议</span><i>不代表 Prompt 必须逐 Token 串行计算</i></div>

<div class="state-chain">
  <div class="state-main-path"><strong>S₀</strong><i><code>A</code> →</i><strong>S(A)</strong><i><code>B</code> →</i><strong>S(A,B)</strong><i><code>C</code> →</i><strong>S(A,B,C)</strong></div>
  <div class="state-fork-path"><span>从 S(A) 分叉</span><i><code>X</code> →</i><strong>S(A,X)</strong><i><code>C</code> →</i><strong>S(A,X,C)</strong><i><code>D</code> →</i><strong>S(A,X,C,D)</strong></div>
</div>

<div class="state-output-loop"><span>当前 Prefix State</span><b>→</b><span>下一个 Token 的概率分布</span><b>→</b><span>Runtime 选择 Token</span><b>↩</b><strong>作为新输入，继续推进状态</strong></div>

:::: {.state-branch-grid}
::: {.state-case .state-hit-case}
<div class="state-case-title"><b>HIT</b><strong>恢复状态，只算新后缀</strong></div>
<div class="state-sequence"><span>已缓存</span><code>A + B</code><em>→ S(A,B)</em></div>
<div class="state-sequence"><span>新请求</span><code><mark>A + B</mark> + D + E</code><em>→ 只计算 D + E</em></div>
:::
::: {.state-case .state-fork-case}
<div class="state-case-title"><b>FORK</b><strong>首个差异后全部重算</strong></div>
<div class="state-sequence"><span>旧序列</span><code>A + B + C + D</code><em>旧分支</em></div>
<div class="state-sequence"><span>新序列</span><code><mark>A</mark> + X + C + D</code><em>复用 S(A)；重算 X + C + D</em></div>
:::
::::

<div class="state-cache-note"><b>KV CACHE</b><span>各层、各历史位置的 K / V 是可复用状态的主体</span><i>位置 · 页表等元数据负责组织</i></div>

<div class="slide-takeaway"><span>EXACT PREFIX</span><strong>相同前缀复用状态；从第一个不同 Token 开始沿新分支计算</strong></div>
````

### 演讲词（TTS）

进入 Cache 之前，先把模型推理抽象成一台增量状态机。这只是理解计算依赖的工程直觉，不是另一种模型架构。对固定的模型、Tokenizer 和输入协议，每读入一个 token，模型就推进到对应更长前缀的状态；模型生成的 token 也会作为下一步输入继续推进。K V Cache 是这份可复用状态的主体。如果新请求仍以 A、B 开头，就能恢复 S A B，只计算新的后缀。若旧序列是 A、B、C、D，新序列变成 A、X、C、D，那么只能复用 A；从第一个不同 token 开始，后续状态都依赖另一条前缀，必须重新计算。

<!-- slide:transformer-kv-cache -->
## 22｜Transformer 推理与 KV Cache

### 主旨

Prefill 是对已知 Prompt 的批量推进优化，而不是架构必需的独立步骤；Decode 因输出尚未确定而逐步推进。KV Cache 保存前缀状态的主体，避免重复计算旧 K/V。

### 展示内容（QMD）

````qmd
## 已知输入批量算，未知输出逐步算 {#transformer-kv-cache .transformer-cache-slide}

<div class="slide-marker"><b>22</b><span>TRANSFORMER · KV CACHE</span></div>

<div class="token-ribbon"><span>rendered input</span><code>t₀</code><code>t₁</code><code>t₂</code><code>…</code><code>tₙ</code><i>→</i><strong>Transformer</strong></div>

:::: {.inference-phases}
::: {.phase-card .prefill-phase}
<div class="phase-head"><b>01</b><strong>PREFILL</strong><span>处理已有输入</span></div>
<div class="parallel-tokens"><i>t₀</i><i>t₁</i><i>t₂</i><i>t₃</i><i>…</i><i>tₙ</i></div>
<p>同一层内，多个 prompt 位置可批量计算；层与层之间仍顺序执行。</p>
:::
::: {.phase-card .decode-phase}
<div class="phase-head"><b>02</b><strong>DECODE</strong><span>逐个生成</span></div>
<div class="decode-chain"><i>tₙ₊₁</i><b>→</b><i>tₙ₊₂</i><b>→</b><i>tₙ₊₃</i><b>→</b><i>…</i></div>
<p>下一个 token 依赖已经生成的前缀，天然更串行。</p>
:::
::::

:::: {.attention-cache-map}
::: {.attention-step}
<small>EACH LAYER · ATTENTION</small>
<div class="qkv-row"><b>Q</b><span>发起匹配</span><b>K</b><span>被匹配</span><b>V</b><span>取回表示</span></div>
<p>新 token 仍产生新的 Q / K / V，并用 Query 关注旧 Keys。</p>
:::
<div class="cache-transfer"><span>保存已处理 token 的</span><b>K / V</b><i>→</i></div>
::: {.kv-bank}
<small>GPU MEMORY</small><strong>KV CACHE</strong>
<div><i>Layer 1</i><span>K₀…Kₙ</span><span>V₀…Vₙ</span></div><div><i>Layer 2</i><span>K₀…Kₙ</span><span>V₀…Vₙ</span></div><div><i>…</i><span>…</span><span>…</span></div>
:::
::::

<div class="slide-takeaway"><span>TRADE-OFF</span><strong>少做重复计算，但 Context 越长，KV 的存储与读取成本越高</strong></div>
````

### 演讲词（TTS）

刚才的状态转移是计算依赖的抽象，不代表 Prompt 必须逐 token 串行执行。实际推理会把已知输入放进 Prefill，在同一层内批量计算多个位置；因果掩码保证每个位置只能读取自己和更早的 token。Decode 的下一个 token 尚未确定，所以必须生成一个，再继续一个。每层 Attention 都会计算 Query、Key 和 Value，旧 token 的 Key 和 Value 保存在 K V Cache 中。它避免重新计算旧 K V，但新 Query 仍要读取前缀；因此 Context 越长，显存占用和读取成本越高。

<!-- slide:cross-request-prefix-cache -->
## 23｜跨请求复用 KV Cache：前缀匹配

### 主旨

跨请求 Prefix Cache 寻找模型实际输入中最长的精确 token 前缀；命中部分直接复用 K/V，只对新增或分叉后的 suffix 做 Prefill。

### 展示内容（QMD）

````qmd
## 跨请求复用：只认最长相同前缀 {#cross-request-prefix-cache .prefix-match-slide}

<div class="slide-marker"><b>23</b><span>CROSS-REQUEST CACHE</span></div>

<div class="request-prefix first-prefix"><b>REQUEST 1</b><span class="hit">A · system + tools</span><span class="hit">B · history</span><span class="old">C · user #1</span><i>完整 Prefill → 写入 K/V</i></div>
<div class="prefix-rail"><span>从输入开头逐 token 比较</span><b>LONGEST EXACT PREFIX</b><em>首个不同 token</em></div>
<div class="request-prefix second-prefix"><b>REQUEST 2</b><span class="hit">A · system + tools</span><span class="hit">B · history</span><span class="new">D · user #2</span><i>复用 A + B；只 Prefill D</i></div>

:::: {.prefix-verdicts}
<div class="prefix-verdict yes"><b>HIT</b><code>A + B</code><span>复用每层对应的 K / V</span></div>
<div class="prefix-verdict no"><b>MISS / NEW</b><code>D</code><span>从分叉点开始重新计算</span></div>
<div class="prefix-verdict exact"><b>EXACT TOKENS</b><code>renderer → tokenizer</code><span>不是“语义差不多”</span></div>
::::

<div class="prefix-inputs"><span>system</span><span>messages</span><span>tools / schema</span><span>images</span><span>special tokens</span><strong>都可能进入 Prefix</strong></div>

<div class="slide-takeaway"><span>RULE</span><strong>相同文本不够；模型最终看到的 token 前缀必须一致</strong></div>
````

### 演讲词（TTS）

单次推理有 K V Cache，供应商还可以把它跨请求复用。第一次请求处理 A、B、C，并缓存这些 token 对应的推理状态。第二次请求是 A、B、D，系统从输入开头寻找最长相同前缀，因此复用 A 加 B，只为新的 D 做 Prefill。这里匹配的不是语义相似，也不只是用户能看到的文本，而是 Renderer 和 Tokenizer 之后模型实际收到的精确 token 序列。System、Messages、Tool schemas、图片和特殊控制 token 都可能属于这个前缀。一般原则是：首个 token 出现差异，旧分支的命中就在那里停止。

<!-- slide:prefix-cache-implementations -->
## 24｜Prefix Cache 的三类实现

### 主旨

Prefix Cache 在 API 和逻辑匹配层至少有三类机制：自动固定 token blocks、选定累计前缀的 breakpoints，以及预先创建并按 ID 引用的命名缓存对象；它们不是互斥的物理存储格式。

### 展示内容（QMD）

````qmd
## Prefix Cache：三种“从哪里命中” {#prefix-cache-implementations .cache-implementations-slide}

<div class="slide-marker"><b>24</b><span>THREE IMPLEMENTATIONS</span></div>

:::: {.cache-method-grid}
::: {.cache-method .block-method}
<div class="cache-method-title"><b>01</b><strong>固定 Token Blocks</strong><span>AUTO</span></div>
<div class="block-chain"><i>A</i><i>B</i><i>C</i><i class="partial">D…</i></div>
<p>每个完整定长 block 自动形成候选点；沿 parent hash 找最长相同 block prefix。</p>
<small>细粒度、无需标记；差异发生在 block 内时，通常只能退回上一完整块。</small>
:::
::: {.cache-method .breakpoint-method}
<div class="cache-method-title"><b>02</b><strong>Breakpoints</strong><span>SELECTED</span></div>
<div class="breakpoint-chain"><i>system</i><b>◆ BP1</b><i>project</i><b>◆ BP2</b><i>chat</i></div>
<p>只在选定位置写入或检查“从开头到这里”的累计前缀。</p>
<small>可控、可分层；未选中的中间位置不保证成为独立命中点。</small>
:::
::: {.cache-method .named-method}
<div class="cache-method-title"><b>03</b><strong>命名缓存对象</strong><span>BY ID</span></div>
<div class="named-cache"><code>create(A+B)</code><b>→</b><strong>cache/123</strong><span>request(cache/123, C)</span></div>
<p>先提交稳定内容并创建资源；后续请求显式引用 cache ID。</p>
<small>复用更确定；要管理不可变内容、模型绑定、TTL、权限与费用。</small>
:::
::::

<div class="implementation-boundary"><b>逻辑机制 ≠ 物理布局</b><span>Breakpoint 或命名对象底层仍可能使用固定大小的 KV pages；API “block” 也不等于物理 page。</span></div>

<div class="slide-takeaway"><span>NOT A FOURTH TYPE</span><strong>Chunked Prefill 只调度未命中的 suffix，不决定 Prefix 如何匹配</strong></div>
````

### 演讲词（TTS）

最长前缀匹配具体怎样实现？从 API 和逻辑匹配层看，可以分成三类。第一类是固定 token blocks，引擎沿 token 序列自动切块，每个完整块都能成为候选命中点，并通过 parent hash 保证这个块属于同一个前缀。第二类是 Breakpoint，只在客户端或供应商选定的位置保存从开头累计到这里的前缀；Breakpoint 的意思是“缓存到这里”，不是“从这里开始”。第三类是命名缓存对象：先创建一段不可变缓存，后续按资源 ID 引用。三类机制描述的是如何创建和寻找逻辑缓存条目，不是三种互斥的物理存储。Breakpoint 和命名对象底层仍可能由固定大小的 K V pages 承载。

<!-- slide:provider-cache-table -->
## 25｜主流供应商的 Prefix Cache 做法

### 主旨

供应商公开的是对外机制、最低长度或可观察粒度和生命周期；这些信息不能反推出内部物理 KV page 大小，且不同机制不可只拿一个“block size”横向比较。

### 展示内容（QMD）

````qmd
## 主流供应商：公开到哪一层？ {#provider-cache-table .provider-cache-slide}

<div class="slide-marker"><b>25</b><span>PROVIDER LANDSCAPE</span></div>

<table class="provider-cache-table">
  <thead><tr><th>供应商</th><th>对外机制</th><th>公开门槛 / 粒度</th><th>生命周期</th></tr></thead>
  <tbody>
    <tr><th>OpenAI</th><td>早期自动增量；GPT-5.6+ 隐式 / 显式 breakpoint</td><td>GPT-5.6+ 最短 1,024 tokens；早期命中量按 128-token 增量报告</td><td>GPT-5.6+ 默认 30 分钟；早期依 retention</td></tr>
    <tr><th>Anthropic</th><td>自动或最多 4 个 content-block breakpoints</td><td>模型相关：512–4,096 tokens；读取向前检查最多 20 个内容块</td><td>默认 5 分钟；可选 1 小时；命中刷新</td></tr>
    <tr><th>Gemini API</th><td>2.5+ 自动隐式；显式为命名 CachedContent</td><td>隐式：2.5 为 2,048；当前 3.x 为 4,096 tokens</td><td>显式默认 1 小时；隐式未公开</td></tr>
    <tr><th>DeepSeek</th><td>自动硬盘前缀单元缓存</td><td>现行固定间隔未公开；64 tokens 仅是 2024 历史方案</td><td>不活跃后通常数小时至数天，非固定 SLA</td></tr>
    <tr><th>Kimi</th><td>自动、完全一致的前缀匹配</td><td>前一请求 prompt &gt; 256 tokens；内部粒度未公开</td><td>自动管理；数值未公开</td></tr>
    <tr><th>GLM</th><td>自动隐式“相同或高度相似内容”缓存</td><td>最小长度、粒度、精确算法均未公开</td><td>仅说明过期后重算</td></tr>
  </tbody>
</table>

<div class="provider-table-note"><b>截至 2026-08-24</b><span>API content block / 命中报告增量 / breakpoint</span><i>≠</i><strong>服务内部物理 KV page</strong></div>

<div class="slide-takeaway"><span>UNKNOWN MEANS UNKNOWN</span><strong>供应商没公开物理 block size，就不能从计费粒度或 API 名词反推</strong></div>
````

### 演讲词（TTS）

把三类机制映射到供应商，会发现公开层次并不一致。OpenAI 早期模型表现为自动增量命中，GPT 五点六以后公开为 Breakpoint；Anthropic 提供自动缓存和显式 Content Block Breakpoints；Gemini 同时有隐式缓存与命名 CachedContent；DeepSeek、Kimi 和 GLM 提供不同程度的自动缓存。OpenAI 早期按一百二十八 token 增量报告 cached tokens，不证明物理 page 就是一百二十八。Anthropic 的 Content Block 是 API 内容块，不是定长 token block。DeepSeek 的六十四 token 是二零二四年历史方案，不能当作现行物理页。信息采集截止日期是今年八月二十四日，实际情况以供应商官方文档为准。

<!-- slide:tools-cache-miss -->
## 26｜改变 Tools 为什么会导致 Cache Miss

### 主旨

Tool definitions 通常位于 trajectory 之前；只要其中一个 model-visible token 改变，最长公共前缀就在该处结束，后续 History 即使字面相同，其 K/V 也因依赖不同前缀而必须重算。

### 展示内容（QMD）

````qmd
## 改一个 Tool，为什么旧 History 也命不中？ {#tools-cache-miss .tools-miss-slide}

<div class="slide-marker"><b>26</b><span>TOOLS → CACHE MISS</span></div>

<div class="cache-formula"><code>P₁ = S + <mark>T₁</mark> + H</code><code>P₂ = S + <mark>T₂</mark> + H + N</code></div>

:::: {.tool-prefix-compare}
<div class="tool-prefix-row old-tools"><b>上一轮</b><span class="shared">S · stable system</span><span class="tools">T₁ · tools v1</span><span class="history">H · long history</span></div>
<div class="difference-marker"><i>↑</i><strong>首个不同 token</strong><span>name / description / schema / order / whitespace</span></div>
<div class="tool-prefix-row new-tools"><b>下一轮</b><span class="shared">S · stable system</span><span class="tools changed">T₂ · tools v2</span><span class="history recalc">H · same text, new K/V</span><span class="suffix">N</span></div>
::::

<div class="dependency-chain"><span>修改 Tool definitions</span><b>→</b><span>前缀在差异处断开</span><b>→</b><span>其后的 H 按新前缀重算</span><b>→</b><span>只保留差异前的命中</span></div>

:::: {.miss-boundaries}
<div><b>不是“文字相同就能接回”</b><span>H 的 K/V 条件是 S + T；T 变了，H 的状态也变了。</span></div>
<div><b>也不是“旧缓存被删除”</b><span>这是当前新请求逻辑 miss；旧分支能否再次命中取决于 TTL、eviction 和路由。</span></div>
::::

<div class="slide-takeaway"><span>FIRST DIFFERENCE</span><strong>Tools 越靠前、History 越长，一次 schema 变化需要重算的 suffix 越大</strong></div>
````

### 演讲词（TTS）

现在可以直接推导 Tools 对 Cache 的影响。上一轮输入是稳定 System，加 Tools 一，再加长 History。下一轮把 Tools 改成版本二，History 文字虽然完全不变，但最长相同前缀会在 Tool definitions 的首个不同 token 处终止。History 的 Key 和 Value 是在旧前缀 System 加 Tools 一的条件下计算的，不能直接接到新的 Tools 二后面，因此后续整段都要重新 Prefill。增删工具、改 name、description、schema、顺序，甚至模板 whitespace，都可能产生这个结果。准确说法不是“改变 Tools 让所有 token 永久失效”，而是差异点之前仍可能命中，差异点之后对当前请求不能复用；旧缓存也不一定被物理删除。

<!-- slide:tools-head-or-tail -->
## 27｜Tool Definitions 放在头部还是尾部

### 主旨

稳定 Tools 前置可形成多轮 append-only prefix；频繁变化的 Tools 后置可保住更长 History 前缀，但每轮移动 Tools 也会制造分叉。布局必须服从训练协议，并按工作负载取舍。

### 展示内容（QMD）

````qmd
## Tool Definitions：放头，还是放尾？ {#tools-head-or-tail .tools-position-slide}

<div class="slide-marker"><b>27</b><span>HEAD vs TAIL</span></div>

:::: {.position-comparison}
::: {.position-card .tools-first}
<div class="position-title"><b>A</b><strong>前置 Tools</strong><code>S + T + H</code></div>
<div class="rounds"><span>R1 · S + T + H₀</span><span>R2 · S + T + H₀ + D₁</span><span>R3 · S + T + H₀ + D₁ + D₂</span></div>
<div class="position-good">稳定 Tools：天然形成增长的 append-only prefix</div>
<div class="position-bad">动态 Tools：前部变化让后续长 History 重算</div>
:::
::: {.position-card .tools-last}
<div class="position-title"><b>B</b><strong>后置 Tools</strong><code>S + H + T</code></div>
<div class="rounds"><span>R1 · S + H₀ + T</span><span>R2 · S + H₀ + D₁ + T</span><span>旧 T 与新 D₁ 在同一位置分叉</span></div>
<div class="position-good">动态 Tools：变化靠后，可保住更长 History prefix</div>
<div class="position-bad">每轮移动同一段 T：也不是真正 append-only</div>
:::
::::

<table class="position-decision"><thead><tr><th>工作负载</th><th>更合理的策略</th></tr></thead><tbody><tr><td>少量、长期稳定的核心 Tools</td><td>保持前置、顺序和序列化稳定</td></tr><tr><td>大型、频繁变化的 Tool catalog</td><td>固定 meta-tools，JIT discovery；或在 epoch 边界成批切换</td></tr><tr><td>模型已经按固定 Tool 模板训练</td><td>服从 API / chat template；不能只改 Jinja 假设行为等价</td></tr></tbody></table>

<div class="slide-takeaway"><span>WORKLOAD</span><strong>没有永远正确的位置：稳定性、History 长度与训练协议共同决定</strong></div>
````

### 演讲词（TTS）

那么 Tool definitions 应该放在头部还是尾部？如果 Tools 少而稳定，前置布局很漂亮：每一轮只在旧轨迹尾部追加新事件，整个输入持续形成更长的可复用前缀。Tool definitions 也描述整段会话的能力，放在 System 附近有自然的语义理由。但当 Tools 高频变化而 History 很长时，前置会从很早的位置打断 Cache；后置可以保住更多 History prefix。不过每轮把同一段 Tools 移到新的尾部，也不是真正的 append-only，因为上一轮那个位置是 Tools，下一轮却变成新的对话事件。结论不是二选一。少量稳定工具保持前置；大型目录用 meta-tools 和按需发现；确需改变原生 Tools 时，低频、成批并尽量对齐 Context Epoch。最重要的是服从模型训练时的协议，不能只修改 Jinja 就假设后置行为等价。

<!-- slide:cache-shaped-context -->
## 28｜Cache 如何影响 Context 布局

### 主旨

理想逻辑布局是“双端热区、瘦中间”：重要且稳定的信息形成短 Head；仍相关的旧状态压缩在 Middle；当前直接证据追加在 Tail；无关且可重取内容留在 Context 外。

### 展示内容（QMD）

````qmd
## Cache 塑造的 Context {#cache-shaped-context .ideal-context-slide}

<div class="slide-marker"><b>28</b><span>IDEAL CONTEXT</span></div>

:::: {.ideal-layout}
::: {.ideal-zone .head-zone}
<div class="zone-label"><b>HEAD</b><span>重要 · 稳定 · 低频变化</span></div>
<div class="zone-items"><span>Base instructions</span><span>安全 / 输出协议</span><span>稳定 Tool definitions</span><span>项目硬约束</span></div>
<small>开头位置优势 + 最长 Prefix Cache reuse</small>
:::
::: {.ideal-zone .middle-zone}
<div class="zone-label"><b>MIDDLE</b><span>有关 · 较旧 · 应压缩</span></div>
<div class="zone-items"><span>Continuation state</span><span>压缩背景 / 计划</span><span>短 Raw Window</span></div>
<small>最容易受位置效应和干扰影响，所以必须“瘦”</small>
:::
::: {.ideal-zone .tail-zone}
<div class="zone-label"><b>TAIL</b><span>重要 · 当前 · 高频变化</span></div>
<div class="zone-items"><span>Current user request</span><span>JIT retrieval</span><span>最新 Tool Result / Error / Diff</span><span>Generation cursor</span></div>
<small>尾部位置优势；变化只影响短 suffix</small>
:::
::::

<div class="outside-context"><b>OUTSIDE CONTEXT</b><span>完整 History</span><span>大文件 / 完整日志</span><span>过期与无关内容</span><span>Artifacts</span><i>需要时检索 → Tail</i></div>

<div class="epoch-line"><span>稳定 Head</span><b>+</b><span>本 Epoch append-only trajectory</span><b>→</b><strong>Compaction = 有计划的 Cache Break</strong><b>→</b><span>新 Epoch</span></div>

<div class="layout-boundary">逻辑布局必须服从 API、chat template、后训练协议和因果顺序；目标是联合优化正确率、信息利用、Cache reuse、延迟成本与可恢复性。</div>

<div class="slide-takeaway"><span>DESIGN RULE</span><strong>稳定且重要的放头部；当前原始证据放尾部；旧信息压成短中部；无关信息移出去</strong></div>
````

### 演讲词（TTS）

Cache 最终会反过来塑造 Context 布局。考虑到 Lost in the Middle，理想结构可以概括成“双端热区、瘦中间”。头部放重要、稳定、低频变化的信息，例如基础 instructions 和 Tool definitions，同时获得开头位置注意力优势和最长前缀复用。中部只放仍相关但较旧的信息，用 continuation state、压缩背景和短 Raw Window 表示；这里最容易受到 Lost in the Middle 和信息干扰，因此不能成为垃圾场。尾部放最新用户请求、最新 Tool Result 或错误，让最直接的原始证据靠近生成位置，而且变化只影响短 suffix。完整 History、大文件和无关内容留在窗口外，需要时再检索。Compaction 则是一次有计划的 Cache Break：集中重建更短 Context，随后在新 Epoch 继续 append-only。这个布局是逻辑原则，实际顺序仍必须服从 API、模板和模型训练协议。

<!-- slide:memory-recall-paths -->
## 29｜指定信息如何跨越 Compaction

### 主旨

摘要无法保证保留指定细节；可靠跨越 Compaction 的前提，是在窗口外保存不受本次压缩影响的副本，并通过确定性加载、选择性预取或模型检索重新召回。

### 展示内容（QMD）

````qmd
## 指定信息如何跨越 Compaction {#memory-recall-paths .memory-recall-slide}

<div class="slide-marker"><b>29</b><span>RECALL AFTER COMPACTION</span></div>

<div class="recall-source"><small>CONTEXT OUTSIDE</small><strong>不受当前 Compaction 影响的副本</strong><span>文件 · Memory Store · 完整 History · Artifact</span></div>

<div class="recall-warning"><span>“请摘要记住它”</span><b>≠</b><strong>可靠的跨越机制</strong><i>摘要无法稳定保证某个细节一定被保留</i></div>

:::: {.recall-path-grid}
::: {.recall-path .deterministic-path}
<div class="recall-path-head"><b>01</b><strong>Runtime 确定性加载</strong></div>
<div class="recall-lines">
<p>按约定文件、路径条件、scope 或其他固定规则加载。</p>
<p>不依赖语义相关性判断；固定条件满足时保证加载。</p>
</div>
:::
::: {.recall-path .prefetch-path}
<div class="recall-path-head"><b>02</b><strong>Runtime 选择性预取</strong></div>
<div class="recall-lines">
<p>主模型调用前，由 Runtime 的检索或召回机制选择候选。</p>
<p>更节省；预取器未命中时模型完全看不到。</p>
</div>
:::
::: {.recall-path .retrieval-path}
<div class="recall-path-head"><b>03</b><strong>模型发起 Retrieval</strong></div>
<div class="recall-lines">
<p>模型调用文件、Memory 或 History Search Tool。</p>
<p>最灵活；可能“已经忘了，也想不起要检索”。</p>
</div>
:::
::::

<div class="recall-boundary"><b>位置不固定</b><span>三种方式描述谁决定加载与何时加载，不规定最终位于 Head、请求附近还是 Tail</span></div>

<div class="slide-takeaway"><span>RECALL, NOT HOPE</span><strong>跨越 Compact 的不是摘要承诺，而是可以再次召回的窗口外副本</strong></div>
````

### 演讲词（TTS）

Compaction 会用摘要替换旧 Context，但摘要无法保证某个指定细节一定被保留。在提示词中加入“请在摘要中记住这件事”不是可靠机制。要让信息跨越 Compaction，必须在窗口外保留一份不受本次压缩影响的副本，再把它召回。召回有三种主导方式。第一，Runtime 确定性加载，按约定文件、路径条件或其他固定规则加载，不依赖语义相关性判断。第二，Runtime 选择性预取，在主模型调用前由检索或召回机制选择候选，更节省，但可能漏掉。第三，模型主动调用文件、Memory 或 History Search Tool，最灵活，但模型可能已经忘记，所以想不起要检索。

<!-- slide:deterministic-loading -->
## 30｜确定性加载

### 主旨

约定文件能否跨越 Compaction，不只取决于文件存在，而取决于 Runtime 的发现规则、注入位置，以及 Compact 后是否重新加载；不同 Agent 对根规则与路径规则的生命周期并不一致。

### 展示内容（QMD）

````qmd
## 确定性加载：谁负责把规则放回来？ {#deterministic-loading .deterministic-loading-slide}

<div class="slide-marker"><b>30</b><span>DETERMINISTIC LOADING</span></div>

<div class="deterministic-flow"><span>约定文件</span><b>→</b><span>发现顺序 / Scope</span><b>→</b><span>Runtime 注入</span><b>→</b><strong>Compact 后重建</strong></div>

<table class="deterministic-table">
  <thead><tr><th>Agent</th><th>支持的约定文件</th><th>Context 位置与 Compact 后行为</th></tr></thead>
  <tbody>
    <tr><th>Codex</th><td><code>AGENTS.override.md</code> · <code>AGENTS.md</code> · configurable fallbacks</td><td>启动时构造全局到当前目录的 instruction chain；同一 Session 内 Compact 后行为未公开</td></tr>
    <tr><th>Claude Code</th><td><code>CLAUDE.md</code> · <code>.claude/CLAUDE.md</code> · <code>CLAUDE.local.md</code> · <code>.claude/rules/*.md</code></td><td>root / ancestor 位于早期 Project Context，压后重载；nested 规则需再次触达路径</td></tr>
    <tr><th>OpenCode</th><td><code>AGENTS.md</code> · fallback <code>CLAUDE.md</code> · configured instructions</td><td>root 每个普通 step 重读、位于 System；nested 跟随 Read Result，不保证重载</td></tr>
    <tr><th>Gemini CLI</th><td><code>GEMINI.md</code> · configurable <code>context.fileName</code></td><td>global / workspace Context 压后重建；nested 位于 Tool Result，可能只剩摘要</td></tr>
    <tr><th>Cursor</th><td><code>AGENTS.md</code> · <code>.cursor/rules/*.mdc</code></td><td>适用 Rules 位于 Context 开头；公开文档未说明 Compact 后重建边界</td></tr>
    <tr><th>Windsurf / Devin</th><td><code>AGENTS.md</code> / <code>agents.md</code> · <code>.devin/rules/</code> · <code>.windsurf/rules/</code></td><td>root 每条消息提供；子目录规则按 glob 注入；内部 Compact 边界未公开</td></tr>
    <tr><th>Cline</th><td><code>.clinerules/</code> · root <code>AGENTS.md</code> · <code>~/.agents/AGENTS.md</code></td><td>无条件 Rules 位于 System；条件 Rules 按 paths 重新匹配；无 nested AGENTS 证据</td></tr>
    <tr><th>GitHub Copilot</th><td><code>.github/copilot-instructions.md</code> · <code>.github/instructions/*.instructions.md</code> · <code>AGENTS.md</code></td><td>repository / applyTo 规则自动加入请求；准确 role 与 Compact 后恢复未公开</td></tr>
  </tbody>
</table>

:::: {.deterministic-lessons}
<div><b>HEAD</b><span>副本不参与摘要，或由 Runtime 压后重建</span></div>
<div><b>HISTORY</b><span>路径规则进入 Tool Result 后，仍可能只剩摘要</span></div>
<div><b>BOUNDARY</b><span>文件支持、注入位置和 Compact 恢复是三个不同问题</span></div>
::::

<div class="slide-takeaway"><span>FILE ≠ GUARANTEE</span><strong>支持约定文件，不等于其中每份正文都能自动跨越 Compaction</strong></div>
````

### 演讲词（TTS）

最可靠的召回方式是确定性加载。以下是主流agent如何实现的确定性加载的表格。

<!-- slide:progressive-disclosure -->
## 31｜渐进式披露

### 主旨

稳定约定文件最适合作为短小的召回索引：只保留永久规则和“触发条件 → 精确路径”，详细正文按需进入 Tail；直接 import 全文只是文件拆分，并不会节省首轮 Context。

### 展示内容（QMD）

````qmd
## 渐进式披露：稳定入口，按需正文 {#progressive-disclosure .progressive-disclosure-slide}

<div class="slide-marker"><b>31</b><span>PROGRESSIVE DISCLOSURE</span></div>

:::: {.disclosure-stage}
::: {.root-index-card}
<div class="index-head"><b>ROOT INDEX</b><span>始终进入 Head</span></div>
<div class="index-rule"><small>ALWAYS</small><strong>修改代码后运行相关测试</strong></div>
<div class="index-rule"><small>WHEN</small><strong>数据库 schema → 读 <code>docs/agent/database.md</code></strong></div>
<div class="index-rule"><small>WHEN</small><strong>鉴权 / 权限 → 读 <code>docs/agent/security.md</code></strong></div>
<div class="index-rule"><small>WHEN</small><strong>发布 / 回滚 → 读 <code>docs/agent/operations.md</code></strong></div>
:::
<div class="disclosure-arrow"><span>任务命中条件</span><b>→</b><span>Read Tool</span><b>→</b></div>
::: {.on-demand-docs}
<div class="doc-card muted"><b>database.md</b><span>窗口外</span></div>
<div class="doc-card active"><b>security.md</b><span>按需读取 → Tail</span></div>
<div class="doc-card muted"><b>operations.md</b><span>窗口外</span></div>
:::
::::

:::: {.disclosure-modes}
<div class="not-progressive"><b>@file import</b><span>加载时立即展开全文</span><small>不节省首轮 Context</small></div>
<div><b>path / glob / decision</b><span>Runtime 判断并注入</span><small>选择性预取</small></div>
<div><b>when → read path</b><span>模型命中后调用 Tool</span><small>模型发起 Retrieval</small></div>
::::

<div class="disclosure-cycle"><span>Compact 后索引重新出现</span><b>→</b><span>仍能再次发现路径</span><b>→</b><strong>正文需要时重新读取</strong></div>

<div class="slide-takeaway"><span>SHORT INDEX</span><strong>索引同时写清触发条件与路径；详细知识留在窗口外</strong></div>
````

### 演讲词（TTS）

确定性加载虽然可靠，但把所有知识都放进约定文件，会持续占用 Context。更好的办法是渐进式披露：Head 中只放短小、稳定、可发现的索引，任务命中条件后再读取正文。内容以后仍可能被 Compact，但条件再次达到时，模型会再次加载。这里要区分三种写法。file import 在加载时直接展开全文，只是文件组织，不节省首轮 Context。Runtime选择性预取指在调用模型前，由规则驱动agent加载内容。索引里写“什么时候读哪个文件”，则是模型Retrieval。稳定入口常驻，详细正文按需进入。

<!-- slide:memory-alternatives -->
## 32｜其他方案对比

### 主旨

Memory 方案仍按确定性加载、Runtime 选择性预取和模型发起 Retrieval 分类；分类依据是一次具体召回由谁决定，而不是产品或存储形态。

### 展示内容（QMD）

````qmd
## 其他 Memory 方案：谁决定召回？ {#memory-alternatives .memory-alternatives-slide}

<div class="slide-marker"><b>32</b><span>MEMORY LANDSCAPE</span></div>

<div class="memory-group-grid">
<div class="memory-group deterministic-group">
<header><b>01</b><strong>Runtime 确定性加载</strong></header>
<div class="memory-group-product"><b>Letta</b><p>挂载的 Memory Blocks 每轮重新进入 Context；模型还可另行调用 Recall。</p></div>
<small>固定条件满足即加载，不依赖语义相关性判断</small>
</div>

<div class="memory-group prefetch-group">
<header><b>02</b><strong>Runtime 选择性预取</strong></header>
<div class="memory-group-product"><b>Mem0</b><p>接入方可在主模型调用前执行 search 并注入命中项。</p></div>
<div class="memory-group-product"><b>Zep</b><p>接入方可在调用前获取组装好的 Context Block。</p></div>
<div class="memory-group-product"><b>Supermemory</b><p>Wrapper 可先搜索相关 Memory，再自动加入请求。</p></div>
<small>这里特指主模型调用前已经完成的选择与注入</small>
</div>

<div class="memory-group retrieval-group">
<header><b>03</b><strong>模型发起 Retrieval</strong></header>
<div class="memory-group-product"><b>Claude Code Auto Memory</b><p>Runtime 重载索引，模型按需读取 topic 文件。</p></div>
<div class="memory-group-product"><b>Gemini CLI Project Memory</b><p>Runtime 重建索引，模型按需读取详细文件。</p></div>
<div class="memory-group-product"><b>Cline Memory Bank</b><p>Rules 提醒模型读取与当前任务相关的 Markdown。</p></div>
<small>索引可确定性恢复；正文是否读取仍由模型决定</small>
</div>

<div class="memory-group unknown-group">
<header><b>?</b><strong>自动召回，机制未公开</strong></header>
<div class="memory-group-product"><b>Codex Local Memories</b><p>可注入未来 Session；候选选择机制未公开。</p></div>
<div class="memory-group-product"><b>Windsurf Memories</b><p>会自动召回相关 Memory；选择机制未公开。</p></div>
<div class="memory-group-product"><b>GitHub Copilot Memory</b><p>会召回并验证相关事实；选择机制未公开。</p></div>
<div class="memory-group-product"><b>Devin Knowledge</b><p>按 Trigger 自动召回；判断发生位置未公开。</p></div>
</div>
</div>

<div class="memory-boundaries"><span>共 11 个具体实现</span><span>按主要召回路径归栏；混合能力写在产品说明中</span></div>

<div class="slide-takeaway"><span>PERSISTED ≠ VISIBLE</span><strong>Store 中保存着，不等于下一次模型调用一定看得见</strong></div>
````

### 演讲词（TTS）

本页列出了其他常见方案的实现方式，同样按照“确定性加载”，“选择性预取”，和“模型召回”分为三类。对于机制未公开的，列为“未公开”。

<!-- slide:skill-definition -->
## 33｜Skill 的作用和定义

### 主旨

Skill 是可按需加载的 instructions、references、scripts 和 assets 包，不是 Tool，也不会自行执行；短 metadata 构成稳定 Catalog，完整正文只在命中后进入 Context。

### 展示内容（QMD）

````qmd
## Skill：Catalog 常驻，正文按需进入 {#skill-definition .skill-definition-slide}

<div class="slide-marker"><b>33</b><span>SKILL LIFECYCLE</span></div>

<div class="skill-definition"><b>SKILL</b><strong>instructions + references + scripts + assets</strong><span>不是 Tool · 不会自行执行</span></div>

:::: {.skill-two-lanes}
::: {.skill-lane .catalog-lane}
<div class="skill-lane-head"><b>METADATA</b><strong>Skill Catalog</strong><span>短 · 稳定 · 可发现</span></div>
<div class="catalog-fields"><code>name</code><code>description</code><code>path</code></div>
<div class="skill-timing"><span>Session 重启</span><b>+</b><span>Compact 后重建</span><b>→</b><strong>Runtime 确定性加载到 Head</strong></div>
<p>告诉模型：有哪些 Skill、何时值得加载、从哪里加载。</p>
:::
::: {.skill-lane .body-lane}
<div class="skill-lane-head"><b>BODY</b><strong>SKILL.md</strong><span>完整 · 专用 · 按需</span></div>
<div class="skill-outside"><span>默认位于 Context Outside</span><b>用户指定 / 模型按 description 选择</b></div>
<div class="skill-activation"><span>激活</span><b>→</b><strong>正文进入 Conversation / Tool Result</strong></div>
<p>references 继续按需读取；scripts 由 Runtime 或 Tool 执行。</p>
:::
::::

<div class="skill-lifecycle"><span>Catalog 仍在</span><b>≠</b><span>正文仍在 Context</span><i>正文进入 History 后可能被摘要；需要时可重新激活</i></div>

<div class="skill-boundary">具体 API role、去重和正文压后恢复由 Runtime 决定；Catalog 与正文必须分开讨论。</div>

<div class="slide-takeaway"><span>DISCOVER → ACTIVATE</span><strong>Metadata 负责“找到并选择”；正文负责“具体怎么做”</strong></div>
````

### 演讲词（TTS）

Skill 是一组可以按需加载的指令，脚本，数据和资源。它不是 Tool，也不会自行执行。Skill 有两个完全不同的部分。第一部分是 metadata，包括 name、description 和 path。Runtime 把它们组成短小的 Catalog，在 Session 重启和 Compact 后重建 Context 时确定性加载到 Head。Metadata 只告诉模型有哪些 Skill、什么时候值得使用，以及去哪里加载。第二部分是完整正文，也就是 SKILL 点 M D。正文默认留在窗口外，只有用户明确指定，或者模型根据 description 选中 Skill 后才加载进 Conversation 或 Tool Result。references 继续按需读取，scripts 则由 Runtime 或 Tool 执行。Metadata 负责找到和选择，正文负责具体怎么做。

<!-- slide:skill-implementations -->
## 34｜主流 Agent 的 Skill 实现对照

### 主旨

主流 Agent 都采用“Catalog 先进入、正文按需加载”，但正文进入 Context 的位置、重复激活和 Compact 后恢复方式并不统一。

### 展示内容（QMD）

````qmd
## 主流 Agent 的 Skill 实现对照 {#skill-implementations .skill-implementations-slide}

<div class="slide-marker"><b>34</b><span>SKILL IMPLEMENTATIONS</span></div>

<div class="skill-impl-table">
<div class="skill-impl-row skill-impl-head"><b>Agent</b><b>Catalog 位置</b><b>激活后的正文</b><b>重复激活</b><b>Compact 后恢复</b></div>
<div class="skill-impl-row"><strong>Codex</strong><span>初始 Context<br><i>role 未公开</i></span><span>未公开</span><span>未公开</span><span>未公开</span></div>
<div class="skill-impl-row"><strong>Claude Code</strong><span>早期 Context<br>+ Skill Tool</span><span>Conversation message</span><span>相同正文仅加短提示</span><span class="positive">自动重挂载<br><i>单项 5k / 合计 25k</i></span></div>
<div class="skill-impl-row"><strong>Gemini CLI</strong><span>System Prompt</span><span><code>activate_skill</code><br>Tool Result</span><span>可重复</span><span>未发现专用恢复</span></div>
<div class="skill-impl-row"><strong>GitHub Copilot CLI</strong><span>Agent Context<br><i>位置未公开</i></span><span>Agent Context<br><i>role 未公开</i></span><span>未公开</span><span>未公开</span></div>
<div class="skill-impl-row"><strong>OpenCode</strong><span>System<br><code>&lt;available_skills&gt;</code></span><span><code>skill</code> Tool Result</span><span>可重复</span><span>随 History 压缩<br>不自动重载</span></div>
<div class="skill-impl-row"><strong>OpenHands</strong><span>前部<br><code>&lt;available_skills&gt;</code></span><span><code>invoke_skill</code><br>Tool Result</span><span>可重复</span><span>未发现正文恢复</span></div>
<div class="skill-impl-row"><strong>Cursor</strong><span>启动时发现<br><i>位置未公开</i></span><span>附着到一条 message</span><span>未公开</span><span>未公开</span></div>
</div>

<div class="skill-impl-notes"><span><b>共同点</b> Catalog 先进入，正文命中后才加载</span><span><b>关键差异</b> 正文进入哪里，以及 Compact 后是否恢复</span></div>

<div class="slide-takeaway"><span>DISCOVERY IS SHARED</span><strong>支持 Skill，不代表正文拥有相同的 Context 生命周期</strong></div>
````

### 演讲词（TTS）

以下是主流agent如何加载和保留skill的列表。重复激活指由人类或模型，对一个已经加载过的skill做二次加载，是否会在context里保留两份内容。Compact后恢复，指skill的指令正文，在Compact后是否会自动恢复。如果不能自动恢复，可能需要模型选择再次加载。

<!-- slide:subagent-context-isolation -->
## 35｜Subagent

### 主旨

Subagent 是由主 Agent 委派、拥有独立 Context 与 Agent Loop 的 Agent Session；模型提出委派，Runtime 负责启动和调度，完成结果再回到主 Agent。

### 展示内容（QMD）

````qmd
## Subagent {#subagent-context-isolation .subagent-concept-slide}

<div class="slide-marker"><b>35</b><span>CONTEXT ISOLATION</span></div>

<div class="subagent-definition"><b>SUBAGENT</b><strong>独立 Agent Session</strong><span>自己的 Current Context · History · Tools · Agent Loop</span></div>

<div class="subagent-mechanism"><span><b>模型</b>发出 Agent / Task Tool Call</span><strong>→</strong><span><b>Runtime</b>启动并调度独立 Session</span><strong>→</strong><span><b>结果</b>作为 Tool Result 返回</span></div>

```{=html}
<svg class="subagent-sequence" viewBox="0 0 1420 420" role="img" aria-label="主 Agent 依次启动两个 Subagent，先启动的 Subagent 先完成">
<defs>
<marker id="subagent-arrowhead" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0,0 L10,4 L0,8 Z"></path></marker>
</defs>
<text class="sequence-time" x="1280" y="28">TIME →</text>

<text class="sequence-actor main-actor" x="18" y="91">主 Agent</text>
<line class="sequence-line main-line" x1="170" y1="84" x2="1385" y2="84"></line>

<text class="sequence-actor" x="18" y="223">Subagent 1</text>
<line class="sequence-line" x1="170" y1="216" x2="1385" y2="216"></line>
<rect class="sequence-run run-one" x="322" y="201" width="560" height="30" rx="15"></rect>
<text class="sequence-run-label" x="602" y="221">独立 Agent Loop · PRIVATE CONTEXT</text>

<text class="sequence-actor" x="18" y="355">Subagent 2</text>
<line class="sequence-line" x1="170" y1="348" x2="1385" y2="348"></line>
<rect class="sequence-run run-two" x="574" y="333" width="586" height="30" rx="15"></rect>
<text class="sequence-run-label" x="867" y="353">独立 Agent Loop · PRIVATE CONTEXT</text>

<line class="sequence-message start-message" x1="250" y1="84" x2="322" y2="201" marker-end="url(#subagent-arrowhead)"></line>
<text class="sequence-step" x="210" y="126">① 启动 S1</text>
<text class="sequence-packet" x="260" y="151">Task Packet</text>

<line class="sequence-message start-message" x1="500" y1="84" x2="574" y2="333" marker-end="url(#subagent-arrowhead)"></line>
<text class="sequence-step" x="460" y="126">② 启动 S2</text>
<text class="sequence-packet" x="500" y="151">Task Packet</text>

<line class="sequence-message return-message" x1="882" y1="201" x2="950" y2="84" marker-end="url(#subagent-arrowhead)"></line>
<text class="sequence-step" x="850" y="126">③ S1 完成</text>
<text class="sequence-packet" x="837" y="151">Evidence Packet</text>

<line class="sequence-message return-message" x1="1160" y1="333" x2="1235" y2="84" marker-end="url(#subagent-arrowhead)"></line>
<text class="sequence-step" x="1160" y="126">④ S2 完成</text>
<text class="sequence-packet" x="1147" y="151">Evidence Packet</text>
</svg>
```

<div class="slide-takeaway"><span>DELEGATE → RUN → RETURN</span><strong>主 Agent 负责委派与综合；每个 Subagent 独立完成自己的 Agent Loop</strong></div>
````

### 演讲词（TTS）

Subagent 是由主 Agent 委派、拥有独立 Context 和 Agent Loop 的 Agent Session。图中时间从左向右。主 Agent 先通过 Task 类 Tool 启动 Subagent 一，再启动 Subagent 二。Runtime 根据各自的 Task Packet 创建并调度两个独立 Session；它们分别调用模型和 Tools，彼此不共享中间轨迹。先启动的一号先完成，把结论和证据返回；随后二号返回。主 Agent 收到结果后统一验证和综合。模型负责提出委派，Runtime 负责真正的 Session 管理。

<!-- slide:subagent-three-uses -->
## 36｜Subagent 的三类用法

### 主旨

Subagent 的价值来自三种不同目标：隔离大量局部细节、并发减少 Wall-clock Time，以及构造真正互相不可见的独立任务。

### 展示内容（QMD）

````qmd
## Subagent 的三类用法 {#subagent-three-uses .subagent-uses-slide}

<div class="slide-marker"><b>36</b><span>THREE USE CASES</span></div>

<div class="subagent-use-grid">
<div class="subagent-use-card detail-use">
<header><b>01</b><strong>隔离大量细节</strong></header>
<div class="use-diagram"><span>Task Packet</span><b>→</b><span>Worker</span><b>→</b><span>Evidence Packet</span></div>
<p>网页正文、日志、搜索过程和失败重试停留在 Worker；主 Context 只保留结论与证据指针。</p>
<small>成立条件：Worker 内部信息 ≫ 跨边界返回信息</small>
</div>

<div class="subagent-use-card parallel-use">
<header><b>02</b><strong>并发缩短经过时间</strong></header>
<div class="parallel-agents"><span>Worker A</span><span>Worker B</span><span>Worker C</span></div>
<div class="time-equation"><code>并发时间 ≈ max(T₁,T₂,T₃) + 协调开销</code></div>
<p>适合互相独立的模型任务；会减少 Wall-clock Time，但通常增加总 Token 与计算成本。</p>
<small>同一 Context 内的独立 I/O，优先 Parallel Tool Calls</small>
</div>

<div class="subagent-use-card blind-use">
<header><b>03</b><strong>隔离“不应知道彼此”</strong></header>
<div class="blind-branches"><span>Code Agent<br>实现</span><b>SPEC</b><span>Test Agent<br>独立测试</span></div>
<p>双方共享规格和验收条件，但初次工作时不读取对方 trajectory；Coordinator 最后合并验证。</p>
<small>必须用 Context、snapshot 或 worktree 隔离，不能只说“请假装没看见”</small>
</div>
</div>

<div class="subagent-use-rule"><b>先问隔离边界，再决定 Agent 数量</b><span>Tool Call 多，不等于需要更多 Subagent</span></div>

<div class="slide-takeaway"><span>ISOLATE · PARALLELIZE · BLIND</span><strong>三类收益不同，不能用“多开几个 Agent”一概而论</strong></div>
````

### 演讲词（TTS）

Subagent 有三类主要用法。第一，隔离具体任务产生的大量细节。网页正文、日志和失败重试留在 Worker，主 Agent 只接收较短的 Evidence Packet。只有内部信息远大于返回信息时，这种隔离才有价值。第二，并发缩短实际经过时间。多个独立 Agent Loop 可以同时推理和调用工具，完成时间接近最慢任务加协调开销；但总 Token 和计算成本通常会上升。同一 Context 内只有工具执行需要并行时，优先使用 Parallel Tool Calls。第三，隔离不应知道彼此的任务，例如 Code Agent 与 Test Agent 独立工作，最后由 Coordinator 验证。对于后两种情况，由于多个agent天然缺乏协调机制，调度设计不慎很可能出现互相冲突。此时需要多种隔离技术来辅助，例如git worktree。

<!-- slide:subagent-startup-cost -->
## 37｜启动方式与成本

### 主旨

Subagent 首次启动可归纳为 Fork、Fresh 和 Persistent Specialist；Resume 是叠加在任一种首次启动方式上的续跑能力。四者的 Context 来源、System Prompt 控制方式和成本不同。

### 展示内容（QMD）

````qmd
## Subagent：启动方式与成本 {#subagent-startup-cost .subagent-startup-slide}

<div class="slide-marker"><b>37</b><span>STARTUP &amp; COST</span></div>

<div class="startup-table">
<div class="startup-row startup-head"><b>形态</b><b>Context 从哪里开始</b><b>与主 History 的关系</b><b>System Prompt 是否可控</b><b>常见 Agent / 实现</b><b>主要成本 / 风险</b></div>
<div class="startup-row fork-row"><strong>Fork</strong><span>复制分叉点的完整<br><b>Current Context</b></span><span>History 从此分叉<br>两边独立继续</span><span><b>通常继承</b>主 Session<br>可追加 Worker 约束</span><span class="agent-examples"><i>Claude Code</i></span><span>状态管理复杂<br>无关信息也被复制</span></div>
<div class="startup-row fresh-row"><strong>Fresh</strong><span>稳定 Instructions<br>+ Task Packet</span><span>不继承主 History<br>任务描述负责交接</span><span><b>由 Runtime 构造</b><br>不一定对用户开放</span><span class="agent-examples"><i>Claude Code 默认</i><i>Cursor</i><i>Gemini CLI</i><i>Cline</i><i>OpenCode</i><i>Copilot CLI</i></span><span>实现最简单<br>主 Agent 要生成完整任务包</span></div>
<div class="startup-row specialist-row"><strong>Persistent<br>Specialist</strong><span>Fresh Context<br>+ 固定 Agent Profile</span><span>通常不继承主 History<br>只接收短任务</span><span class="prompt-control"><b>明确可控</b><br>独立 Prompt / Tools / 权限</span><span class="agent-examples"><i>Claude Code</i><i>Gemini CLI</i><i>OpenCode</i><i>Copilot CLI</i><i>Codex Custom Agents</i></span><span>重复背景成本更低<br>需治理陈旧配置或 Memory</span></div>
</div>

<div class="resume-lane">
<div><b>RESUME</b><strong>在原 Worker Session 上继续追加指令</strong></div>
<span>首次可以来自 Fork / Fresh / Specialist</span>
<i>保留 Worker History · 减少重复交接 · 也会继续消耗 Context Window</i>
</div>

<div class="startup-cost-equation"><span>额外成本</span><b>=</b><code>Task Packet</code><b>+</b><code>Worker Tool Loop</code><b>+</b><code>Evidence Packet</code><b>+</b><code>主 Agent 验证</code></div>

<div class="slide-takeaway"><span>START ≠ CONTINUE</span><strong>Fork / Fresh 决定从哪里开始；Resume 决定能否从原 Worker 继续</strong></div>
````

### 演讲词（TTS）

三种形态是能力分类，同一个产品可能支持多种。Fork 复制分叉点的 Current Context，Subagent可能复用主Agent的Cache。Fresh 只接收稳定 Instructions 和 Task Packet，是目前最常见的默认方式；代价是主 Agent 必须重新讲清任务，会产生大量output。Persistent Specialist 是带固定 Agent Profile 的 Fresh置；它的 Prompt、Tools 和权限可以独立控制。Resume 则是续跑能力：只要保存了 Worker Session，就能继续在原 History 上追加指令，但 Context 也会继续增长。

<!-- slide:opencode-qwen-context -->
## 38｜OpenCode 调用 Qwen3 的真实 Context

### 主旨

OpenCode 调用 Qwen3 时，模型可见 Context 由请求中的 System Prompt、Qwen 模板插入的 Tools、History 消息序列和 Assistant generation cursor 四部分组成。

### 展示内容（QMD）

````qmd
## OpenCode调用Qwen3的真实Context {#opencode-qwen-context .opencode-context-slide}

<div class="slide-marker"><b>38</b><span>REAL CONTEXT · OPENCODE 1.18.21</span></div>

<div class="real-context-layout">
<div class="real-context-stack">
<div class="context-table-group system-prompt-group">
<strong>System Prompt<br><small>请求发送</small></strong>
<div><span>OpenCode default base prompt</span><span>Environment</span><span>Project / parent <code>AGENTS.md</code></span><span>Skill Catalog</span></div>
</div>
<div class="context-table-group qwen-template-group">
<strong>Qwen Template<br><small>模板插入</small></strong>
<div><span>10 Tool definitions</span><span>Qwen Tool Call protocol</span></div>
</div>
<div class="context-table-group history-sequence-group">
<strong>History<br><small>消息序列</small></strong>
<div class="history-sequence"><span><b>USER · U1</b> Calculate the requested expression…</span><span><b>ASSISTANT · A1</b> The result is…</span><i>⋮</i><span><b>USER · Uₙ</b> Current request…</span></div>
</div>
<div class="context-table-group generation-cursor-group">
<strong>Model</strong>
<div><span>Assistant generation cursor</span></div>
</div>
</div>

<div class="real-context-color-legend">
<div class="system-legend"><b>SYSTEM PROMPT</b><span>请求中发送的 System Prompt</span></div>
<div class="template-legend"><b>QWEN TEMPLATE</b><span>模板插入的 Tools 定义与调用协议。注意，也以 System role 插入和提交</span></div>
<div class="history-legend"><b>HISTORY</b><span>按 User / Assistant 顺序构造的消息序列</span></div>
<div class="cursor-legend"><b>CURSOR</b><span>模型开始生成下一个 Assistant message</span></div>
</div>
</div>

<div class="slide-takeaway"><span>PAYLOAD → TEMPLATE → CONTEXT</span><strong>API 字段的边界，不等于模型最终看到的边界</strong></div>
````

### 演讲词（TTS）

这是 OpenCode 调用 Qwen3 时，模型真正接收的 Context 结构。绿色是请求中发送的 System Prompt，包括基础 Prompt、环境、项目规则和 Skill Catalog。红色是 Qwen 模板插入的 Tool definitions 和 Tool Call 协议；注意，这些内容同样以 System role 插入和提交。黄色是 History 按 User、Assistant 顺序形成的消息序列。最后的黑色区域是 Assistant generation cursor，模型从这里开始生成下一条回复。

<!-- slide:opencode-compaction-context -->
## 39｜OpenCode 在 Compaction 前后的 Context

### 主旨

OpenCode Compact 不是在原 Context 上原地删短，而是先构造一次无 Tools 的独立摘要请求，再重建普通 Head，并用摘要与可选 raw tail 开启新的 Context epoch。

### 展示内容（QMD）

````qmd
## OpenCode在Compaction前后的Context {#opencode-compaction-context .opencode-compaction-slide}

<div class="slide-marker"><b>39</b><span>CONTEXT RECONSTRUCTION</span></div>

<div class="compact-context-flow">
<div class="compact-context-column before-context">
<header><b>BEFORE COMPACT · n=4</b><strong>普通 Context</strong></header>
<div class="compact-stack-group compact-system-group"><b>SYSTEM PROMPT</b><div><span>OpenCode default base prompt</span><span>Environment</span><span>Project / parent <code>AGENTS.md</code></span><span>Skill Catalog</span></div></div>
<div class="compact-stack-group compact-template-group"><b>QWEN TEMPLATE</b><div><span>10 Tool definitions</span><span>Qwen Tool Call protocol</span></div></div>
<div class="compact-stack-group compact-history-group"><b>HISTORY</b><div><span>User U1</span><span>Assistant · Tool Call</span><span>Tool Result · 完整 SKILL.md</span><span>Assistant · Tool Call</span><span>Tool Result · command not found</span><span>Assistant 阶段回答 · User U2</span></div></div>
<div class="compact-stack-group compact-cursor-group"><b>MODEL</b><div><span>Assistant generation cursor</span></div></div>
</div>

<div class="compact-context-column summary-context">
<header><b>COMPACTION · n=5</b><strong>摘要 Context</strong><code>tools = []</code></header>
<div class="compact-stack-group compact-system-group"><b>SYSTEM PROMPT</b><div><span>Compaction Agent system prompt</span></div></div>
<div class="compact-stack-group compact-history-group summary-transcript-group"><b>USER REQUEST</b><div><span>Here is the conversation so far:</span><span>旧事件 transcript</span><span>Summary 输出要求</span></div></div>
<div class="compact-stack-group compact-cursor-group"><b>MODEL</b><div><span>Assistant generation cursor</span></div></div>
</div>

<div class="compact-context-column after-context">
<header><b>AFTER COMPACT · n=6</b><strong>新 Context Epoch</strong></header>
<div class="compact-stack-group compact-system-group"><b>SYSTEM PROMPT</b><div><span>OpenCode default base prompt</span><span>Environment</span><span>Project / parent <code>AGENTS.md</code></span><span>Skill Catalog</span></div></div>
<div class="compact-stack-group compact-template-group"><b>QWEN TEMPLATE</b><div><span>10 Tool definitions</span><span>Qwen Tool Call protocol</span></div></div>
<div class="compact-stack-group compact-history-group"><b>HISTORY</b><div><span>User · What did we do so far?</span><span>Assistant · Generated History Abstract</span><span>Raw tail · User U2</span><span>Raw tail · Assistant answer</span><span>User · Continue…</span></div></div>
<div class="compact-stack-group compact-cursor-group"><b>MODEL</b><div><span>Assistant generation cursor</span></div></div>
</div>
</div>

<div class="slide-takeaway"><span>SUMMARIZE → REBUILD</span><strong>Compact 产生摘要；下一次调用用摘要重建模型可见 Context</strong></div>
````

### 演讲词（TTS）

OpenCode 的 Compaction 不是把原 Context 原地删短。Compact 前，普通 Context 包含稳定 Head 和完整事件。触发压缩后，Runtime 先发起一次独立摘要请求：专用 Prompt 加旧事件 transcript，并且不提供 Tools。摘要完成后，下一次普通调用重新构造 Head、Catalog 和 Tools，再接 marker、生成的 History Abstract，以及预算允许时保留的 raw tail。旧 History 没有被覆盖，变化的是模型下一次看到的 Context。

<!-- slide:agent-futures -->
## 40｜我对 Agent 未来方向的四个预测

### 主旨

Agent 将从单机工具演进为中心化基础设施与稳定的 Agent 组合；模型适配、知识系统和 Context 管理也会逐步围绕 Agent Loop 重构。

### 展示内容（QMD）

````qmd
## 我对Agent未来方向的四个预测 {#agent-futures .agent-futures-slide}

<div class="slide-marker"><b>40</b><span>WHAT COMES NEXT</span></div>

<div class="future-grid">
<div class="future-card infrastructure-future">
<header><b>01 · MOST CERTAIN</b><strong>中心化 Agent 系统成为独立基础设施</strong></header>
<p>核心价值是操作全程可审计、权限能够统一配置。Agent 如果只留在个人机器上，很难实现组织级治理。</p>
<div class="future-mini-flow"><span>统一权限</span><b>→</b><span>受控执行</span><b>→</b><span>完整审计记录</span></div>
</div>

<div class="future-card profile-future">
<header><b>02 · COMPOSITION</b><strong>从单一通用 Agent 走向稳定 Agent 组合</strong></header>
<div class="agent-profile-equation"><code>Agent</code><b>=</b><span>Model</span><b>+</b><span>Prompt</span><b>+</b><span>Tools</span><b>+</b><span>Skills</span><b>+</b><span>权限集</span></div>
<p>平台维护多个用途明确、配置稳定的 Agent，由任务决定调用哪个组合。</p>
</div>

<div class="future-card alignment-future">
<header><b>03 · CO-DESIGN</b><strong>Agent 与模型共同适配</strong></header>
<p>Tools、Skills 等新设施需要进入后训练；不同模型对 Prompt、位置和协议的偏好不同，Agent 将维护模型专属 Adapter。</p>
<div class="future-tags"><span>POST-TRAINING</span><span>RENDERER</span><span>PARSER</span><span>POLICY</span></div>
</div>

<div class="future-card context-future">
<header><b>04 · EMERGING</b><strong>知识、History 与 Context 分层治理</strong></header>
<p><b>现实基础：</b>可管理知识库与可搜索 History。<br><b>下一步：</b>模型提出保留、丢弃与召回建议，Runtime 验证后管理 Context。</p>
<div class="future-mini-flow"><span>Knowledge</span><span>Searchable History</span><span>Managed Context</span></div>
</div>
</div>

<div class="slide-takeaway"><span>STATE · PROFILE · PROTOCOL · CONTEXT</span><strong>未来的 Agent 能力，越来越来自系统，而不只来自单次模型调用</strong></div>
````

### 演讲词（TTS）

最后提出四个预测。第一个预测是，中心化 Agent 系统会成为独立基础设施。它的核心价值是操作可审计、权限可统一配置；Agent 如果只留在个人机器上，很难实现组织级治理。第二，平台会从单一通用 Agent 走向稳定的 Agent 组合：特定模型、Prompt、Tools、Skills 和权限集，共同定义一个 Agent。第三，新的 Agent 设施需要模型在后训练阶段学会使用。不同模型对 Prompt、Tools、Skills 的位置和协议可能有不同偏好，因此 Agent 平台会像推理框架一样，为不同模型维护专属 Adapter。第四，知识库、可搜索 History 与模型可管理的 Context 会形成分层系统。

<!-- slide:closing-qa -->
## 尾页｜感谢与 Q&A

### 主旨

感谢听众与现场辅助回答的 Agent，把最后的交流留给 Agent 尚未回答的问题，以及更适合由现场人类共同讨论的问题。

### 展示内容（QMD）

````qmd
## 感谢 · Q&A {#closing-qa .closing-slide}

<div class="slide-marker"><b>41</b><span>HUMAN ↔ AGENT ↔ HUMAN</span></div>

<div class="closing-stage">
<div class="closing-thanks">
<span>THANK YOU</span>
<strong>感谢各位的听讲</strong>
<p>也感谢各位 Agent 的辅助回答</p>
</div>

<div class="closing-questions">
<article class="closing-question agent-question"><small>01 · ASK THE ROOM</small><strong>还有没有 Agent<br>无法回答的问题？</strong></article>
<article class="closing-question human-question"><small>02 · TALK TO PEOPLE</small><strong>有没有希望和现场其他人<br>一起交流的问题？</strong></article>
</div>
</div>

<div class="closing-footer"><span>Q&amp;A</span><strong>把最后一轮留给现场</strong></div>
````

### 演讲词（TTS）

感谢各位的听讲，也感谢各位 Agent 在演讲过程中辅助回答。最后把问题交还给现场：还有没有您的 Agent 无法回答的问题？或者有没有您更希望和现场其他人一起交流的问题？谢谢大家。
