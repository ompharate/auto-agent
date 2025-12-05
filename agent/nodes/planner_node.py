from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState
import json
import re


def planner_node(state: AgentState) -> AgentState:
    """Determine user's task and decide if clarification is needed."""

    extracted_text = state.get("extracted_text", "")
    is_youtube = state.get("is_youtube", False)

    if is_youtube:
        return {
            **state,
            "task": "youtube_transcript",
            "needs_clarification": False,
            "clarification_question": None,
            "plan": ["YouTube transcript detected", "Will summarize in 3 formats"],
        }

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0
    )

    planning_prompt = f"""
        You are an intent-classification and task-planning assistant inside a LangGraph agent.

        Your job: Determine the user's task from ONE of these:
        - summarization
        - sentiment
        - code_explain
        - youtube_transcript
        - general_qa
        - unclear

        Rules:
        - Summarization ALWAYS includes 1-line + 3-bullets + 5-sentences.
        - If text is ambiguous, choose "unclear".
        - If input contains a YouTube link → task = youtube_transcript.
        - If the input seems like code → task = code_explain.
        - If user expresses emotion → task = sentiment.
        - If user asks a question → task = general_qa.

        Return STRICT JSON:

        {{
        "task": "<task_name>",
        "needs_clarification": true/false,
        "clarification_question": "<question or empty>",
        "reasoning": ["step1", "step2", "..."]
        }}

        User text:
        \"\"\"{extracted_text}\"\"\"
        """

    try:
        messages = [
            SystemMessage(content="You are a precise JSON-producing planner."),
            HumanMessage(content=planning_prompt)
        ]

        response = llm.invoke(messages)
        raw = response.content.strip()

        try:
            data = json.loads(raw)
        except:
            json_str = raw[raw.find("{"): raw.rfind("}")+1]
            data = json.loads(json_str)

        task = data.get("task", "general_qa")
        needs_clarification = data.get("needs_clarification", False)
        clarification_question = data.get("clarification_question", "")
        reasoning = data.get("reasoning", [])

        if task == "unclear":
            needs_clarification = True
            clarification_question = "What would you like me to do with this text? Summarize, analyze sentiment, explain code, or something else?"

        return {
            **state,
            "task": task,
            "needs_clarification": needs_clarification,
            "clarification_question": clarification_question,
            "plan": reasoning,
        }

    except Exception as e:
        return {
            **state,
            "task": "general_qa",
            "needs_clarification": False,
            "clarification_question": "",
            "plan": ["Planner encountered an error"],
        }
