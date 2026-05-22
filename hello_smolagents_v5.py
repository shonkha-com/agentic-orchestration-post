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
def get_top_gdp_countries(n: int) -> list[str]:
    """
    Returns a list of country names ordered from largest to smallest economy, length n.

    Args:
        n: Number of country names to return.
    """
    countries = [
        "United States",
        "China",
        "Germany",
        "Japan",
        "India",
        "United Kingdom",
        "France",
    ]
    return countries[: max(0, n)]


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
        return capital
    return f"{country}: not found in lookup table"


session = SessionLogger(log_dir="logs")
agent = CodeAgent(
    tools=[get_top_gdp_countries, get_country_capital],
    model=model,
    step_callbacks=session.callbacks,
)

result = agent.run(
    "What is the capital city of the country with the second largest economy? Use get_top_gdp_countries and get_country_capital."
)
print("=== Query Direction GDP and Capital Task v5 ===")
print(result)

session.close()
print(f"\nSession logged to: {session.log_path}")
