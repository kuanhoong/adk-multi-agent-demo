# Exposes root_agent for `adk web` discovery.
# ADK looks for root_agent when serving this package.
try:
    from .agent import root_agent  # when imported as a package (e.g. from Desktop: adk web bwai)
except ImportError:
    from agent import root_agent   # when run directly from within bwai/ directory

__all__ = ["root_agent"]
