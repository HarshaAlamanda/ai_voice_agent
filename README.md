\# 🤖 AI Voice Receptionist \& Appointment Booking Agent



<p align="center">

&#x20; <strong>An AI-powered receptionist designed to automate conversations, manage appointments, and streamline customer interactions.</strong>

</p>



<p align="center">

&#x20; <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge\&logo=python\&logoColor=white" alt="Python">

&#x20; <img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge\&logo=fastapi\&logoColor=white" alt="FastAPI">

&#x20; <img src="https://img.shields.io/badge/Google-Gemini-4285F4?style=for-the-badge\&logo=google\&logoColor=white" alt="Gemini">

&#x20; <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white" alt="SQLite">

</p>



<p align="center">

&#x20; <a href="https://github.com/HarshaAlamanda/ai\_voice\_agent">Repository</a> ·

&#x20; <a href="#-architecture">Architecture</a> ·

&#x20; <a href="#-getting-started">Getting Started</a> ·

&#x20; <a href="#-roadmap">Roadmap</a>

</p>



\---



\## ✨ Overview



The \*\*AI Voice Receptionist\*\* is a Python-based conversational agent that helps automate receptionist workflows through natural-language interaction.



It combines Google's Gemini model with deterministic Python tools, a FastAPI backend, and an SQLite database to handle business questions, appointment availability, booking workflows, and appointment records.



The project is being developed toward a complete AI receptionist experience, with real cellular-call integration and real SMS delivery treated as separate integration milestones.



\### What it does



\- 🧠 \*\*AI conversations\*\* — Uses Gemini to interpret requests and generate responses.

\- 📅 \*\*Appointment scheduling\*\* — Checks availability and manages booking workflows.

\- 🗄️ \*\*Persistent storage\*\* — Stores appointment records using SQLite.

\- 🌐 \*\*REST API\*\* — Exposes backend functionality through FastAPI.

\- 🔊 \*\*Voice components\*\* — Includes local microphone and text-to-speech functionality.

\- 📩 \*\*SMS confirmation workflow\*\* — Generates appointment confirmation messages and supports mock delivery for development.

\- 🧪 \*\*Automated tests\*\* — Covers core agent, scheduling, date/time, and confirmation behavior.



\---



\## 🏗️ Architecture



```mermaid

flowchart TD

&#x20;   U\[User / Caller] --> I\[Interaction Layer]

&#x20;   I --> API\[FastAPI Backend]

&#x20;   I --> VOICE\[Local Voice Interface]

&#x20;   API --> AGENT\[AI Agent]

&#x20;   VOICE --> AGENT

&#x20;   AGENT --> GEMINI\[Google Gemini]

&#x20;   AGENT --> TOOLS\[Python Business Tools]

&#x20;   TOOLS --> SCHED\[Appointment Scheduler]

&#x20;   TOOLS --> CONTEXT\[Business Context and Contacts]

&#x20;   SCHED --> DB\[(SQLite Database)]

&#x20;   SCHED --> SMS\[SMS Confirmation Service]

&#x20;   SMS --> MOCK\[Mock SMS Delivery]

```



> \*\*Current integration boundary:\*\* The local voice interface is not yet connected to incoming cellular calls on a Jio SIM. SMS confirmation currently operates in mock mode and does not deliver real text messages.



\### Technology stack



| Component | Technology | Responsibility |

|---|---|---|

| Language | Python | Application logic and integrations |

| AI model | Google Gemini | Natural-language understanding and response generation |

| API | FastAPI | HTTP endpoints and backend access |

| Database | SQLite | Persistent appointment records |

| Voice | Speech recognition and Edge TTS | Local voice interaction |

| Scheduling | Python tools | Availability, validation, booking, and cancellation |

| SMS | Custom SMS service | Confirmation message generation and mock delivery |

| Testing | pytest | Automated regression testing |



\---



\## 🔄 End-to-End Workflows



\### 1. Conversation workflow



```mermaid

sequenceDiagram

&#x20;   participant User

&#x20;   participant Agent as Python AI Agent

&#x20;   participant Gemini

&#x20;   participant Tools as Business Tools



&#x20;   User->>Agent: Ask a question or request a booking

&#x20;   Agent->>Gemini: Interpret the request

&#x20;   Gemini-->>Agent: Response or tool decision

&#x20;   Agent->>Tools: Execute required business operation

&#x20;   Tools-->>Agent: Validated result

&#x20;   Agent-->>User: Natural-language response

```



\### 2. Appointment booking workflow



```mermaid

flowchart TD

&#x20;   A\[Customer requests appointment] --> B\[Collect booking details]

&#x20;   B --> C\[Validate date and time]

&#x20;   C --> D{Slot available?}

&#x20;   D -- No --> E\[Offer alternative slots]

&#x20;   E --> B

&#x20;   D -- Yes --> F\[Ask customer to confirm]

&#x20;   F --> G{Confirmed?}

&#x20;   G -- No --> H\[Continue conversation]

&#x20;   G -- Yes --> I\[Save appointment to SQLite]

&#x20;   I --> J\[Generate confirmation message]

&#x20;   J --> K\[Mock SMS result]

&#x20;   K --> L\[Return booking status]

```



