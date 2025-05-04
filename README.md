# 2048-LLM

A 2048 game that can be played with various AI agents, including LLM models.

## LLM Agents

The game now supports the following LLM models as agents:

1. **Gemini** - Google's Gemini Pro model
2. **GPT-4o Mini** - OpenAI's GPT-4o Mini model
3. **DeepSeek v3** - DeepSeek's v3 model
4. **Gemma 3** - Google's Gemma 3 model

### Setup

To use the LLM agents, you need to set up the following environment variables with your API keys:

```bash
# For Gemini and Gemma 3
export GEMINI_API_KEY=your_google_api_key

# For GPT-4o Mini
export OPENAI_API_KEY=your_openai_api_key

# For DeepSeek v3
export DEEPSEEK_API_KEY=your_deepseek_api_key
```

You can set these environment variables in a `.env` file in the project root directory.

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running the Game

```bash
python run.py
```

Then open your browser and navigate to `http://localhost:5001`.

### Testing LLM Agents

You can test if your LLM API keys are properly configured using the test scripts:

```bash
# Test all LLM agents
python tests/test_all_llms.py

# Test a specific LLM agent
python tests/test_all_llms.py --llm gemini
python tests/test_all_llms.py --llm gpt4o_mini
python tests/test_all_llms.py --llm deepseekv3
python tests/test_all_llms.py --llm gemma3
```

See the [tests/README.md](tests/README.md) file for more details on testing.