#!/usr/bin/env python
import sys
from agentic_rag_psychological_diagnostics_treatment_planning_system.crew import AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    print("\n=== Agentic Psychological Diagnostics & Treatment Planning System ===\n")
    
    print("Welcome! I'm here to conduct a comprehensive psychological assessment.")
    print("This will be an interactive conversation where I'll ask you questions to understand your concerns.\n")
    
    # Get basic patient information
    print("To get started, could you please share your name and initial concerns?")
    initial_input = input("> ").strip()
    
    if not initial_input:
        initial_input = "Patient requested general psychological assessment"
    
    # Simple inputs - the agent will conduct the full interactive assessment
    inputs = {
        'patient_concerns': initial_input,
        'diagnosed_condition': 'To be determined through interactive assessment',
        'selected_treatment_option': 'To be selected through patient interaction'
    }
    
    print("\n" + "="*60)
    print("STARTING INTERACTIVE DIAGNOSTIC ASSESSMENT")
    print("="*60 + "\n")
    
    AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        'patient_concerns': 'sample_value',
        'diagnosed_condition': 'sample_value',
        'selected_treatment_option': 'sample_value'
    }
    try:
        AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        'patient_concerns': 'sample_value',
        'diagnosed_condition': 'sample_value',
        'selected_treatment_option': 'sample_value'
    }
    try:
        AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
