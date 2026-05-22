# Agentic Orchestration Demo — smolagents + Claude Sonnet

A minimal two-tool agent demonstrating LLM-driven orchestration: the model writes code, executes it, observes output, replans across failures, and chains tool calls — without any procedural control flow in the implementation.

## What This Demonstrates

The structural shift from *"procedural code that calls an LLM"* to *"LLM that sequences calls to your tools."*

Query issued: `"Find the country ranked #3 by GDP. Then look up its capital."`

No join logic. No ranking loop. No relational query in the implementation. The LLM sequences tool calls, observes intermediate output, and replans when a call fails or returns unexpected results.

## Tools

| Tool | Input | Output |
|------|-------|--------|
| `get_country_gdp_rank(country: str)` | Country name | GDP rank + approximate value (2024 IMF) |
| `get_country_capital(country: str)` | Country name | Capital city |

Both tools are deterministic lookups backed by hardcoded dictionaries. No fuzzy matching, no LLM inside the tool.

## Execution Trace

| Step | Agent Action | Outcome |
|------|-------------|---------|
| 1 | `get_country_gdp_rank("3")` | **Fail** — tool expects a country name, not a rank integer |
| 2 | `web_search("country ranked #3 by GDP")` | **Blocked** — tool not registered in agent scope |
| 3 | Loop over `["Japan", "Germany", "India"]` | Germany → rank #3 confirmed via tool |
| 4 | `get_country_capital("Germany")` | **Berlin ✓** |

**Step 3 is where replanning is visible.** After two dead ends, the agent shifted strategy: it enumerated candidate countries and verified each via tool call until rank #3 was confirmed. No developer-written fallback logic triggered this. The LLM replanned based on what the previous observations ruled out.

**One caveat worth noting:** the candidate list in Step 3 (`["Japan", "Germany", "India"]`) came from the LLM's parametric knowledge (training data), not from a registered tool. The tool call *verified* the guess — it didn't *produce* it. In a production system, stale or incorrect parametric knowledge here would cause a silent wrong answer. If correctness depends on current data, the tool set needs to cover the full retrieval path — world-knowledge shortcuts are a reliability risk, not a feature.

## Execution Pattern

This is a **ReAct loop** (Reason → Act → Observe → repeat):

```
Thought:  What do I need to do next?
Code:     [Python snippet using available tools]
Observe:  [Tool output or error]
→ repeat until final_answer()
```

smolagents surfaces this loop explicitly. Every step — including failures — is logged with token counts, generated code, and observations.

## Stack

| Component | Choice |
|-----------|--------|
| Agent framework | [smolagents](https://github.com/huggingface/smolagents) (Hugging Face) |
| Primary model | `claude-sonnet-4-20250514` via LiteLLM |
| Fallback model | `Qwen/Qwen2.5-Coder-32B-Instruct` (HF Inference, no API key required) |
| Session logging | Custom `SessionLogger` with step callbacks |

## Setup

```bash
pip install smolagents litellm anthropic
export ANTHROPIC_API_KEY=your_key_here
python agent_demo.py
```

Omit the `ANTHROPIC_API_KEY` export to run on the Qwen fallback via Hugging Face Inference API (free tier).

## Key Distinction

Most "agentic" workflows are procedural code with LLM calls inserted at decision points. The developer controls the call sequence; the LLM answers questions within it. Change the requirements and you rewrite the orchestration logic.

True agent orchestration inverts the sequencing responsibility: the developer registers tools and defines their contracts; the LLM decides which tool to call next, with what arguments, and whether the current result is sufficient to stop. The execution plan is generated dynamically at each step, not hardcoded ahead of time.

The difference is observable in the trace — look for step-level replanning when a tool returns unexpected output. A procedurally-driven system follows a fixed call sequence regardless of intermediate results. An LLM-orchestrated system can replan remaining steps based on what each observation rules out.

Note the constraint: the LLM sequences within an envelope the framework enforces. In this demo, `web_search` was available to the LLM as a concept but blocked by the agent's tool registry — the framework, not the LLM, made that call. And if the LLM replans using its own parametric knowledge rather than registered tools, that's a contract violation. Well-designed tool sets should make parametric shortcuts unnecessary.

---

> Bad tools make agents guess. Good tools make agents orchestrate.