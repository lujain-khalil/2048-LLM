import os
import google.generativeai as genai
from agents.llm_base_agent import LLMBaseAgent
from agents.registry import register_agent

@register_agent('gemma3')
class Gemma3Agent(LLMBaseAgent):
    """Agent that uses Google's Gemma 3 model to play 2048."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Configure the Gemini API with API key from environment
        api_key = os.getenv("GEMINI_API_KEY")  # Same API key as Gemini
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        
        # Initialize model using Gemma 3
        self.model = genai.GenerativeModel('gemma-3b',
            generation_config={
                "temperature": 0.2,  # Lower temperature for more consistent outputs
                "max_output_tokens": 10,  # Short response with just the move
            },
        )
    
    def call_llm(self, prompt):
        """
        Call the Gemma 3 API with the given prompt.
        Raises an exception if the API call fails.
        """
        safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]
        
        response = self.model.generate_content(
            prompt,
            safety_settings=safety_settings
        )
        return response.text 