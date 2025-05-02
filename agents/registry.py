import importlib
import pkgutil
import agents

# Removed old AGENTS dictionary

AGENT_REGISTRY = {}

def register_agent(name):
    def decorator(cls):
        AGENT_REGISTRY[name] = cls
        return cls
    return decorator

def discover_agents():
    """Automatically discover agents in the agents package."""
    import agents # Ensure the package is imported
    # Add path check for robustness
    if not hasattr(agents, '__path__'):
         print("Warning: 'agents' is not a package or path is not set.")
         return
    for _, name, _ in pkgutil.iter_modules(agents.__path__):
        # Also skip __init__.py
        if name != 'agent' and name != 'registry' and name != '__init__': 
            try:
                importlib.import_module(f'agents.{name}')
                # print(f"Successfully discovered and imported agent: {name}") # Optional: Debug print
            except ModuleNotFoundError:
                 print(f"Warning: Could not import module agents.{name}. Skipping.") # More specific error
            except Exception as e:
                print(f"Error importing agent {name}: {e}")

def get_agent(name):
    """Get an agent class by name."""
    discover_agents() # Ensure agents are loaded
    return AGENT_REGISTRY.get(name)

def list_agents():
    """List available agent names."""
    discover_agents() # Ensure agents are loaded
    # print(f"Available agents in registry: {list(AGENT_REGISTRY.keys())}") # Optional: Debug print
    return list(AGENT_REGISTRY.keys())

# Initial discovery
discover_agents()
