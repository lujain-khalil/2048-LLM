#!/usr/bin/env python
"""
Test script for GPT-4o mini LLM agent.
This script tests if the GPT-4o mini agent is properly configured with API keys
and can generate valid responses.
"""

import os
import sys
import openai
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def test_gpt4o_mini_api():
    """Test the GPT-4o mini API with a simple prompt."""
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.")
        print("Please set it in your environment or in a .env file.")
        sys.exit(1)
    
    try:
        # Initialize client
        client = openai.OpenAI(api_key=api_key)
        
        # Test prompt with valid moves explicitly mentioned
        test_prompt = """
        You are controlling a 2048 game. Here's the current grid:

        2 _ 4 _
        _ 2 _ _
        4 _ 2 _
        _ _ _ 2

        Current score: 16

        Valid moves (that will change the grid): UP, DOWN, LEFT, RIGHT

        Analyze the grid and choose the best move from the valid options.
        Respond with exactly one of these words: UP, DOWN, LEFT, RIGHT.
        """
        
        # Call API
        print("Calling GPT-4o mini API...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a 2048 game agent. Reply with exactly one word from the valid moves: UP, DOWN, LEFT, or RIGHT."},
                {"role": "user", "content": test_prompt}
            ],
            temperature=0.5,
            max_tokens=10
        )
        
        response_text = response.choices[0].message.content
        
        # Print response
        print("\nGPT-4o mini API Response:")
        print("=========================")
        print(response_text)
        print("=========================")
        
        # Check if response contains a valid move
        valid_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        response_upper = response_text.strip().upper()
        
        if response_upper in valid_moves:
            print(f"✅ Valid move detected: {response_upper}")
        else:
            contains_valid = False
            for move in valid_moves:
                if move in response_upper:
                    contains_valid = True
                    print(f"⚠️ Response contains valid move '{move}' but includes extra text.")
                    break
            
            if not contains_valid:
                print("❌ No valid move found in response.")
        
        print("\nTest completed successfully!")
        return True
        
    except Exception as e:
        print(f"ERROR: Failed to call GPT-4o mini API: {e}")
        return False

if __name__ == "__main__":
    print("Testing GPT-4o mini LLM Agent")
    print("============================")
    test_gpt4o_mini_api() 