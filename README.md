# Plumbing Voice AI Agent

A sophisticated multi-agent voice AI system built with LiveKit for a fictitious plumbing company. This system provides intelligent call routing, appointment scheduling, customer feedback handling, and business development inquiries through natural voice conversations.

## Engineering Notes

A few problems worth calling out, since they're the parts that took real work rather than configuration.

### Handoffs that don't lose the conversation

Routing a caller to a specialist is easy. Routing them *without making them repeat themselves* is the actual problem.

Context travels through a `UserData` dataclass attached to the session:

```python
@dataclass
class UserData:
    prev_agent: Optional[Agent] = None
    agents: Dict[str, Agent] = field(default_factory=dict)
    problem_description: Optional[str] = None
```

The transferring agent writes `problem_description` before handing off, and the receiving agent reads it in `on_enter` to open with an informed greeting instead of a cold one. Agents are held in a registry rather than recreated per transfer, so a caller bounced back to a previous agent returns to the same instance. All four are pre-initialised in the entrypoint to avoid a cold-start pause mid-call — latency you'd hear.

### Markdown was being read out loud

The LLM formats its responses. Asterisks, underscores and backticks are invisible in a chat UI and audible in a voice one — the TTS was pronouncing them.

Fixed by subclassing the Cartesia TTS and stripping formatting before synthesis:

```python
class CleanTTS(cartesia.TTS):
    async def say(self, text: str, **kwargs) -> None:
        await super().say(clean_text(text), **kwargs)
```

Solving it at the TTS boundary rather than in the prompt means it holds regardless of what the model decides to emit.

### Tuning for telephony, not for a demo

The voice pipeline is assembled for phone-quality audio and natural turn-taking:

- **STT** — Deepgram Nova-3
- **TTS** — Cartesia Sonic-2, with per-agent voices
- **VAD** — Silero
- **Turn detection** — LiveKit's multilingual model, so turn-ends are predicted from linguistic cues rather than a fixed silence threshold. Fixed thresholds either cut people off mid-sentence or leave dead air.
- **Noise cancellation** — BVC Telephony, chosen over the general-purpose model because the target input is a phone line.

Agent instructions also carry explicit conversational guidance — pause naturally, don't interrupt, acknowledge before answering — because a response that reads well can still sound wrong.

### Testing agent behaviour, not just agent wiring

Roughly 2,300 lines of tests across four suites:

- **Basic** — initialisation, configuration, tool registration
- **Behavioural** — conversation flow and response quality
- **Handoffs** — transfer correctness and, importantly, that context survives the transfer
- **Edge cases** — invalid input, missing data, boundary conditions

The handoff suite is the one that earns its keep. Asserting that a transfer *happened* is trivial; asserting that `problem_description` arrived intact and the receiving agent used it is what actually catches regressions.

### Tools and validation

Business logic sits in `function_tool` handlers rather than in prompts: appointment scheduling, cancellation by tracking ID, technician availability, appointment history lookup. Customer data is validated in code — US address format, phone number format, zip code — so a mis-heard transcription fails a check instead of quietly booking a job to a nonexistent address.

### Deployment

Containerised with a multi-stage build on `python:3.11-slim`, running as a non-privileged user, with `uv` for dependency resolution. Deployed to LiveKit Cloud via `lk agent create` / `deploy` / `rollback`, with region configuration in `livekit.toml`. A `Makefile` wraps the console, dev and production modes so the run path is the same for everyone.

### What I'd do next

- Replace the mocked appointment store with a real database and proper concurrency handling around slot booking
- Add structured logging and per-turn latency metrics across the STT → LLM → TTS chain, so regressions surface as numbers rather than as "it feels slow"
- Build an evaluation harness with recorded conversations to catch behavioural drift when prompts or models change
- Handle provider failure explicitly — timeouts and fallbacks when STT or TTS stalls, rather than letting the caller sit in silence
  
## 🏗️ Architecture

The system consists of **4 specialized AI agents** that work together to handle different aspects of customer service:
### **Anna** - Main Receptionist
- **Role**: Primary point of contact and call router
- **Capabilities**: 
  - Greets customers and determines their needs
  - Answers general questions about plumbing services
  - Routes calls to appropriate specialists
  - Handles emergency situations with priority
