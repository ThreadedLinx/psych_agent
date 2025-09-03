import os
from crewai import LLM
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import (
	PDFSearchTool,
	SerperDevTool
)
# Removed HumanTool import - now using message-based approach




@CrewBase
class AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew:
    """AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystem crew"""

    
    @agent
    def conversational_diagnostic_coordinator(self) -> Agent:
        
        embedding_config_pdfsearchtool = dict(
            llm=dict(
                provider="openai",
                config=dict(
                    model="gpt-4o",
                ),
            ),
            embedder=dict(
                provider="openai",
                config=dict(
                    model="text-embedding-3-large",
                ),
            ),
        )
        
        # PDFSearchTool - initialize empty then add PDFs dynamically
        pdf_tool = PDFSearchTool(config=embedding_config_pdfsearchtool)
        
        # Dynamically load all PDFs from knowledge directory
        knowledge_dir = "knowledge"
        if os.path.exists(knowledge_dir):
            for filename in os.listdir(knowledge_dir):
                if filename.endswith('.pdf'):
                    pdf_path = os.path.join(knowledge_dir, filename)
                    pdf_tool.add(pdf_path)
        
        return Agent(
            config=self.agents_config["conversational_diagnostic_coordinator"],
            tools=[
				pdf_tool,
				SerperDevTool()
            ],
            reasoning=False,
            max_reasoning_attempts=None,
            inject_date=True,
            allow_delegation=False,
            max_iter=25,
            max_rpm=None,
            max_execution_time=None,
            llm=LLM(
                model="gpt-4o-mini",
                temperature=0.7,
            ),
        )
    
    # @agent
    # def treatment_plan_writer(self) -> Agent:
    #     
    #     embedding_config_pdfsearchtool = dict(
    #         llm=dict(
    #             provider="openai",
    #             config=dict(
    #                 model="gpt-4o",
    #             ),
    #         ),
    #         embedder=dict(
    #             provider="openai",
    #             config=dict(
    #                 model="text-embedding-3-large",
    #             ),
    #         ),
    #     )
    #     
    #     # PDFSearchTool - initialize empty then add PDFs dynamically
    #     pdf_tool = PDFSearchTool(config=embedding_config_pdfsearchtool)
    #     
    #     # Dynamically load all PDFs from knowledge directory
    #     knowledge_dir = "knowledge"
    #     if os.path.exists(knowledge_dir):
    #         for filename in os.listdir(knowledge_dir):
    #             if filename.endswith('.pdf'):
    #                 pdf_path = os.path.join(knowledge_dir, filename)
    #                 pdf_tool.add(pdf_path)
    #     
    #     return Agent(
    #         config=self.agents_config["treatment_plan_writer"],
    #         tools=[
	# 				SerperDevTool(),
	# 				pdf_tool
    #         ],
    #         reasoning=False,
    #         max_reasoning_attempts=None,
    #         inject_date=True,
    #         allow_delegation=False,
    #         max_iter=25,
    #         max_rpm=None,
    #         max_execution_time=None,
    #         llm=LLM(
    #             model="gpt-4o-mini",
    #             temperature=0.7,
    #         ),
    #     )
    

    
    @task
    def conversational_message_response(self) -> Task:
        return Task(
            config=self.tasks_config["conversational_message_response"],
            markdown=False,
        )
    
    # @task
    # def professional_treatment_plan_creation(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["professional_treatment_plan_creation"],
    #         markdown=False,
    #     )
    

    @crew
    def crew(self) -> Crew:
        """Creates the AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystem crew"""
        return Crew(
            agents=[self.conversational_diagnostic_coordinator()],  # Only conversational agent
            tasks=[self.conversational_message_response()],  # Only conversational task
            process=Process.sequential,
            memory=True,  # Enable memory for patient conversation continuity
            verbose=True,
        )
