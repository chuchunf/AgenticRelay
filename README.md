# Relay

A proof-of-concept project exploring the use of LLM to generate workflows from SOPs, validate and approve workflows, and execute them as LangGraph applications.

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
   OPENAI_API_KEY=your_actual_api_key_here
   # or other LLM provider keys
   ```

2. Run integration tests:
   ```bash
   # Run integration tests
   pytest tests_integration/ -v
   
   # Or use the helper script
   python tests_integration/run_with_api_key.py
   ```

**Note**: Integration tests will be automatically skipped if no API key is configured.

## Project Structure

```
src/
├── utilities/               # Shared utilities and LLM integration
│   ├── llm_client.py       # Generic LangChain LLM client
│   ├── configuration_manager.py
│   └── logger.py
├── sop_processing/         # SOP to workflow conversion
├── workflow_management/    # Workflow validation and management
├── workflow_execution/     # LangGraph workflow execution
└── skills/                 # Skill management system
tests/                     # Unit and integration tests
```

## License

MIT License