- **Voice**: Professional, friendly receptionist voice

### **Naya** - Appointment Specialist  
- **Role**: Handles all appointment-related tasks
- **Capabilities**:
  - Schedules new plumbing appointments
  - Reschedules or cancels existing appointments
  - Checks technician availability
  - Validates customer information (address, phone, zip code)
  - Generates tracking IDs for appointments
- **Voice**: Clear, professional appointment specialist voice

### **Helen** - Customer Feedback Specialist
- **Role**: Manages customer feedback and suggestions
- **Capabilities**:
  - Listens to customer complaints and suggestions
  - Links feedback to specific past appointments
  - Stores feedback for management review
  - Provides empathetic customer support
- **Voice**: Warm, empathetic feedback specialist voice

### **Marcus** - Business Development Specialist
- **Role**: Handles business inquiries and partnerships
- **Capabilities**:
  - Processes service offerings from other companies
  - Handles employment requests
  - Manages partnership proposals
  - Filters relevant vs. irrelevant business inquiries
- **Voice**: Professional, business-focused voice

## 🚀 Key Features

### **Intelligent Call Routing**
- Automatic detection of customer intent
- Seamless handoffs between specialized agents
- Context preservation across agent transfers
- Problem description sharing between agents

### **Advanced Voice Processing**
- **Speech-to-Text**: Deepgram Nova-3 for accurate transcription
- **Text-to-Speech**: Cartesia Sonic-2 with custom voice cleaning
- **Voice Activity Detection**: Silero VAD for natural conversation flow
- **Turn Detection**: Multilingual model for conversation management
- **Noise Cancellation**: BVC Telephony for clear audio in noisy environments

### **Smart Appointment Management**
- Real-time technician availability checking
- US address and zip code validation
- Phone number format verification
- Automatic tracking ID generation
- Appointment history lookup

### **Comprehensive Data Handling**
- Customer information collection and validation
- Feedback storage and categorization
- Business inquiry processing and filtering
- Appointment tracking and management

## 🛠️ Technology Stack

- **Framework**: LiveKit Agents
- **Language Model**: OpenAI GPT-4o-mini
- **Speech-to-Text**: Deepgram Nova-3
- **Text-to-Speech**: Cartesia Sonic-2
- **Voice Processing**: Silero VAD, Multilingual Turn Detection
- **Noise Cancellation**: BVC Telephony
- **Language**: Python 3.11+
- **Package Manager**: UV

## 📋 Prerequisites

Before running the project, you'll need API keys for:

1. **LiveKit** - For real-time communication infrastructure
2. **OpenAI** - For language model processing
3. **Cartesia** - For text-to-speech synthesis
4. **Deepgram** - For speech-to-text transcription

## ⚙️ Project Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd plumbing_voice_ai_agent
   ```

2. **Install dependencies**
   ```bash
   make setup
   ```

3. **Configure environment variables**
   ```bash
   cp .env.sample .env.local
   # Edit .env.local with your API keys
   ```

4. **Download required models**
   ```bash
   uv run agent.py download-files
   ```

## 🚀 Running the Project

The project provides several convenient Makefile commands for different running modes:

### Console Mode (Testing)
```bash
# Run the agent in terminal for testing and development
make run-console
# Equivalent to: uv run agent.py console
```
**Use case**: Perfect for testing agent responses, debugging, and development. The agent runs in a text-based console where you can type messages and see responses.

### Development Mode
```bash
# Start the agent in development mode with hot reloading
make run-dev
# Equivalent to: uv run agent.py dev

# In another terminal, start your frontend client
# The agent will be available at your LiveKit URL
```
**Use case**: Ideal for development and testing with a web frontend. The agent runs with development features enabled and connects to your LiveKit development environment.

### Production Mode
```bash
# Deploy the agent to LiveKit Cloud for production use
make run-prod
# Equivalent to: uv run agent.py start
```
**Use case**: Deploys the agent to LiveKit Cloud for production use. This is what you'd use when the agent is ready for real customer calls.

### Manual Commands
You can also run the commands directly without the Makefile:

```bash
# Console mode
uv run agent.py console

