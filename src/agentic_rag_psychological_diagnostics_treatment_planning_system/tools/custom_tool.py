from crewai.tools import BaseTool, tool
from typing import Type
from pydantic import BaseModel, Field


@tool("Ask Human follow up questions")
def ask_human(question: str) -> str:
    """
    Ask human follow up questions during diagnostic interview.
    Use this tool to gather information from the patient throughout the diagnostic process.
    
    Args:
        question (str): The question to ask the human/patient
        
    Returns:
        str: The human's response to the question
    """
    print(f"\n🔹 {question}")
    response = input("> ")
    return response


class MyCustomToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    argument: str = Field(..., description="Description of the argument.")

class MyCustomTool(BaseTool):
    name: str = "Name of my tool"
    description: str = (
        "Clear description for what this tool is useful for, your agent will need this information to use it."
    )
    args_schema: Type[BaseModel] = MyCustomToolInput

    def _run(self, argument: str) -> str:
        # Implementation goes here
        return "this is an example of a tool output, ignore it and move along."
