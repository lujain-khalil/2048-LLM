#!/usr/bin/env python
"""
Test script for Gemini LLM agent.
This script tests if the Gemini agent is properly configured with API keys
and can generate valid responses.
"""

import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def test_gemini_api():
    """Test the Gemini API with a simple prompt."""
    # Check if API key is set
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.")
        print("Please set it in your environment or in a .env file.")
        sys.exit(1)
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        # Initialize model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
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
        print("Calling Gemini API...")
        response = model.generate_content(test_prompt)
        
        # Print response
        print("\nGemini API Response:")
        print("====================")
        print(response.text)
        print("====================")
        
        # Check if response contains a valid move
        valid_moves = ["UP", "DOWN", "LEFT", "RIGHT"]
        response_upper = response.text.strip().upper()
        
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
        print(f"ERROR: Failed to call Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini LLM Agent")
    print("========================")
    test_gemini_api() 