# Development mode  
uv run agent.py dev

# Production mode
uv run agent.py start
```

## 🧪 Testing

The project includes comprehensive test suites:

```bash

# Run specific test categories
make test-basic      # Basic functionality tests
make test-behavior   # Behavioral tests
make test-handoffs   # Agent handoff tests
make test-edge-cases # Edge case handling tests

# Run with coverage
make test-coverage
```

### Test Categories

- **Basic Tests**: Agent initialization, configuration, and tool registration
- **Behavioral Tests**: Conversation flow, response quality, and user interaction
- **Handoff Tests**: Agent transfer functionality and context preservation
- **Edge Case Tests**: Error handling, invalid inputs, and boundary conditions

## 📁 Project Structure

```
plumbing_voice_ai_agent/
├── agent.py                 # Main agent implementation
├── livekit.toml            # LiveKit configuration
├── pyproject.toml          # Python project configuration
├── Dockerfile              # Container configuration
├── Makefile               # Build and test automation
├── README.md              # This file
├── .env.sample            # Environment variables template
├── tests/                 # Test suites
│   ├── test_simple.py     # Basic unit tests
│   ├── test_final.py      # Comprehensive behavioral tests
│   ├── test_agent_handoffs.py    # Handoff functionality tests
│   └── test_agent_edge_cases.py  # Edge case tests
└── KMS/                   # Logs directory
```

## 🔧 Configuration

### LiveKit Configuration (`livekit.toml`)
```toml
[project]
subdomain = "your-livekit-subdomain"
url = "wss://your-livekit-subdomain.livekit.cloud"

[agent]
id = "your-agent-id"
regions = ["us-east"]
```

### Environment Variables (`.env.local`)
```bash
LIVEKIT_URL="wss://your-subdomain.livekit.cloud"
LIVEKIT_API_KEY="your-api-key"
LIVEKIT_API_SECRET="your-api-secret"
OPENAI_API_KEY="your-openai-key"
CARTESIA_API_KEY="your-cartesia-key"
DEEPGRAM_API_KEY="your-deepgram-key"
```

## 🎯 Use Cases

### **Customer Service Scenarios**
- **Emergency Calls**: "I have a burst pipe!" → Immediate routing to appointment specialist
- **Appointment Booking**: "I need to schedule a repair" → Transfer to Naya for scheduling
- **Feedback**: "I want to complain about my service" → Transfer to Helen for feedback handling
- **Business Inquiries**: "I want to sell you supplies" → Transfer to Marcus for business development

### **Appointment Management**
- Schedule new appointments with available technicians
- Reschedule or cancel existing appointments using tracking IDs
- Validate customer information (US addresses, phone numbers, zip codes)
- Generate and provide tracking IDs for appointment confirmation

### **Feedback Processing**
- Collect customer complaints and suggestions
- Link feedback to specific past appointments
- Store feedback for management review
- Provide empathetic customer support

## 🔄 Agent Handoff Flow

```
Customer Call
     ↓
   Anna (Receptionist)
     ↓
   Intent Detection
     ↓
┌─────────────────┬─────────────────┬─────────────────┐
│   Naya          │     Helen       │     Marcus      │
│ (Appointments)  │   (Feedback)    │ (Business Dev)  │
└─────────────────┴─────────────────┴─────────────────┘
     ↓
  Context Preservation
     ↓
  Specialized Service
```

## 🚀 Deployment

### Local Development
```bash
make dev
```

### Production Deployment in LiveKit
For the first time:
```bash
lk agent create
```

And for the other times:
```bash
lk agent deploy
```

To rollback, you can use the following cmd:
```bash
lk agent rollback
```

## 📊 Monitoring and Logs

- **Agent Logs**: Available through LiveKit Cloud dashboard
- **Console Output**: Real-time logging of agent interactions
- **Test Results**: Comprehensive test reporting with coverage metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the test results: `make test`
2. Review the logs in the LiveKit Cloud dashboard
3. Check the console output for error messages
4. Ensure all API keys are correctly configured

---

**Built with ❤️ using LiveKit Agents**

