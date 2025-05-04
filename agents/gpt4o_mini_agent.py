import os
import openai
from agents.llm_base_agent import LLMBaseAgent
from agents.registry import register_agent

@register_agent('gpt4o_mini')
class GPT4oMiniAgent(LLMBaseAgent):
    """Agent that uses OpenAI's GPT-4o-mini model to play 2048."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        # Initialize client
        self.client = openai.OpenAI(api_key=api_key)
    
    def call_llm(self, prompt):
        """
        Call the OpenAI API with the given prompt.
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
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are a 2048 game agent. Reply with exactly one word from these valid moves: {valid_moves_str}. Do not include any explanation or additional text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=5
        )
        return response.choices[0].message.content 