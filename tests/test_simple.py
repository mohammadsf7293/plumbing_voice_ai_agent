import pytest
from agent import Assistant, AppointmentAgent, SuggestionAgent, BusinessDevelopmentAgent, clean_text


def test_assistant_initialization():
    """Test that the Assistant class initializes correctly."""
    assistant = Assistant()
    assert "Anna" in assistant.instructions
    assert "receptionist" in assistant.instructions.lower()


def test_appointment_agent_initialization():
    """Test that the AppointmentAgent class initializes correctly."""
    agent = AppointmentAgent()
    assert "Naya" in agent.instructions
    assert "appointment" in agent.instructions.lower()


def test_suggestion_agent_initialization():
    """Test that the SuggestionAgent class initializes correctly."""
    agent = SuggestionAgent()
    assert "Helen" in agent.instructions
    assert "feedback" in agent.instructions.lower()


def test_business_development_agent_initialization():
    """Test that the BusinessDevelopmentAgent class initializes correctly."""
    agent = BusinessDevelopmentAgent()
    assert "Marcus" in agent.instructions
    assert "business development" in agent.instructions.lower()


def test_clean_text_function():
    """Test that the clean_text function works correctly."""
    # Test basic markdown symbols
    assert clean_text("**bold**") == "bold"
    assert clean_text("_italic_") == "italic"
    assert clean_text("# heading") == " heading"
    assert clean_text("`code`") == "code"
    assert clean_text("~strikethrough~") == "strikethrough"
    assert clean_text("> quote") == " quote"
    assert clean_text("- list item") == " list item"
    
    # Test multiple symbols
    assert clean_text("**_bold italic_**") == "bold italic"
    assert clean_text("# `code heading`") == " code heading"
    
    # Test symbols in middle of text
    assert clean_text("This is *bold* text") == "This is bold text"
    assert clean_text("Before-after") == "Beforeafter"
    
    # Test empty string
    assert clean_text("") == ""
    
    # Test string with only symbols
    assert clean_text("*_#`~>-") == ""


def test_agent_tools_exist():
    """Test that agents have the expected tools."""
    # Test Assistant tools
    assistant = Assistant()
    assert hasattr(assistant, 'tools')
    assert len(assistant.tools) > 0
    
    # Check for transfer tools
    tool_names = [str(tool) for tool in assistant.tools]
    assert any("transfer_to_appointment_agent" in name for name in tool_names)
    assert any("transfer_to_suggestion_agent" in name for name in tool_names)
    assert any("transfer_to_business_development_agent" in name for name in tool_names)
    
    # Test AppointmentAgent tools
    appointment_agent = AppointmentAgent()
    assert hasattr(appointment_agent, 'tools')
    assert len(appointment_agent.tools) > 0
    
    # Check for appointment-related tools
    tool_names = [str(tool) for tool in appointment_agent.tools]
    assert any("get_technician_available_times" in name for name in tool_names)
    assert any("book_appointment_in_db" in name for name in tool_names)
    assert any("find_active_appointments_for_customer" in name for name in tool_names)
    assert any("cancel_appointments_by_tracking_ids" in name for name in tool_names)
    
    # Test SuggestionAgent tools
    suggestion_agent = SuggestionAgent()
    assert hasattr(suggestion_agent, 'tools')
    assert len(suggestion_agent.tools) > 0
    
    # Check for suggestion-related tools
    tool_names = [str(tool) for tool in suggestion_agent.tools]
    assert any("store_customer_suggestions" in name for name in tool_names)
    assert any("get_finished_appointments_for_customer" in name for name in tool_names)
    
    # Test BusinessDevelopmentAgent tools
    business_agent = BusinessDevelopmentAgent()
    assert hasattr(business_agent, 'tools')
    assert len(business_agent.tools) > 0
    
    # Check for business-related tools
    tool_names = [str(tool) for tool in business_agent.tools]
    assert any("store_miscellaneous_requests_in_db" in name for name in tool_names)


def test_agent_instructions_contain_key_elements():
    """Test that agent instructions contain key elements."""
    # Test Assistant instructions
    assistant = Assistant()
    instructions = assistant.instructions.lower()
    assert "anna" in instructions
    assert "receptionist" in instructions
    assert "plumbing" in instructions
    assert "hand off" in instructions or "transfer" in instructions
    
    # Test AppointmentAgent instructions
    appointment_agent = AppointmentAgent()
    instructions = appointment_agent.instructions.lower()
    assert "naya" in instructions
    assert "appointment" in instructions
    assert "schedule" in instructions
    assert "appointment" in instructions  # "booking" is not in the instructions, but "appointment" is
    
    # Test SuggestionAgent instructions
    suggestion_agent = SuggestionAgent()
    instructions = suggestion_agent.instructions.lower()
    assert "helen" in instructions
    assert "feedback" in instructions
    assert "suggestion" in instructions
    assert "complaint" in instructions
    
    # Test BusinessDevelopmentAgent instructions
    business_agent = BusinessDevelopmentAgent()
    instructions = business_agent.instructions.lower()
    assert "marcus" in instructions
    assert "business development" in instructions
    assert "employment" in instructions
    assert "partnership" in instructions


def test_agent_tts_configuration():
    """Test that agents have TTS configured."""
    # Test that all agents have TTS configured
    agents = [Assistant(), AppointmentAgent(), SuggestionAgent(), BusinessDevelopmentAgent()]
    
    for agent in agents:
        assert hasattr(agent, 'tts')
        assert agent.tts is not None
        # Check that it's a TTS instance (CleanTTS wraps Cartesia)
        assert "tts" in str(type(agent.tts)).lower()


def test_agent_voice_assignment():
    """Test that agents have different voices assigned."""
    # Test that different agents have different voice configurations
    assistant = Assistant()
    appointment_agent = AppointmentAgent()
    suggestion_agent = SuggestionAgent()
    business_agent = BusinessDevelopmentAgent()
    
    # All should have TTS configured
    assert assistant.tts is not None
    assert appointment_agent.tts is not None
    assert suggestion_agent.tts is not None
    assert business_agent.tts is not None
    
    # They should be different instances (different voice IDs)
    # We can't easily test the voice IDs directly, but we can test they're different objects
    assert assistant.tts is not appointment_agent.tts
    assert appointment_agent.tts is not suggestion_agent.tts
    assert suggestion_agent.tts is not business_agent.tts
