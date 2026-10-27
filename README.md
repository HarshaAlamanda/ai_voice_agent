&#x20;<!--

&#x20; AI VOICE AGENT

&#x20; Premium GitHub README

&#x20; Repository: HarshaAlamanda/ai\_voice\_agent

\-->



<div align="center">



\# ◈ AI VOICE AGENT



\### INTELLIGENT CONVERSATION. DETERMINISTIC EXECUTION. PERSISTENT MEMORY.



\*\*An AI-powered receptionist architecture for conversational business automation, appointment orchestration, and voice-enabled customer experiences.\*\*



<br/>



<a href="https://github.com/HarshaAlamanda/ai\_voice\_agent">

&#x20; <img src="https://img.shields.io/badge/PROJECT-AI%20VOICE%20AGENT-8B5CF6?style=for-the-badge\&labelColor=09090B" alt="AI Voice Agent"/>

</a>

<a href="https://fastapi.tiangolo.com/">

&#x20; <img src="https://img.shields.io/badge/API-FastAPI-009688?style=for-the-badge\&logo=fastapi\&logoColor=white\&labelColor=09090B" alt="FastAPI"/>

</a>

<a href="https://ai.google.dev/gemini-api/docs">

&#x20; <img src="https://img.shields.io/badge/AI-Google%20Gemini-4285F4?style=for-the-badge\&logo=googlegemini\&logoColor=white\&labelColor=09090B" alt="Google Gemini"/>

</a>

<a href="https://www.sqlite.org/">

&#x20; <img src="https://img.shields.io/badge/DATA-SQLite-003B57?style=for-the-badge\&logo=sqlite\&logoColor=white\&labelColor=09090B" alt="SQLite"/>

</a>



<br/><br/>



