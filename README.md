# Plumbing Voice AI Agent

A sophisticated multi-agent voice AI system built with LiveKit for a fictitious plumbing company. This system provides intelligent call routing, appointment scheduling, customer feedback handling, and business development inquiries through natural voice conversations.

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

