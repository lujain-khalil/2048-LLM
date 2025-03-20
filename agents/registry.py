from agents.random_agent import agent_instance as random_agent_instance
from agents.loop_agent import agent_instance as loop_agent_instance

# Central registry mapping an agent's identifier to its instance and display name.
AGENTS = {
    "random": {
        "instance": random_agent_instance,
        "display_name": "Random Agent"
    },
    "loop": {
        "instance": loop_agent_instance,
        "display_name": "Loop Agent"
    },
    # Add new agents here in the future.
}

def get_agent(agent_name):
    """Return the agent instance for the given name, or None if not found."""
    return AGENTS.get(agent_name, {}).get("instance")

def list_agents():
    """Return a list of available agents with their identifiers and display names."""
    return [{"name": name, "display_name": data["display_name"]} for name, data in AGENTS.items()]
