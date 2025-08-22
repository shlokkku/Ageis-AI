Aegis AI: Your Pension's Future, In Focus
Live Demo: https://pension-zeta.vercel.app/


🚀 The Vision: From Financial Fog to Future Certainty
The pension landscape is a fog of uncertainty. Members can't see their future, advisors are buried in scattered data, and regulators lack a clear view of systemic risk. Decisions are made on fragments of information, not on a complete picture.

Aegis AI is the navigation system for this fog.

We are an enterprise-grade intelligence platform that cuts through the complexity to deliver a clear, confident path forward for everyone in the pension ecosystem. By transforming fragmented data into predictive, actionable intelligence, we're replacing ambiguity with certainty. It's not just a tool; it's a new standard of clarity for an entire industry.

Stop guessing about the future. Start seeing it.

✨ One Platform, Three Crystal-Clear Realities
Aegis AI delivers a secure, role-based experience tailored to solve the unique challenges of each stakeholder.

For the Member: Your Personal Financial Co-pilot
We empower members to take control of their financial destiny with an AI that speaks their language.

Interactive Future-Mapping: Go beyond static reports. Ask "What if I retire at 55?" or "How do I increase my pension by 20%?" and get instant, easy-to-understand projections.

Effortless Document Intelligence: Upload your pension statements and ask direct questions. Our AI reads the fine print so you don't have to.

24/7 Financial Clarity: Get secure, conversational answers about your pension's health and security, anytime you need them.

For the Advisor: From Data Overload to Decisive Action
We turn hours of analysis into seconds of insight, freeing advisors to focus on what matters: their clients.

The 360° Client Intelligence Hub: Instantly access a unified view of a client's risk profile, fraud indicators, and asset allocation without juggling multiple systems.

Proactive Opportunity Engine: Our AI doesn't just answer questions—it surfaces them. Identify at-risk clients or growth opportunities across your entire portfolio automatically.

Build Trust Faster: Generate data-driven, personalized recommendations with AI-backed explanations, solidifying your role as a trusted advisor.

For the Regulator: Systemic Insight, On Demand
We provide the macro-view needed to ensure compliance and safeguard the stability of the entire pension system.

The Macro-View Cockpit: See real-time, anonymized analytics on risk distribution, demographic trends, and asset allocation across the entire fund.

AI-Powered Compliance Co-pilot: Ask critical oversight questions like, "Flag all funds with high-risk exposure to members nearing retirement" or "Generate a summary of all anomalous activity this quarter."

Explainable & Auditable AI: Every insight is delivered with structured, transparent reasoning, providing the reliability needed for regulatory confidence.

🧠 The Aegis Engine: A Collaborative AI Workforce
This isn't just another AI chatbot. Aegis is powered by a sophisticated multi-agent system—a team of specialized AIs working in concert, orchestrated by LangGraph.

How It Works:
User Query: A user asks a question through their tailored dashboard.

AI Supervisor: A central supervisor agent analyzes the query's strategic intent.

Intelligent Delegation: The supervisor assigns the task to the right specialist—our Fraud Detection Agent, Risk Analysis Agent, or Projection Specialist.

Hybrid Intelligence:

ML First: The agent first leverages a custom-trained XGBoost model for a rapid, statistically powerful prediction (like a fraud score).

LLM Reasoning: This data-driven insight is then passed to a Google Gemini reasoning engine, which crafts a detailed, human-readable explanation and actionable recommendation.

Trusted Results: The final, structured answer is returned to the user, backed by both machine-learning accuracy and LLM-powered context.

This hybrid approach delivers the best of both worlds: the raw predictive power of fine-tuned ML and the sophisticated, explainable reasoning of a world-class LLM.

🛠️ Technology Stack
Frontend: React, Tailwind CSS, Plotly.js

Backend: FastAPI (Python), Deployed on Render

Database: MySQL, Deployed on Railway

Vector Store: ChromaDB for RAG on documents and FAQs

AI Orchestration: LangGraph

LLM: Google Gemini 1.5 Pro & Flash

Machine Learning: XGBoost, Scikit-learn, SMOTE

🚀 How to Run Locally
1. Clone the Repository
git clone https://github.com/shlokkku/pension-ai-api.git

2. Setup the Backend
# Navigate to the server directory
cd pension-ai-api/server

# Create a virtual environment and activate it
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Set up your .env file with your database URL and Gemini API key

# Run the data import script
python -m app.import_data

# Start the server
uvicorn app.main:app --reload

3. Setup the Frontend
# Navigate to the client directory in a new terminal
cd pension-ai-api/client

# Install dependencies
npm install

# Start the development server
npm run dev

# To build the production-ready code
npm run build
