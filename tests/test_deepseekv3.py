#!/usr/bin/env python
"""
Test script for DeepSeek v3 LLM agent.
This script tests if the DeepSeek v3 agent is properly configured with API keys
and can generate valid responses.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

def list_models(api_key):
    """Optional helper: list available DeepSeek models."""
    url = "https://api.deepseek.com/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    print("Available models:")
    for m in resp.json().get("data", []):
        print("  -", m["id"])


def test_deepseekv3_api():
    """Test the DeepSeek v3 API with a simple prompt."""
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("ERROR: DEEPSEEK_API_KEY environment variable is not set.")
        sys.exit(1)
    
    # Uncomment this if you want to confirm model names:
    # list_models(api_key)

    # Correct chat-completions endpoint
    api_url = "https://api.deepseek.com/v1/chat/completions"
    
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

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a 2048 game agent. Reply with exactly one word from the valid moves: UP, DOWN, LEFT, or RIGHT."},
            {"role": "user",   "content": test_prompt}
        ],
        "temperature": 0.0,
        "max_tokens": 5
    }

    try:
        print("Calling DeepSeek v3 API...")
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"ERROR: API returned HTTP {response.status_code}: {response.text}")
        return False
    except Exception as e:
        print(f"ERROR: Failed to call DeepSeek v3 API: {e}")
        return False

    data = response.json()
    # DeepSeek returns content in choices[0].message.content
    response_text = data["choices"][0]["message"]["content"].strip()
    print("\nDeepSeek v3 API Response:")
    print("========================")
    print(response_text)
    print("========================")

    valid_moves = {"UP", "DOWN", "LEFT", "RIGHT"}
    upper = response_text.upper()
    if upper in valid_moves:
        print(f"✅ Valid move detected: {upper}")
    else:
        # see if any valid move is embedded
        for move in valid_moves:
            if move in upper:
                print(f"⚠️ Found '{move}' in response, but unexpected extra text.")
                break
        else:
            print("❌ No valid move found in response.")

    print("\nTest completed!")
    return True

if __name__ == "__main__":
    print("Testing DeepSeek v3 LLM Agent")
    print("============================")
    test_deepseekv3_api()
