# LLM Agent Tests

This directory contains test scripts for each LLM agent in the 2048 game.

## Prerequisites

1. Make sure you have installed all dependencies:
   ```bash
   pip install -r ../requirements.txt
   ```

2. Set up your API keys as environment variables or in a `.env` file in the project root:
   ```bash
   # For Gemini and Gemma 3
   GEMINI_API_KEY=your_google_api_key

   # For GPT-4o Mini
   OPENAI_API_KEY=your_openai_api_key

   # For DeepSeek v3
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

## Running Tests

### Test All LLMs

To test all LLM agents at once:

```bash
python test_all_llms.py
```

### Test a Specific LLM

To test a specific LLM agent:

```bash
python test_all_llms.py --llm gemini
python test_all_llms.py --llm gpt4o_mini
python test_all_llms.py --llm deepseekv3
python test_all_llms.py --llm gemma3
```

Or run the individual test scripts directly:

```bash
python test_gemini.py
python test_gpt4o_mini.py
python test_deepseekv3.py
python test_gemma3.py
```

## Test Results

Each test will:
1. Check if the required API key is set
2. Make a test call to the LLM API with a sample 2048 game grid
3. Validate the response to ensure it contains a valid move
4. Print the result

If any test fails, it will print the error message and exit with a non-zero status code. 