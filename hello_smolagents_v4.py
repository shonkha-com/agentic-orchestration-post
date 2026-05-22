import os
from smolagents import CodeAgent
from smolagents import tool

from session_logger import SessionLogger

if os.getenv("ANTHROPIC_API_KEY"):
    from smolagents import LiteLLMModel
    model = LiteLLMModel(model_id="anthropic/claude-sonnet-4-20250514")
else:
    from smolagents import InferenceClientModel
    model = InferenceClientModel(model_id="Qwen/Qwen2.5-Coder-32B-Instruct")


@tool
def get_country_gdp_rank(country: str) -> str:
    """
    Returns the approximate GDP rank and GDP value for a given country.
    Use this when you need to verify or look up where a specific country
    ranks in global GDP.

    Args:
        country: The name of the country to look up.
    """
    gdp_data = {
        "united states": (1, 28.78),
        "china": (2, 18.53),
        "germany": (3, 4.59),
        "japan": (4, 4.11),
        "india": (5, 3.94),
        "united kingdom": (6, 3.34),
        "france": (7, 3.13),
    }
    result = gdp_data.get(country.lower())
    if result:
        rank, gdp = result
        return f"{country}: GDP rank #{rank}, ~${gdp}T USD (2024 IMF estimate)"
    return f"{country}: not found in lookup table"


@tool
def get_country_capital(country: str) -> str:
    """
    Returns the capital city of a given country.
    Use this when you need to look up the capital of a specific country.

    Args:
        country: The name of the country.
    """
    capital_data = {
        "united states": "Washington D.C.",
        "china": "Beijing",
        "germany": "Berlin",
        "japan": "Tokyo",
        "india": "New Delhi",
        "united kingdom": "London",
        "france": "Paris",
    }
    capital = capital_data.get(country.lower())
    if capital:
        return f"{country}: capital is {capital}"
    return f"{country}: not found in lookup table"

session = SessionLogger(log_dir="logs")
agent = CodeAgent(
    tools=[get_country_gdp_rank, get_country_capital],
    model=model,
    step_callbacks=session.callbacks,
)

result = agent.run(
    "Find the country ranked #3 by GDP. Then look up its capital. " \
    "Use only the available tools for both steps."
)

print("=== GDP Rank and Capital Task v4 ===")
print(result)

session.close()
print(f"\nSession logged to: {session.log_path}")