\[Architecture](#-system-architecture) ·

\[Workflows](#-end-to-end-workflows) ·

\[Engineering](#-engineering-design) ·

\[API](#-api-and-local-development) ·

\[Testing](#-test-strategy) ·

\[Security](#-security-and-operational-considerations)



<br/>



> A practical exploration of how a language model, deterministic business logic, persistent storage, and voice interfaces can work together to automate receptionist workflows.



</div>



\---



\## 01 — The vision



Traditional receptionist workflows often involve repetitive conversations, manual appointment coordination, repeated availability checks, and follow-up messages.



\*\*AI Voice Agent\*\* is a Python-based project designed to bring these workflows into a single conversational system.



Rather than allowing a language model to independently control every operation, the architecture separates conversational intelligence from business execution:



\- \*\*Gemini\*\* interprets requests and generates natural-language responses.

\- \*\*Python tools\*\* perform application-defined business operations.

\- \*\*The scheduling layer\*\* validates availability and manages appointments.

\- \*\*SQLite\*\* persists appointment records.

\- \*\*FastAPI\*\* exposes backend functionality over HTTP.

\- \*\*Voice and messaging modules\*\* provide integration points for human-facing interactions.



The goal is to build a receptionist that is conversational on the surface and predictable underneath.



\### Core engineering principle



```text

LLM for language.

Python for decisions that must be validated.

Database for persistent state.

APIs for integration.

Tests for confidence.

```



This separation is central to making conversational automation more maintainable and easier to test.



\---



\## 02 — Capability overview



| Capability | Current implementation |

|---|---|

| Conversational AI | Gemini integration |

| Application backend | FastAPI |

| Business logic | Python agent and tools |

| Appointment availability | Scheduling module |

| Appointment persistence | SQLite |

| Date and time handling | Dedicated date/time utilities |

| Local voice interaction | Voice module |

| Booking confirmation formatting | SMS service |

| SMS delivery simulation | Mock mode |

| Incoming cellular call answering | Not yet integrated |

| Live SMS delivery | Not yet integrated |

| Browser-based management dashboard | Not yet implemented |



> \*\*Implementation status matters.\*\* Local voice interaction, live cellular telephony, browser-based calling, and real SMS delivery are different capabilities; one should not be presented as proof that the others are complete.



\---



\## 03 — System architecture



The architecture is organized around clear boundaries between the interaction layer, AI reasoning, business operations, persistence, and external integrations.



```mermaid

flowchart TB

&#x20;   subgraph CLIENT\["01 · INTERACTION LAYER"]

&#x20;       CLI\["CLI / Text Interface"]

&#x20;       LOCALVOICE\["Local Voice Interface"]

&#x20;       FUTUREWEB\["Future Web Dashboard"]

&#x20;   end



&#x20;   subgraph BACKEND\["02 · APPLICATION LAYER"]

&#x20;       API\["FastAPI Application"]

&#x20;       STATE\["Conversation State"]

&#x20;       AGENT\["Python AI Agent"]

&#x20;   end



&#x20;   subgraph INTELLIGENCE\["03 · INTELLIGENCE LAYER"]

&#x20;       GEMINI\["Google Gemini API"]

&#x20;       EXTRACT\["Intent \& Detail Extraction"]

&#x20;       RESPONSE\["Response Generation"]

&#x20;   end



&#x20;   subgraph DOMAIN\["04 · BUSINESS DOMAIN"]

&#x20;       VALIDATE\["Input Validation"]

&#x20;       DATE\["Date \& Time Resolution"]

&#x20;       SCHED\["Appointment Scheduler"]

&#x20;       CONTACTS\["Contact \& Company Context"]

&#x20;   end



&#x20;   subgraph DATA\["05 · PERSISTENCE"]

&#x20;       SQLITE\[("SQLite")]

&#x20;       KNOWLEDGE\["Knowledge Files"]

&#x20;   end



&#x20;   subgraph INTEGRATIONS\["06 · INTEGRATION BOUNDARY"]

&#x20;       SMS\["SMS Service"]

&#x20;       MOCK\["Mock Delivery"]

&#x20;       TELEPHONY\["Future Telephony Adapter"]

&#x20;   end



&#x20;   CLI --> AGENT

&#x20;   LOCALVOICE --> AGENT

&#x20;   FUTUREWEB -. "Planned" .-> API

&#x20;   API --> AGENT

&#x20;   AGENT <--> STATE

&#x20;   AGENT <--> GEMINI

&#x20;   GEMINI --> EXTRACT

&#x20;   EXTRACT --> VALIDATE

&#x20;   VALIDATE --> DATE

&#x20;   DATE --> SCHED

&#x20;   AGENT --> RESPONSE

&#x20;   CONTACTS --> AGENT

&#x20;   CONTACTS --> KNOWLEDGE

&#x20;   SCHED <--> SQLITE

&#x20;   SCHED --> SMS

&#x20;   SMS --> MOCK

&#x20;   TELEPHONY -. "Not implemented" .-> API



&#x20;   classDef client fill:#111827,stroke:#818CF8,color:#FFFFFF

&#x20;   classDef backend fill:#172554,stroke:#60A5FA,color:#FFFFFF

&#x20;   classDef ai fill:#312E81,stroke:#A78BFA,color:#FFFFFF

&#x20;   classDef domain fill:#064E3B,stroke:#34D399,color:#FFFFFF

&#x20;   classDef data fill:#3F2D0B,stroke:#FBBF24,color:#FFFFFF

&#x20;   classDef integration fill:#3F1D2E,stroke:#F472B6,color:#FFFFFF



&#x20;   class CLI,LOCALVOICE,FUTUREWEB client

&#x20;   class API,STATE,AGENT backend

&#x20;   class GEMINI,EXTRACT,RESPONSE ai

&#x20;   class VALIDATE,DATE,SCHED,CONTACTS domain

&#x20;   class SQLITE,KNOWLEDGE data

&#x20;   class SMS,MOCK,TELEPHONY integration

```



\### Architectural boundaries



\*\*Interaction layer\*\*



Accepts user input and presents responses. The existing project includes CLI and local voice components. A browser dashboard remains a future extension.



\*\*Application layer\*\*



FastAPI provides HTTP entry points, while the agent coordinates conversation state, AI requests, and business tools.



\*\*Intelligence layer\*\*



Gemini provides language understanding and response generation. The application remains responsible for validating tool inputs and deciding whether an operation can proceed.



\*\*Business domain\*\*



Python modules handle date resolution, scheduling rules, contact information, and appointment workflows.



\*\*Persistence layer\*\*



SQLite stores structured appointment records. Knowledge files provide business and contact context.



\*\*Integration boundary\*\*



SMS and telephony should remain separate adapters. This makes it possible to develop and test business logic without requiring live telecom connectivity.



\---



\## 04 — End-to-end workflows



\### Workflow A · Conversational request



```mermaid

sequenceDiagram

&#x20;   autonumber

&#x20;   participant U as User

&#x20;   participant A as AI Agent

&#x20;   participant G as Gemini

&#x20;   participant T as Python Tools



&#x20;   U->>A: Submit a question or request

&#x20;   A->>G: Request interpretation or response

&#x20;   G-->>A: Language response or tool decision

&#x20;   opt A business operation is required

&#x20;       A->>T: Invoke the appropriate application logic

&#x20;       T->>T: Validate inputs and business rules

&#x20;       T-->>A: Return the operation result

&#x20;       A->>G: Generate a response using the result

&#x20;       G-->>A: Natural-language answer

&#x20;   end

&#x20;   A-->>U: Return the conversational response

```



\*\*Why this separation matters:\*\* A generated sentence is not equivalent to a completed transaction. Appointment availability, booking persistence, and confirmation status should be based on application results, not on what the model claims to have done.



\### Workflow B · Appointment booking



```mermaid

flowchart TD

&#x20;   A(\["Incoming booking request"]) --> B\["Extract appointment details"]

&#x20;   B --> C{"Required details available?"}

&#x20;   C -- No --> D\["Ask for missing details"]

&#x20;   D --> B

&#x20;   C -- Yes --> E\["Normalize date and time"]

&#x20;   E --> F\["Validate business hours"]

&#x20;   F --> G{"Within allowed hours?"}

&#x20;   G -- No --> H\["Explain restriction and offer alternatives"]

&#x20;   H --> B

&#x20;   G -- Yes --> I\["Check availability"]

&#x20;   I --> J{"Slot available?"}

&#x20;   J -- No --> K\["Find alternative slots"]

&#x20;   K --> D

&#x20;   J -- Yes --> L\["Present booking details"]

&#x20;   L --> M{"Customer confirms?"}

&#x20;   M -- No --> N\["Revise details or end request"]

&#x20;   M -- Yes --> O\["Create appointment record"]

&#x20;   O --> P{"Save successful?"}

&#x20;   P -- No --> Q\["Report failure and preserve conversation"]

&#x20;   P -- Yes --> R\["Generate confirmation message"]

&#x20;   R --> S\["Invoke configured SMS mode"]

&#x20;   S --> T(\["Return booking result"])



&#x20;   classDef decision fill:#312E81,stroke:#A78BFA,color:#FFFFFF

&#x20;   classDef success fill:#064E3B,stroke:#34D399,color:#FFFFFF

&#x20;   classDef failure fill:#450A0A,stroke:#F87171,color:#FFFFFF

&#x20;   class C,G,J,M,P decision

&#x20;   class O,R,T success

&#x20;   class Q failure

```



\#### Booking invariants



A reliable booking workflow should maintain these conditions:



1\. Required appointment details must be present before confirmation.

2\. Availability must be checked against application scheduling rules.

3\. A booking must not be described as confirmed until persistence succeeds.

4\. Confirmation messages must use the saved appointment details.

5\. Messaging failure must not silently undo an appointment that was successfully saved.

6\. Repeated requests should be handled carefully to avoid duplicate bookings.



These are engineering requirements for a dependable implementation, not claims that every production safeguard is already implemented.



\### Workflow C · Appointment persistence and confirmation



```mermaid

sequenceDiagram

&#x20;   autonumber

&#x20;   participant A as Agent

&#x20;   participant S as Scheduler

&#x20;   participant D as SQLite

&#x20;   participant M as SMS Service



&#x20;   A->>S: Submit confirmed booking

&#x20;   S->>S: Validate scheduling rules

&#x20;   S->>D: Insert appointment

&#x20;   D-->>S: Return persistence result

&#x20;   alt Appointment saved

&#x20;       S-->>A: Return saved appointment details

&#x20;       A->>M: Build confirmation message

&#x20;       M->>M: Check configured SMS mode

&#x20;       M-->>A: Return mock or delivery status

&#x20;       A-->>A: Preserve booking result

&#x20;   else Save failed

&#x20;       S-->>A: Return booking failure

&#x20;       A-->>A: Do not claim success

&#x20;   end

```



The current SMS service formats a confirmation with the meeting date, time, duration, purpose, reference, and support contact. Its default mode simulates delivery; it does not send a real text message.



\---



\## 05 — Engineering design



\### Deterministic business tools



Language models are useful for interpreting flexible human language, but scheduling rules need explicit validation.



The project uses Python modules to separate responsibilities such as:



\- Resolving natural-language date and time expressions.

\- Checking availability and business-hour constraints.

\- Creating, finding, and cancelling appointments.

\- Managing conversation state and required booking details.

\- Accessing company and contact information.

\- Building appointment confirmation messages.



This reduces the risk of allowing unconstrained language generation to become the source of truth for business transactions.



\### Conversation state management



A multi-turn receptionist needs to retain information collected over several messages.



For example:



```text

Customer: I need a meeting tomorrow.

Agent: What time would you prefer?

Customer: 11 AM.

Agent: What is the meeting about?

Customer: My AI project.

Agent: I have the details. Shall I book it?

Customer: Yes, please.

Agent: \[Validates, saves, and reports the actual result]

```



The example illustrates the intended interaction pattern. Actual responses depend on the current agent implementation, required fields, and availability.



\### Persistent scheduling



SQLite provides a local persistence layer without requiring a separate database server.



Typical appointment fields include:



| Field | Purpose |

|---|---|

| Appointment ID | Booking reference |

| Customer name | Identify the appointment owner |

| Email | Optional contact field, depending on workflow |

| Phone | Optional phone contact field |

| Date | Appointment date |

| Start and end time | Scheduling boundaries |

| Duration | Appointment length |

| Purpose | Reason for the meeting |



The scheduler should remain the authoritative source for saved appointment records.



\### Failure handling



The application should distinguish between:



\- AI provider errors.

\- Missing or invalid user input.

\- Unavailable appointment slots.

\- Database failures.

\- SMS delivery failures.

\- Voice transport or speech recognition failures.



These failures should produce meaningful outcomes rather than generic success messages. External integrations should be independently testable wherever possible.



\---



\## 06 — Repository structure



```text

D:\\

└── agentic/

&#x20;   ├── app/

&#x20;   │   ├── \_\_init\_\_.py

&#x20;   │   ├── agent.py

&#x20;   │   ├── api.py

&#x20;   │   ├── contacts.py

&#x20;   │   ├── context.py

&#x20;   │   ├── conversation.py

&#x20;   │   ├── date\_resolver.py

&#x20;   │   ├── gemini\_client.py

&#x20;   │   ├── main.py

&#x20;   │   ├── scheduler.py

&#x20;   │   ├── sms\_service.py

&#x20;   │   └── voice.py

&#x20;   │

&#x20;   ├── data/

&#x20;   │   └── appointments.db

&#x20;   │

&#x20;   ├── knowledge/

&#x20;   │   ├── company\_context.json

&#x20;   │   └── contacts.json

&#x20;   │

&#x20;   ├── tests/

&#x20;   │   ├── conftest.py

&#x20;   │   ├── test\_agent.py

&#x20;   │   ├── test\_booking\_confirmation.py

&#x20;   │   ├── test\_confirmation\_flow.py

&#x20;   │   ├── test\_date\_time.py

&#x20;   │   ├── test\_dates.py

&#x20;   │   ├── test\_scheduler.py

&#x20;   │   └── test\_time\_normalization.py

&#x20;   │

&#x20;   ├── .env.example

&#x20;   ├── .gitignore

&#x20;   ├── README.md

&#x20;   └── requirements.txt

```



The tree highlights the main application and test modules. Check the repository before publishing database files, backups, or customer information.



\---



\## 07 — API and local development



\### Run the application



\*\*Prerequisites\*\*



\- Python 3.11 or newer recommended.

\- Git.

\- A valid Gemini API key.

\- A local development environment.



\#### Step 1 — Clone



```bash

git clone https://github.com/HarshaAlamanda/ai\_voice\_agent.git

cd ai\_voice\_agent

```



\#### Step 2 — Create a virtual environment



Windows CMD:



```cmd

python -m venv .venv

.venv\\Scripts\\activate

```



\#### Step 3 — Install dependencies



```cmd

python -m pip install --upgrade pip

pip install -r requirements.txt

```



\#### Step 4 — Configure secrets



```cmd

copy .env.example .env

notepad .env

```



Add your own valid API key and any other required configuration. Preserve the exact environment variable names expected by the application.



\*\*Never commit `.env` or real API credentials.\*\*



\#### Step 5 — Start FastAPI



```cmd

python -m uvicorn app.api:app --reload

```



| Resource | Local URL |

|---|---|

| API server | `http://127.0.0.1:8000` |

| Health endpoint | `http://127.0.0.1:8000/health` |

| Interactive API documentation | `http://127.0.0.1:8000/docs` |



The health endpoint was previously verified to return a healthy status in the development environment.



> The endpoints above are local development addresses, not public deployment URLs.



\### API documentation



FastAPI provides an interactive OpenAPI interface at `/docs`, allowing developers to inspect available routes and test supported request schemas.



The exact request fields and response models should be taken from the current `app/api.py` implementation rather than assumed from this README.



\---



\## 08 — Test strategy



Run the test suite:



```cmd

python -m pytest -v

```



The project has previously passed \*\*60 automated tests\*\* in the development environment. Re-run the tests on the current checkout to confirm the result.



\### Areas covered



\- Agent behavior and conversational flows.

\- Booking confirmation.

\- Confirmation-state transitions.

\- Date and time handling.

\- Appointment scheduling.

\- Time normalization.



\### Recommended next tests



\- SMS-service unit tests for missing phone numbers and message formatting.

\- Tests confirming that failed SMS delivery does not invalidate a saved booking.

\- API route tests for success and error responses.

\- Duplicate-booking and concurrent-slot scenarios.

\- Tests for missing and malformed environment variables.

\- Integration tests with external services mocked.

\- Tests for phone-number masking and sensitive-data logging.



A passing test suite improves confidence in the current behavior; it does not by itself establish production readiness.



\---



\## 09 — Security and operational considerations



Security must be part of the architecture, especially when handling phone numbers, appointments, and third-party AI services.



\### Secret management



\- Keep real API keys in `.env`.

\- Keep `.env` excluded through `.gitignore`.

\- Use placeholders in `.env.example`.

\- Rotate any credential that has actually been exposed.

\- Use environment-specific secret storage when deploying.



\### Customer data



\- Avoid publishing real appointment databases.

\- Do not commit private customer records or unnecessary backups.

\- Minimize personal information sent to external services.

\- Mask phone numbers in logs wherever practical.

\- Define retention and deletion procedures for customer data.



\### Public API deployment



Before exposing the backend publicly:



\- Configure HTTPS.

\- Add appropriate authentication and authorization.

\- Apply request validation and rate limiting.

\- Configure safe CORS policies where browser clients are used.

\- Add structured logging and error monitoring.

\- Use persistent, backed-up storage appropriate to the deployment.

\- Keep development reload settings disabled in production.



\### Telephony and messaging



An API server does not automatically control an ordinary cellular SIM.



Real incoming-call handling requires a supported telephony or audio-routing integration. Real SMS delivery requires a supported messaging integration and compliance with applicable provider and regulatory requirements.



The existing mock SMS service is a development abstraction, not a live messaging gateway.



\---



\## 10 — Design principles



This project is guided by several practical engineering principles:



\*\*Separation of concerns\*\*  

AI reasoning, scheduling, persistence, and messaging should have clear boundaries.



\*\*Deterministic execution\*\*  

Critical business operations should use explicit validation rather than relying solely on generated language.



\*\*Persistence over assumptions\*\*  

Saved records and tool results determine whether an operation succeeded.



\*\*Graceful degradation\*\*  

An optional integration failure should not silently corrupt an already-completed business operation.



\*\*Testability\*\*  

External APIs should be replaceable with mocks for repeatable automated tests.



\*\*Incremental delivery\*\*  

Build and validate one integration at a time rather than combining untested voice, messaging, and deployment changes.



\---



\## 11 — Future direction



The long-term goal is to develop an AI receptionist that combines natural conversation with dependable business automation.



That means moving beyond a chatbot to a system that can manage conversational context, validate real-world constraints, persist transactions, report outcomes accurately, and connect to supported communication channels.



The next milestone is not simply adding more AI features. It is closing the gap between the working local application and a secure, testable, real-world service.



\---



\## Author



\*\*Harsha Alamanda\*\*



\- GitHub: \[@HarshaAlamanda](https://github.com/HarshaAlamanda)

\- Repository: \[AI Voice Agent](https://github.com/HarshaAlamanda/ai\_voice\_agent)



\---



<div align="center">



\### ENGINEERED FOR CONVERSATION. BUILT FOR EXECUTION.



\*AI · Automation · Voice · Scheduling · Backend Engineering\*



</div>



