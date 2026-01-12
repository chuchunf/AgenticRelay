# Relay  

A proof-of-concept project to explore using LLMs to generate workflows from SOPs, and execute them as LangGraph applications.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your actual API keys
   ```

3. Run tests:
   ```bash
   # Run unit tests
   pytest tests/
   
   # Run integration tests (requires API key)
   pytest tests_integration/
   
   # Run all tests
   pytest
   ```

## Integration Testing

The project includes integration tests that verify real connectivity with external APIs.

### Setup for Integration Tests

1. Configure your LLM API key in `.env`:
   ```
GOOGLE_API_KEY=[Gemini API Key]
GOOGLE_MODEL_NAME=gemini-3-flash-preview
   ```

2. Run integration tests:
   ```bash
   # Run integration tests
   pytest tests_integration/ -v
   
   # Or use the helper script
   python tests_integration/test_llm_integration.py
   ```



## License

MIT License