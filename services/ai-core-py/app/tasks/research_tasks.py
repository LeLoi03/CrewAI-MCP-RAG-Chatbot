# app/tasks/research_tasks.py
from crewai import Task

conference_research_task = Task(
    description=(
        "Analyze the user's request: '{query}'.\n"
        "First, determine the user's intent. \n"
        "- If the user is asking a simple question, making a greeting (like 'hello', 'hi', 'xin chào'), or having a general conversation, answer it directly in a friendly and helpful manner. \n"
        "- If the user's request is clearly about finding information on tech conferences (e.g., asking for dates, locations, topics, or details of conferences), you MUST delegate this task to the 'Conference Research Specialist'. \n"
        "- Your final response should be a complete and helpful answer synthesized from your own knowledge or the results from the specialist."
    ),
    expected_output=(
        "A comprehensive and helpful answer to the user. This could be a simple greeting, a direct answer to a question, or a formatted list of conferences provided by the specialist agent."
    ),
)