import importlib
import pkgutil
import agents

# Removed old AGENTS dictionary

AGENT_REGISTRY = {}
DEFAULT_PARAMS = {
    'a_star': {
        'depth_limit': 3
    },
    'ida_star': {
        'initial_depth_limit': 1,
        'max_overall_depth': 5
    },
    'expectimax': {
        'search_depth': 3
    },
    'mcts': {
        'iterations': 100,
        'rollout_depth': 10
    },
    'td_learning': {
        'learning_rate': 0.01,
        'discount_factor': 0.95,
        'epsilon': 0.1
    }
}

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

def get_default_params(name):
    """Get default parameters for an agent."""
    return DEFAULT_PARAMS.get(name, {})

def get_agent_with_params(name, game, params=None):
    """
    Get an agent instance with proper parameters.
    This centralizes parameter handling.
    """
    agent_class = get_agent(name)
    if not agent_class:
        return None
        
    # Start with defaults
    final_params = get_default_params(name).copy()
    
    # Override with provided params
    if params:
        final_params.update(params)
    
    # Instantiate the agent with appropriate parameters
    return agent_class(game, **final_params)

def list_agents():
    """List available agent names."""
    discover_agents() # Ensure agents are loaded
    # print(f"Available agents in registry: {list(AGENT_REGISTRY.keys())}") # Optional: Debug print
    return list(AGENT_REGISTRY.keys())

# Initial discovery
discover_agents()