\### 3. Appointment confirmation workflow



1\. The customer confirms the proposed booking.

2\. The scheduler creates the appointment record.

3\. The agent passes the saved appointment details to the SMS service.

4\. The service formats a message containing the date, time, duration, purpose, and booking reference.

5\. In the current mock configuration, the service simulates delivery and masks the recipient's phone number in its returned result.



\*\*Mock delivery is not real SMS delivery.\*\* A live SMS provider or supported phone-based integration must be implemented and tested separately.



\---



\## 📁 Project Structure



```text

ai\_voice\_agent/

├── app/

│   ├── agent.py                 # Conversational agent and booking flow

│   ├── api.py                   # FastAPI application

│   ├── contacts.py              # Contact-related logic

│   ├── context.py               # Conversation context

│   ├── conversation.py          # Conversation state and management

│   ├── date\_resolver.py         # Date and time resolution

│   ├── gemini\_client.py         # Gemini integration

│   ├── main.py                  # CLI entry point

│   ├── scheduler.py             # Appointment scheduling and persistence

│   ├── sms\_service.py           # Confirmation message service

│   └── voice.py                 # Local voice interface

├── data/                        # Local database files

├── knowledge/

│   ├── company\_context.json     # Business information

│   └── contacts.json            # Contact information

├── tests/                       # Automated test suite

├── .env.example                 # Environment configuration template

├── .gitignore

├── README.md

└── requirements.txt

```



The tree above highlights the primary application modules; additional project files may exist in the repository.



\---



\## ⚙️ Getting Started



\### Prerequisites



\- Python 3.11 or newer recommended

\- Git

\- A Google Gemini API key

\- Windows, macOS, or Linux



\### 1. Clone the repository



```bash

git clone https://github.com/HarshaAlamanda/ai\_voice\_agent.git

cd ai\_voice\_agent

```



\### 2. Create a virtual environment



\*\*Windows CMD:\*\*



```cmd

python -m venv .venv

.venv\\Scripts\\activate

```



\*\*macOS / Linux:\*\*



```bash

python3 -m venv .venv

source .venv/bin/activate

```



\### 3. Install dependencies



```bash

python -m pip install --upgrade pip

pip install -r requirements.txt

```



\### 4. Configure environment variables



Copy the example file:



\*\*Windows CMD:\*\*



```cmd

copy .env.example .env

```



\*\*macOS / Linux:\*\*



```bash

cp .env.example .env

```



Open `.env` and add your own valid Gemini API key using the variable name expected by the application.



\*\*Never commit `.env`, API keys, credentials, or private customer data to GitHub.\*\*



\### 5. Start the API server



```bash

python -m uvicorn app.api:app --reload

```



Open these local URLs:



\- API health check: `http://127.0.0.1:8000/health`

\- Interactive API documentation: `http://127.0.0.1:8000/docs`



The API server is intended for local development in this setup. Production deployment requires appropriate HTTPS, authentication, and configuration.



\### 6. Run the test suite



```bash

python -m pytest -v

```



The project has previously passed \*\*60 automated tests\*\* in the development environment. Run the command above on your current checkout to verify its status.



\---



\## 🔐 Configuration and Security



\- Keep API keys in `.env`, not in source code.

\- Use `.env.example` for placeholder configuration only.

\- Do not publish databases containing personal or customer information.

\- Protect API endpoints with authentication before exposing them publicly.

\- Use HTTPS and secure secret management in production.

\- Avoid logging full phone numbers, authentication tokens, or private conversation content.



\---



\## 🚧 Roadmap



| Feature | Status |

|---|---|

| Gemini-powered AI agent | Implemented |

| FastAPI backend | Implemented |

| Appointment scheduling and SQLite persistence | Implemented |

| Date/time and availability workflows | Implemented |

| Local voice interface | Implemented |

| Booking confirmation message generation | Implemented |

| Mock SMS delivery | Implemented |

| Dedicated SMS integration with real delivery | Planned |

| Incoming cellular call answering on existing Jio SIM | Under investigation |

| Website dashboard and mobile-number verification | Planned |

| Production deployment, authentication, and monitoring | Planned |



Statuses describe the current development state and should be updated as integrations are completed and verified.



\---



\## 🧪 Testing



Run the full suite:



```bash

python -m pytest -v

```



The tests cover key agent behavior, booking confirmation, conversation flow, scheduling, and date/time handling.



\---



\## 🎯 Project Goals



The long-term objective is to build a reliable AI receptionist that can:



\- Handle customer conversations naturally.

\- Answer business-related questions.

\- Check availability and book appointments.

\- Maintain consistent appointment records.

\- Send booking confirmations through a verified messaging integration.

\- Connect to a real-time voice channel when a technically supported telephony integration is available.



\---



\## 👨‍💻 Author



\*\*Harsha Alamanda\*\*



GitHub: \[@HarshaAlamanda](https://github.com/HarshaAlamanda)



Project: \[ai\_voice\_agent](https://github.com/HarshaAlamanda/ai\_voice\_agent)



\---



<p align="center">

&#x20; <strong>Built with Python, AI, and a focus on practical automation.</strong>

</p>



