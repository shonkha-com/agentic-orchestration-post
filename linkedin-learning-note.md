# What Two Tiny Agent Runs Teach About Tool Design

This note summarizes two `smolagents` session logs:

- `session_20260521_212608.log`
- `session_20260521_212736.log`

Both runs completed the task:

> Find the country ranked number 3 by GDP. Then look up its capital. Use only the available tools for both steps.

Both runs ended with the same final answer:

> Germany: capital is Berlin

The interesting lesson is not the answer. The interesting lesson is how the agent got there.

## The Setup

The agent had two tools:

```python
get_country_gdp_rank(country: str) -> str
get_country_capital(country: str) -> str
```

The first tool looks up GDP rank when given a country name. It does not look up a country when given a rank.

That difference sounds small, but it changed the agent's behavior.

The user asked a rank-shaped question:

```text
Which country is ranked #3?
```

But the tool exposed a country-shaped interface:

```text
Tell me the rank for this country.
```

That mismatch created extra work.

## What Happened In The Logs

In the first run, the agent tried to ask the GDP tool directly:

```python
get_country_gdp_rank(country="global #3")
```

The tool returned:

```text
global #3: not found in lookup table
```

The agent tried again with a more descriptive phrase:

```python
get_country_gdp_rank(country="country with the third highest GDP")
```

That also failed, because the tool still expected a country name.

Then the agent changed strategy. It tested candidate countries one by one:

```python
countries = ["Germany", "Japan", "UK", "France"]
```

That worked. Germany returned GDP rank number 3, so the agent called the capital tool and answered Berlin.

In the second run, the same pattern appeared:

1. Try `rank #3`.
2. Get `not found`.
3. Check likely countries manually.
4. Find Germany.
5. Ask for Germany's capital.
6. Return Berlin.

The agent succeeded, but it had to discover the right pathway through trial and error.

## The Lesson

Agents are not just "models plus tools." They are models operating inside the affordances and constraints of the tools we give them.

If the tool interface matches the user's question, the agent can move directly.

If the tool interface does not match the user's question, the agent has to improvise.

That improvisation can be useful. It is also more expensive, slower, and less predictable.

## A Better Tool Shape

For the original task, this tool is technically useful but directionally awkward:

```python
def get_country_gdp_rank(country: str) -> str:
    ...
```

It answers:

```text
What is the GDP rank of Germany?
```

But the user asked:

```text
Which country has GDP rank number 3?
```

A better interface would match the direction of the user's intent:

```python
def get_country_by_gdp_rank(rank: int) -> str:
    ...
```

Or expose an ordered list:

```python
def get_top_gdp_countries(n: int) -> list[str]:
    ...
```

That is the idea behind the `v5` version in this repo. Instead of asking the agent to reverse-engineer the rank through country lookups, give it a tool that naturally supports the query direction.

## Why Logs Matter

The final answer hides the most valuable part of the experiment.

If you only look at the answer, the run looks simple:

```text
Germany: capital is Berlin
```

If you look at the trace, you learn how the agent behaved:

- It initially passed the wrong kind of argument to the tool.
- It read the tool's failure as feedback.
- It revised its plan.
- It used candidate exploration to recover.
- It completed the task in four steps.

That is why traces are useful when building agentic systems. They show the difference between a lucky final answer and a reliable workflow.

## A Practical Rule

When designing tools for agents, ask:

> Does this tool accept inputs in the same shape as the user's likely question?

If yes, the agent can often solve the task cleanly.

If no, the agent may still solve it, but it will need extra reasoning steps to bridge the gap.

For small demos, that extra reasoning is interesting.

For production workflows, it can become cost, latency, and risk.

## LinkedIn Post Draft

I ran a tiny `smolagents` experiment that taught a useful agent-design lesson.

The task was simple: find the country ranked number 3 by GDP, then find its capital.

The agent had a GDP lookup tool and a capital lookup tool. It got the right answer: Germany, Berlin.

But the logs were more interesting than the answer.

The GDP tool accepted a country name and returned that country's rank. The user question was the opposite: given a rank, find the country.

So the agent first tried calls like `rank #3` and `global #3`. Those failed. Then it recovered by testing likely countries one by one until it found Germany.

That is a nice little reminder:

Agents are not just models plus tools. They are models operating inside the shape of the tools we give them.

If the tool matches the user's intent, the agent moves directly.

If the tool is directionally awkward, the agent may still succeed, but through extra trial, error, tokens, and latency.

The final answer said "Berlin."

The trace said: "design your tools to match the query direction."

That is where the learning was.
