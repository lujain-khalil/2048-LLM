import os
import google.generativeai as genai
from agents.llm_base_agent import LLMBaseAgent
from agents.registry import register_agent

@register_agent('gemini')
class GeminiAgent(LLMBaseAgent):
    """Agent that uses Google's Gemini model to play 2048."""
    
    def __init__(self, game):
        super().__init__(game)
        
        # Configure the Gemini API with API key from environment
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel('gemini-2.0-flash',
            generation_config={
                "temperature": 0.2,  # Lower temperature for more consistent outputs
                "max_output_tokens": 10,  # Short response with just the move
            },
        )
    
    def call_llm(self, prompt):
        """
        Call the Gemini API with the given prompt.
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