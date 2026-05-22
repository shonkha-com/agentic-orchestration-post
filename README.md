# Agentic Orchestration Demo — smolagents + Claude Sonnet

A minimal two-tool agent demonstrating LLM-driven orchestration: the model writes code, executes it, observes output, recovers from failures, and chains tool calls — without any procedural control flow in the implementation.

## What This Demonstrates

The structural shift from *"procedural code that calls an LLM"* to *"LLM that calls your tools."*

Query issued: `"Find the country ranked #3 by GDP. Then look up its capital."`

No join logic. No ranking loop. No relational query in the implementation. The LLM plans the execution, hits dead ends, recovers using world knowledge, and chains two tool calls to reach the answer.

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
| 3 | Loop over `["Japan", "Germany", "India"]` using world-knowledge priors | Germany → rank #3 confirmed |
| 4 | `get_country_capital("Germany")` | **Berlin ✓** |

**The recovery in Step 3 is the key demonstration.** The agent pivoted from a failing call strategy to a world-knowledge-seeded enumeration strategy — no procedural fallback written by the developer, no `try/except` recovery logic, no explicit plan B. The LLM reasoned its way out.

## Execution Pattern

This is a **ReAct loop** (Reason → Act → Observe → repeat):

```
Thought:  What do I need to do next?
Code:     [Python snippet using available tools]
Observe:  [Tool output or error]
→ repeat until final_answer()
```

smolagents makes this loop explicit and inspectable. Every step — including failures — is logged with token counts, generated code, and observations. The orchestration is not hidden inside a framework abstraction.

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

Most "agentic" workflows are procedural code with LLM calls inserted at decision points. The developer controls the execution graph; the LLM answers questions within it.

True orchestration inverts this: the developer registers tools; the LLM controls the execution graph. The difference is observable in the trace — look for recovery behavior across steps. A procedurally-driven system fails silently or throws. An LLM-orchestrated system reasons its way around the failure using whatever tools remain available.

---

> Bad tools make agents guess. Good tools make agents orchestrate.
