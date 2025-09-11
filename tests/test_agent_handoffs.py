import pytest
from livekit.agents import AgentSession, mock_tools
from livekit.plugins import openai

from agent import (
    Assistant, 
    AppointmentAgent, 
    SuggestionAgent, 
    BusinessDevelopmentAgent,
    transfer_to_appointment_agent,
    transfer_to_suggestion_agent,
    transfer_to_business_development_agent,
    UserData
)


@pytest.mark.asyncio
async def test_appointment_agent_handoff_with_context():
    """Test that appointment agent receives context from the main assistant."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create user data with problem description
        userdata = UserData()
        userdata.problem_description = "leaky faucet"
        
        # Start with appointment agent directly
        await session.start(AppointmentAgent())
        session.userdata = userdata
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as appointment specialist and mentions helping with the leaky faucet problem."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_suggestion_agent_handoff_with_context():
    """Test that suggestion agent receives context from the main assistant."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create user data with problem description
        userdata = UserData()
        userdata.problem_description = "poor service quality"
        
        # Start with suggestion agent directly
        await session.start(SuggestionAgent())
        session.userdata = userdata
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as feedback specialist and mentions listening to feedback about poor service quality."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_business_development_agent_handoff_with_context():
    """Test that business development agent receives context from the main assistant."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Create user data with problem description
        userdata = UserData()
        userdata.problem_description = "marketing services inquiry"
        
        # Start with business development agent directly
        await session.start(BusinessDevelopmentAgent())
        session.userdata = userdata
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces himself as business development specialist and mentions helping with marketing services inquiry."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_transfer_functions_create_agents():
    """Test that transfer functions properly create and return agent instances."""
    # Mock context
    class MockContext:
        def __init__(self):
            self.userdata = UserData()
            self.session = MockSession()
    
    class MockSession:
        def __init__(self):
            self.current_agent = None
    
    context = MockContext()
    
    # Test appointment agent transfer
    appointment_agent = await transfer_to_appointment_agent(context, "test problem")
    assert isinstance(appointment_agent, AppointmentAgent)
    assert context.userdata.problem_description == "test problem"
    assert "naya" in context.userdata.agents
    
    # Test suggestion agent transfer
    suggestion_agent = await transfer_to_suggestion_agent(context, "feedback topic")
    assert isinstance(suggestion_agent, SuggestionAgent)
    assert context.userdata.problem_description == "feedback topic"
    assert "helen" in context.userdata.agents
    
    # Test business development agent transfer
    business_agent = await transfer_to_business_development_agent(context, "business inquiry")
    assert isinstance(business_agent, BusinessDevelopmentAgent)
    assert context.userdata.problem_description == "business inquiry"
    assert "marcus" in context.userdata.agents


@pytest.mark.asyncio
async def test_agent_reuse_in_userdata():
    """Test that agents are reused when already created in userdata."""
    # Mock context
    class MockContext:
        def __init__(self):
            self.userdata = UserData()
            self.session = MockSession()
    
    class MockSession:
        def __init__(self):
            self.current_agent = None
    
    context = MockContext()
    
    # Create agents first time
    agent1 = await transfer_to_appointment_agent(context, "problem 1")
    agent2 = await transfer_to_appointment_agent(context, "problem 2")
    
    # Should be the same instance
    assert agent1 is agent2
    assert "naya" in context.userdata.agents
    assert len(context.userdata.agents) == 1  # Only one appointment agent


@pytest.mark.asyncio
async def test_handoff_preserves_previous_agent():
    """Test that handoff functions preserve the previous agent reference."""
    # Mock context
    class MockContext:
        def __init__(self):
            self.userdata = UserData()
            self.session = MockSession()
    
    class MockSession:
        def __init__(self):
            self.current_agent = "previous_agent"
    
    context = MockContext()
    
    # Transfer to appointment agent
    appointment_agent = await transfer_to_appointment_agent(context, "test problem")
    
    # Should preserve previous agent
    assert context.userdata.prev_agent == "previous_agent"
    assert isinstance(appointment_agent, AppointmentAgent)


@pytest.mark.asyncio
async def test_multiple_agent_handoffs():
    """Test that multiple different agents can be created and managed."""
    # Mock context
    class MockContext:
        def __init__(self):
            self.userdata = UserData()
            self.session = MockSession()
    
    class MockSession:
        def __init__(self):
            self.current_agent = None
    
    context = MockContext()
    
    # Create all three types of agents
    appointment_agent = await transfer_to_appointment_agent(context, "appointment issue")
    suggestion_agent = await transfer_to_suggestion_agent(context, "feedback issue")
    business_agent = await transfer_to_business_development_agent(context, "business issue")
    
    # All agents should be created and stored
    assert "naya" in context.userdata.agents
    assert "helen" in context.userdata.agents
    assert "marcus" in context.userdata.agents
    assert len(context.userdata.agents) == 3
    
    # All should be different instances
    assert appointment_agent is not suggestion_agent
    assert appointment_agent is not business_agent
    assert suggestion_agent is not business_agent


@pytest.mark.asyncio
async def test_agent_handoff_without_problem_description():
    """Test that agents work correctly when no problem description is provided."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Start with appointment agent without context
        await session.start(AppointmentAgent())
        
        result = await session.run(user_input="Hello")
        
        await result.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Introduces herself as appointment specialist and asks how she can help with appointment needs."
        )
        result.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_handoff_sequence():
    """Test a sequence of handoffs between different agents."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Start with main assistant
        await session.start(Assistant())
        
        # First handoff to appointment agent
        result1 = await session.run(user_input="I need to schedule an appointment")
        result1.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
        result1.expect.next_event().is_function_call_output()
        await result1.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges appointment request and mentions connecting to specialist."
        )
        result1.expect.no_more_events()
        
        # Second handoff to suggestion agent
        result2 = await session.run(user_input="Actually, I want to complain about something")
        result2.expect.next_event().is_function_call(name="transfer_to_suggestion_agent")
        result2.expect.next_event().is_function_call_output()
        await result2.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges feedback request and mentions connecting to specialist."
        )
        result2.expect.no_more_events()
        
        # Third handoff to business development agent
        result3 = await session.run(user_input="I'm from another company and want to sell you services")
        result3.expect.next_event().is_function_call(name="transfer_to_business_development_agent")
        result3.expect.next_event().is_function_call_output()
        await result3.expect.next_event().is_message(role="assistant").judge(
            llm, intent="Acknowledges business inquiry and mentions connecting to specialist."
        )
        result3.expect.no_more_events()


@pytest.mark.asyncio
async def test_agent_handoff_with_mocked_tools():
    """Test agent handoffs work correctly with mocked tools."""
    async with (
        openai.LLM(model="gpt-4o-mini") as llm,
        AgentSession(llm=llm) as session,
    ):
        # Mock the transfer functions to return specific agents
        with mock_tools(
            Assistant,
            {
                "transfer_to_appointment_agent": lambda: AppointmentAgent(),
                "transfer_to_suggestion_agent": lambda: SuggestionAgent(),
                "transfer_to_business_development_agent": lambda: BusinessDevelopmentAgent(),
            },
        ):
            await session.start(Assistant())
            
            # Test appointment handoff
            result1 = await session.run(user_input="I need an appointment")
            result1.expect.next_event().is_function_call(name="transfer_to_appointment_agent")
            result1.expect.next_event().is_function_call_output()
            await result1.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges appointment request and mentions connecting to specialist."
            )
            result1.expect.no_more_events()
            
            # Test suggestion handoff
            result2 = await session.run(user_input="I want to give feedback")
            result2.expect.next_event().is_function_call(name="transfer_to_suggestion_agent")
            result2.expect.next_event().is_function_call_output()
            await result2.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges feedback request and mentions connecting to specialist."
            )
            result2.expect.no_more_events()
            
            # Test business development handoff
            result3 = await session.run(user_input="I want to sell you something")
            result3.expect.next_event().is_function_call(name="transfer_to_business_development_agent")
            result3.expect.next_event().is_function_call_output()
            await result3.expect.next_event().is_message(role="assistant").judge(
                llm, intent="Acknowledges business inquiry and mentions connecting to specialist."
            )
            result3.expect.no_more_events()
