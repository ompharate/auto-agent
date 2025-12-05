from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from state import AgentState


def executor_node(state: AgentState) -> AgentState:
    """Execute the identified task and return formatted results."""

    task = state.get("task", "general_qa")
    extracted_text = state.get("extracted_text", "")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.2
    )

    try:
        if task == "summarization":
            prompt = f"""
                Summarize the following text in 3 formats:

                Text:
                {extracted_text}

                Provide your response in this exact markdown format:

                **One-line Summary:**
                [one line here]

                **Three Bullet Points:**
                - [point 1]
                - [point 2]
                - [point 3]

                **Five Sentences:**
                1. [sentence 1]
                2. [sentence 2]
                3. [sentence 3]
                4. [sentence 4]
                5. [sentence 5]
                """

        elif task == "sentiment":
            prompt = f"""
                Analyze the sentiment of the following text:

                Text:
                {extracted_text}

                Provide your response in this format:

                **Sentiment:** [positive/negative/neutral]

                **Confidence:** [0-100]%

                **Explanation:**
                [brief explanation]
                """

        elif task == "code_explain":
            prompt = f"""
                Analyze the following code:

                Code:
                {extracted_text}

                Provide your response in this format:

                **What it does:**
                [explanation]

                **Potential Bugs:**
                - [bug 1 or "None detected"]
                - [bug 2 if any]

                **Time Complexity:**
                [complexity analysis]
                """

        elif task == "youtube_transcript":
            prompt = f"""
                Summarize the following YouTube video transcript in 3 formats:

                Transcript:
                {extracted_text}

                Provide your response in this exact markdown format:

                **One-line Summary:**
                [one line here]

                **Three Bullet Points:**
                - [point 1]
                - [point 2]
                - [point 3]

                **Five Sentences:**
                1. [sentence 1]
                2. [sentence 2]
                3. [sentence 3]
                4. [sentence 4]
                5. [sentence 5]
                """

        else:
            prompt = f"""Answer the following question or request clearly and concisely.

            Use markdown formatting for better readability (headings, lists, code blocks, etc.).

            Question:
            {extracted_text}"""

        messages = [
            SystemMessage(content="You are a helpful assistant. Always respond using proper markdown formatting with headers, lists, and clear structure."),
            HumanMessage(content=prompt)
        ]

        response = llm.invoke(messages)
        final_result = response.content

        return {
            **state,
            "final_result": final_result,
        }

    except Exception as e:
        return {
            **state,
            "final_result": f"Executor error: {str(e)}",
        }
