#!/usr/bin/env python
"""
Test script for all LLM agents.
This script allows testing all LLM agents or a specific one.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Import test functions from individual test scripts
try:
    from test_gemini import test_gemini_api
    from test_gpt4o_mini import test_gpt4o_mini_api
    from test_deepseekv3 import test_deepseekv3_api
    from test_gemma3 import test_gemma3_api
except ImportError:
    # Adjust import paths for running from the tests directory
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from test_gemini import test_gemini_api
    from test_gpt4o_mini import test_gpt4o_mini_api
    from test_deepseekv3 import test_deepseekv3_api
    from test_gemma3 import test_gemma3_api

# Load environment variables from .env file if it exists
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Test LLM agents for 2048 game.')
    parser.add_argument('--llm', type=str, choices=['gemini', 'gpt4o_mini', 'deepseekv3', 'gemma3', 'all'],
                        default='all', help='Specify which LLM to test (default: all)')
    return parser.parse_args()

def main():
    """Run tests based on command line arguments."""
    args = parse_args()
    
    test_functions = {
        'gemini': test_gemini_api,
        'gpt4o_mini': test_gpt4o_mini_api,
        'deepseekv3': test_deepseekv3_api,
        'gemma3': test_gemma3_api
    }
    
    if args.llm == 'all':
        print("Testing all LLM agents")
        print("=====================")
        
        results = {}
        for llm_name, test_func in test_functions.items():
            print(f"\n\nTesting {llm_name} agent:")
            print("-" * (len(llm_name) + 15))
            try:
                result = test_func()
                results[llm_name] = result
            except Exception as e:
                print(f"ERROR: Test for {llm_name} failed with exception: {e}")
                results[llm_name] = False
        
        # Print summary
        print("\n\nTest Summary:")
        print("=============")
        all_passed = True
        for llm_name, result in results.items():
            status = "PASSED" if result else "FAILED"
            print(f"{llm_name}: {status}")
            if not result:
                all_passed = False
        
        # Set exit code based on test results
        sys.exit(0 if all_passed else 1)
    else:
        # Test specific LLM
        test_func = test_functions.get(args.llm)
        if test_func:
            result = test_func()
            sys.exit(0 if result else 1)
        else:
            print(f"ERROR: No test function found for LLM: {args.llm}")
            sys.exit(1)

if __name__ == "__main__":
    main() 