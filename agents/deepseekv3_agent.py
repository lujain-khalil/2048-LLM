import os
import requests
from agents.llm_base_agent import LLMBaseAgent
from agents.registry import register_agent

@register_agent('deepseekv3')
class DeepSeekV3Agent(LLMBaseAgent):
    """Agent that uses DeepSeek v3 model to play 2048."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Get API key from environment
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
        
        # API endpoint
        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    
    def call_llm(self, prompt):
        """
        Call the DeepSeek API with the given prompt.
        Raises an exception if the API call fails.
        """
        # Extract valid moves from the prompt to use in the system message
        valid_moves = []
        for line in prompt.split("\n"):
            if "Valid moves" in line:
                # Extract text after colon
                moves_part = line.split(":", 1)[1].strip()
                valid_moves = [m.strip() for m in moves_part.split(",")]
                break
        
        valid_moves_str = ", ".join(valid_moves) if valid_moves else "UP, DOWN, LEFT, RIGHT"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": f"You are a 2048 game agent. Reply with exactly one word from these valid moves: {valid_moves_str}. Do not include any explanation or additional text."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 5
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"] 