Prism AI: See Your Pension in Full Spectrum
Live Demo: [Link to your deployed Vercel frontend]

Video Walkthrough: [Link to a 2-minute YouTube demo video]

🚀 The Vision: From Complexity to Clarity
Pension data is like a single beam of white light—it holds immense potential, but its true components are hidden within a complex, unified stream. To make confident decisions, every stakeholder needs to see the full spectrum of insights that data contains.

Prism AI is an enterprise-grade intelligence platform that acts as a financial prism for the entire pension ecosystem. It takes complex, siloed data and transforms it into a clear spectrum of actionable insights, providing a tailored view for Members, Advisors, and Regulators.

The Regulator Dashboard provides a high-level, anonymized view for compliance and systemic risk analysis.

✨ Key Features: A Tailored Spectrum for Every Role
Prism AI provides a unique, secure, and role-based experience for each user, ensuring they see the exact "colors" of data they need.

For the Member
A personalized, conversational AI assistant that illuminates their financial journey.

Conversational Insights: Ask complex questions in natural language, like "What's my projected pension?" or "How secure is my pension?"

Document Understanding (RAG): Upload PDF statements and ask questions about them directly.

Clear Projections: Receive easy-to-understand forecasts and recommendations.

For the Advisor
A powerful dashboard for efficient client management and data-driven advice.

Client Portfolio Analysis: Get instant summaries of a client's risk profile, asset allocation, and fraud indicators.

AI-Powered Recommendations: Leverage the AI assistant to identify opportunities and risks across the client base.

Streamlined Workflow: Quickly access the information needed to provide high-quality, personalized advice.

For the Regulator
A high-level, anonymized oversight dashboard for compliance and systemic risk monitoring.

Fund-Wide Analytics: Instantly view aggregated data on risk distribution, asset allocation, and demographic trends across the entire fund.

AI Regulatory Assistant: Ask global questions like, "Show high-risk members nearing retirement" or "Summarize all suspicious activity this month."

Reliable & Auditable AI: Our agents provide structured, explainable outputs, ensuring transparency and trust for compliance purposes.

🧠 The Prism Engine: A Multi-Agent Supervisor System
Our backend is not a single, monolithic AI; it's a sophisticated multi-agent system designed for specialized, expert analysis. This architecture combines the predictive power of custom Machine Learning models with the advanced reasoning of Google's Gemini LLM, all orchestrated by LangGraph. By delegating tasks to a team of expert agents, we ensure that the right AI is always on the right job, leading to higher accuracy and reliability.

How It Works:
User Query: A user asks a question through their role-specific dashboard.

AI Supervisor: A central supervisor agent, built with LangGraph, analyzes the query's intent.

Intelligent Routing: The supervisor intelligently routes the request to the correct specialized agent—such as our Fraud Agent or Risk Analyst.

Hybrid Analysis:

ML First Pass: The agent first uses a custom-trained XGBoost model for a rapid, highly accurate statistical prediction (e.g., a fraud score).

LLM Reasoning: The agent then passes this score and the raw data to a Gemini-powered reasoning engine to provide a detailed, human-readable explanation and final recommendation.

Secure, Accurate Results: The agent returns a structured, reliable answer to the user, with built-in guardrails to prevent hallucinations and ensure data privacy.

This hybrid, two-stage approach gives us the best of both worlds: the raw predictive accuracy of a fine-tuned ML model and the sophisticated, explainable reasoning of a state-of-the-art LLM.

🛠️ Technology Stack
Frontend: React, Tailwind CSS, Plotly.js

Backend: FastAPI (Python), Deployed on Render

Database: MySQL, Deployed on Railway

Vector Store: ChromaDB for RAG on documents and FAQs

AI Orchestration: LangGraph

LLM: Google Gemini 1.5 Pro & Flash

Machine Learning: XGBoost, Scikit-learn, SMOTE

🚀 How to Run Locally
Clone the repository:

git clone https://github.com/shlokkku/pension-ai-api.git

Setup the Backend:

Navigate to the server directory.

Create a virtual environment and install dependencies: pip install -r requirements.txt.

Set up your .env file with your database URL and Gemini API key.

Run the data import script: python -m app.import_data.

Start the server: uvicorn app.main:app --reload.

Setup the Frontend:

Navigate to the client directory.

Install dependencies: npm install.

Build the production-ready code:

npm run build

Start the development server:

npm run dev
