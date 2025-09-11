# Testing Guide for Plumbing Voice AI Agent

This guide explains how to test the plumbing voice AI agent using the LiveKit testing framework.

## Overview

The test suite includes comprehensive behavioral tests for all agents in the system:
- **Anna** (Main Receptionist) - Handles initial customer contact and routing
- **Naya** (Appointment Specialist) - Manages appointment scheduling and booking
- **Helen** (Feedback Specialist) - Collects customer feedback and suggestions
- **Marcus** (Business Development) - Handles business inquiries and partnerships

## Test Categories

### 1. Basic Tests (`test_assistant.py`)
- Agent initialization
- Basic greeting behavior
- Handoff identification

### 2. Behavior Tests (`test_agent_behavior.py`)
- Complete conversation flows
- Tool usage and function calls
- Agent-specific capabilities
- Multi-turn conversations

### 3. Edge Case Tests (`test_agent_edge_cases.py`)
- Error handling
- Invalid inputs
- Service failures
- Boundary conditions

### 4. Handoff Tests (`test_agent_handoffs.py`)
- Agent-to-agent transfers
- Context preservation
- Agent reuse and management

## Running Tests

### Prerequisites

Make sure you have your API keys set up in `.env.local`:
```bash
OPENAI_API_KEY=your_openai_key
DEEPGRAM_API_KEY=your_deepgram_key
CARTESIA_API_KEY=your_cartesia_key
LIVEKIT_API_KEY=your_livekit_key
LIVEKIT_API_SECRET=your_livekit_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
```

### Quick Start

```bash
# Run all tests
make test-behavior

# Run specific test categories
make test-basic
make test-handoffs
make test-edge-cases

# Run with verbose output
make test-verbose

# Run with coverage report
make test-coverage
```

### Individual Test Files

```bash
# Run specific test files
uv run pytest -v tests/test_assistant.py
uv run pytest -v tests/test_agent_behavior.py
uv run pytest -v tests/test_agent_edge_cases.py
uv run pytest -v tests/test_agent_handoffs.py
```

### Verbose Output

For detailed test execution information:
```bash
LIVEKIT_EVALS_VERBOSE=1 uv run pytest -v -s tests/
```

## Test Examples

### Basic Agent Behavior Test

```python
@pytest.mark.asyncio
async def test_assistant_greeting():
    """Test that Anna provides a friendly greeting."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(Assistant())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Makes a friendly introduction as a receptionist and offers assistance."
        )
        result.expect.no_more_events()
```

### Tool Usage Test

```python
@pytest.mark.asyncio
async def test_appointment_agent_checks_availability():
    """Test that Naya can check technician availability."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="What times are available?")
        
        # Should call the availability function
        result.expect.next_event().is_function_call(name="get_technician_available_times")
        result.expect.next_event().is_function_call_output()
        
        # Should provide available times
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Provides available appointment times from the function call result."
        )
        result.expect.no_more_events()
```

### Error Handling Test

```python
@pytest.mark.asyncio
async def test_appointment_agent_handles_booking_error():
    """Test that Naya handles booking errors gracefully."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the booking function to raise an error
        with mock_tools(
            AppointmentAgent,
            {"book_appointment_in_db": lambda: RuntimeError("Database connection failed")},
        ):
            await session.start(AppointmentAgent())
            
            result = await session.run(user_input="Book me an appointment")
            
            # Should call the booking function
            result.expect.next_event().is_function_call(name="book_appointment_in_db")
            result.expect.next_event().is_function_call_output()
            
            # Should handle the error gracefully
            await result.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges the error and offers alternative solutions."
            )
            result.expect.no_more_events()
```

## Test Assertions

The LiveKit testing framework provides several assertion methods:

### Message Assertions
- `is_message(role="assistant")` - Check message role
- `judge(llm, intent="...")` - Use LLM to evaluate message content
- `contains_message(role="user")` - Check if message exists anywhere

### Function Call Assertions
- `is_function_call(name="function_name")` - Check function was called
- `is_function_call_output()` - Check function output
- `is_agent_handoff(new_agent_type=AgentClass)` - Check agent handoff

### Flow Control
- `next_event()` - Move to next event
- `no_more_events()` - Assert no more events remain
- `skip_next()` - Skip the next event

## Writing New Tests

### 1. Test Structure
```python
@pytest.mark.asyncio
async def test_your_scenario():
    """Test description."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        await session.start(YourAgent())
        
        result = await session.run(user_input="Your test input")
        
        # Your assertions here
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Expected behavior description."
        )
        result.expect.no_more_events()
```

### 2. Testing with Mocked Tools
```python
with mock_tools(
    YourAgent,
    {"tool_name": lambda: "mocked_result"},
):
    # Your test code here
```

### 3. Multi-turn Conversations
```python
# First turn
result1 = await session.run(user_input="First input")
# Assertions for first turn

# Second turn (builds on conversation history)
result2 = await session.run(user_input="Second input")
# Assertions for second turn
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env.local`
2. **Import Errors**: Make sure you're running tests from the project root
3. **Async Issues**: Use `@pytest.mark.asyncio` and `async with` statements
4. **LLM Judgments Failing**: Check that your intent descriptions are clear and specific

### Debug Mode

Run tests with maximum verbosity:
```bash
LIVEKIT_EVALS_VERBOSE=1 uv run pytest -v -s --tb=long tests/
```

### Test Isolation

Each test runs in isolation with fresh agent instances. No cleanup is needed between tests.

## Continuous Integration

For CI/CD pipelines, ensure API keys are available as environment variables:
```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  DEEPGRAM_API_KEY: ${{ secrets.DEEPGRAM_API_KEY }}
  CARTESIA_API_KEY: ${{ secrets.CARTESIA_API_KEY }}
```

## Best Practices

1. **Clear Intent Descriptions**: Write specific, testable intent descriptions for LLM judgments
2. **Test Edge Cases**: Include tests for error conditions and boundary cases
3. **Mock External Dependencies**: Use `mock_tools` for functions that depend on external services
4. **Descriptive Test Names**: Use clear, descriptive names that explain what's being tested
5. **Single Responsibility**: Each test should focus on one specific behavior or scenario

## Resources

- [LiveKit Testing Documentation](https://docs.livekit.io/agents/build/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [LiveKit Agents API Reference](https://docs.livekit.io/agents/reference/)
