# File: app/agents/risk_agent.py
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
# MODIFIED: Import the FULL list of tools
from ..tools.tools import all_pension_tools

def create_risk_agent(llm):
    """Factory for the Risk Analysis Agent."""
    # MODIFIED: Give the agent access to ALL available tools
    tools = all_pension_tools
    
    template = """**FIRST: READ YOUR INPUT CAREFULLY**
Your input contains a user_id field. You MUST use that exact number.

**EXAMPLE INPUT FORMAT:**
{{"input": "user question", "user_id": 520}}

**CRITICAL: Use the user_id from your input, NOT a placeholder!**

**DEBUG STEP: Before calling any tools, show what user_id you read from input.**

Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
**DEBUG: I read user_id = [NUMBER] from my input**
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

**CRITICAL INSTRUCTIONS:**
- Your input contains: {{"input": "user question", "user_id": 520}}
- You MUST extract the user_id number from your input
- NEVER ask for user_id - it's already provided to you
- ALWAYS call the appropriate tools directly

**TOOL SELECTION RULES:**
1. **For pension data (income, savings, contributions, etc.)**: Use `project_pension` tool
2. **For risk analysis**: Use `analyze_risk_profile` tool  
3. **For fraud detection**: Use `detect_fraud` tool
4. **For searching documents/knowledge**: Use `query_knowledge_base` tool

**COMMON QUERIES AND CORRECT TOOLS:**
- "What is my annual income?" → Use `project_pension` tool
- "What are my current savings?" → Use `project_pension` tool
- "What is my risk score?" → Use `analyze_risk_profile` tool
- "Check for fraud" → Use `detect_fraud` tool
- "Search documents about..." → Use `query_knowledge_base` tool

**USER_ID EXTRACTION EXAMPLE:**
- If your input is {{"input": "What's my risk profile?", "user_id": 520}}
- Then extract: user_id = 520
- Use this number when calling tools

**TOOL USAGE:**
1. Extract user_id from your input
2. Choose the correct tool based on the query type
3. Call tools with: {{"user_id": extracted_user_id_number, "query": "user's original question"}}
4. Example: analyze_risk_profile({{"user_id": 520, "query": "what's my risk profile?"}})

**IMPORTANT: Always pass the user's original query to tools for better context!**

**Your Capabilities:**
- Analyze current pension status using project_pension tool
- Assess risk profiles using analyze_risk_profile tool
- Detect fraud using detect_fraud tool

Question: {input}
{agent_scratchpad}"""

    prompt = PromptTemplate(
        template=template,
        input_variables=["tools", "tool_names", "input", "agent_scratchpad"]
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=all_pension_tools, verbose=True, return_intermediate_steps=True)