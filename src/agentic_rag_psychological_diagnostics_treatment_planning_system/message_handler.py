"""
Message Handler for Conversational Psychological Diagnostic Agent
Processes individual user messages and maintains session state
"""

from typing import Dict, Any, List
from .crew import AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew


class ConversationState:
    """Manages conversation state for diagnostic session"""
    
    def __init__(self):
        self.current_step = 1
        self.patient_info = {}
        self.conversation_history = []
        self.symptoms = {}
        self.temporal_patterns = {}
        self.functional_impact = {}
        self.diagnosis = None
        self.treatment_options = []
        self.selected_treatment = None
        self.assessment_complete = False
        self.treatment_plan_generated = False
        
        # Enhanced tracking for collected information
        self.symptoms_collected = {
            'severity': None,
            'frequency': None,
            'triggers': [],
            'onset': None,
            'specific_symptoms': [],
            'eating_issues': None,
            'sleep_issues': None,
            'reality_perception': None,
            'physical_symptoms': []
        }
        
        self.duration_info = {
            'symptom_duration': None,
            'pattern': None,  # episodic vs continuous
            'worst_period': None,
            'best_period': None,
            'changes_over_time': None
        }
        
        self.functional_impact_info = {
            'work_impact': None,
            'relationship_impact': None,
            'daily_activities': None,
            'self_care': None,
            'coping_mechanisms': [],
            'support_system': None
        }
        
        # Track step completion status
        self.step_completion_status = {
            1: {'complete': False, 'required_fields': ['severity', 'frequency', 'triggers', 'specific_symptoms']},
            2: {'complete': False, 'required_fields': ['symptom_duration', 'pattern']},
            3: {'complete': False, 'required_fields': ['work_impact', 'daily_activities', 'coping_mechanisms']},
            4: {'complete': False, 'required_fields': []},
            5: {'complete': False, 'required_fields': []},
            6: {'complete': False, 'required_fields': []}
        }
        
        # Track which questions have been answered
        self.answered_questions = set()


def initialize_session() -> ConversationState:
    """Initialize a new diagnostic session"""
    return ConversationState()


def process_message(user_message: str, session_state: ConversationState) -> str:
    """
    Process a single user message and return agent response
    
    Args:
        user_message (str): The user's message
        session_state (ConversationState): Current conversation state
        
    Returns:
        str: Agent's response to the user message
    """
    
    # Add user message to conversation history
    session_state.conversation_history.append({
        'role': 'user', 
        'content': user_message,
        'step': session_state.current_step
    })
    
    # Determine current context based on session state
    context = _build_context(session_state, user_message)
    
    # Create inputs for CrewAI
    inputs = {
        'user_message': user_message,
        'current_step': session_state.current_step,
        'conversation_context': context,
        'patient_concerns': _extract_initial_concerns(session_state),
        'diagnosed_condition': session_state.diagnosis or 'To be determined',
        'selected_treatment_option': session_state.selected_treatment or 'To be selected'
    }
    
    # Get response from CrewAI agent
    try:
        crew = AgenticRagPsychologicalDiagnosticsTreatmentPlanningSystemCrew()
        result = crew.crew().kickoff(inputs=inputs)
        
        # Extract agent response
        agent_response = str(result.raw) if hasattr(result, 'raw') else str(result)
        
        # Update session state based on response and current step
        _update_session_state(session_state, user_message, agent_response)
        
        # Add agent response to conversation history
        session_state.conversation_history.append({
            'role': 'agent',
            'content': agent_response,
            'step': session_state.current_step
        })
        
        return agent_response
        
    except Exception as e:
        error_msg = f"I apologize, but I encountered an error processing your message. Please try again. Error: {str(e)}"
        session_state.conversation_history.append({
            'role': 'agent',
            'content': error_msg,
            'step': session_state.current_step
        })
        return error_msg


def _build_context(session_state: ConversationState, user_message: str) -> str:
    """Build context string for the agent based on current session state"""
    
    context_parts = []
    
    # Add current step information
    context_parts.append(f"Current Diagnostic Step: {session_state.current_step}")
    
    # Add step descriptions
    step_descriptions = {
        1: "Symptom Assessment - Gathering detailed symptom information",
        2: "Duration and Temporal Patterns - Understanding timeline and patterns", 
        3: "Functional Impact Assessment - Exploring daily life impact",
        4: "Clinical Diagnosis - Formulating diagnosis based on gathered information",
        5: "Treatment Options - Presenting treatment options for patient selection",
        6: "Treatment Plan Generation - Creating comprehensive treatment plan"
    }
    
    if session_state.current_step <= 6:
        context_parts.append(f"Focus: {step_descriptions[session_state.current_step]}")
    
    # Add COLLECTED INFORMATION to prevent duplicate questions
    context_parts.append("\n**Information Already Collected:**")
    
    # Step 1 collected info
    if session_state.current_step >= 1:
        symptom_info = []
        if session_state.symptoms_collected['severity']:
            symptom_info.append(f"- Severity: {session_state.symptoms_collected['severity']}")
        if session_state.symptoms_collected['frequency']:
            symptom_info.append(f"- Frequency: {session_state.symptoms_collected['frequency']}")
        if session_state.symptoms_collected['triggers']:
            symptom_info.append(f"- Triggers: {', '.join(session_state.symptoms_collected['triggers'])}")
        if session_state.symptoms_collected['eating_issues']:
            symptom_info.append("- Eating difficulties: Yes (no appetite)")
        if session_state.symptoms_collected['reality_perception']:
            symptom_info.append("- Reality perception issues: Yes (disconnection episodes)")
        if session_state.functional_impact_info['coping_mechanisms']:
            symptom_info.append(f"- Coping mechanisms: {', '.join(session_state.functional_impact_info['coping_mechanisms'])}")
        
        if symptom_info:
            context_parts.append("Symptom Information:")
            context_parts.extend(symptom_info)
    
    # Step 2 collected info
    if session_state.current_step >= 2:
        duration_info = []
        if session_state.duration_info['symptom_duration']:
            duration_info.append(f"- Duration: {session_state.duration_info['symptom_duration']}")
        if session_state.duration_info['pattern']:
            duration_info.append(f"- Pattern: {session_state.duration_info['pattern']}")
        
        if duration_info:
            context_parts.append("Duration/Pattern Information:")
            context_parts.extend(duration_info)
    
    # Step 3 collected info
    if session_state.current_step >= 3:
        impact_info = []
        if session_state.functional_impact_info['work_impact']:
            impact_info.append(f"- Work impact: {session_state.functional_impact_info['work_impact']}")
        if session_state.functional_impact_info['daily_activities']:
            impact_info.append(f"- Daily activities: {session_state.functional_impact_info['daily_activities']}")
        
        if impact_info:
            context_parts.append("Functional Impact:")
            context_parts.extend(impact_info)
    
    # Add what's still needed for current step
    context_parts.append(f"\n**Step {session_state.current_step} Progress:**")
    if session_state.current_step == 1:
        needed = []
        if not session_state.symptoms_collected['severity']:
            needed.append("severity ratings")
        if not session_state.symptoms_collected['triggers']:
            needed.append("triggers")
        if not session_state.symptoms_collected['frequency']:
            needed.append("frequency/patterns")
        
        if needed:
            context_parts.append(f"Still need to gather: {', '.join(needed)}")
        else:
            context_parts.append("✓ Sufficient information collected for Step 1. Ready to move to Step 2.")
    
    elif session_state.current_step == 2:
        needed = []
        if not session_state.duration_info['symptom_duration']:
            needed.append("symptom duration/timeline")
        if not session_state.duration_info['pattern']:
            needed.append("episodic vs continuous pattern")
        
        if needed:
            context_parts.append(f"Still need to gather: {', '.join(needed)}")
        else:
            context_parts.append("✓ Sufficient information collected for Step 2. Ready to move to Step 3.")
    
    elif session_state.current_step == 3:
        needed = []
        if not session_state.functional_impact_info['work_impact'] and not session_state.functional_impact_info['daily_activities']:
            needed.append("impact on work/daily activities")
        
        if needed:
            context_parts.append(f"Still need to gather: {', '.join(needed)}")
        else:
            context_parts.append("✓ Sufficient information collected for Step 3. Ready to move to Step 4.")
    
    # Add conversation summary
    if session_state.conversation_history:
        recent_messages = session_state.conversation_history[-4:]  # Last 4 messages for context
        context_parts.append("\n**Recent Conversation:**")
        for msg in recent_messages:
            context_parts.append(f"- {msg['role'].title()}: {msg['content'][:100]}...")
    
    return "\n".join(context_parts)


def _extract_initial_concerns(session_state: ConversationState) -> str:
    """Extract initial patient concerns from conversation history"""
    if session_state.conversation_history:
        first_message = session_state.conversation_history[0]
        return first_message.get('content', 'General psychological assessment requested')
    return 'General psychological assessment requested'


def _update_session_state(session_state: ConversationState, user_message: str, agent_response: str):
    """Update session state based on user message and agent response"""
    
    user_lower = user_message.lower()
    agent_lower = agent_response.lower()
    
    # Extract information from user message based on current step
    if session_state.current_step == 1:  # Symptom Assessment
        # Extract severity info
        if any(word in user_lower for word in ['anxiety', 'depression', 'stress']):
            if 'anxiety' in user_lower and any(char.isdigit() for char in user_message):
                # Extract anxiety level (e.g., "anxiety is at a 9")
                for word in user_message.split():
                    if word.replace(',', '').replace('.', '').isdigit():
                        session_state.symptoms_collected['severity'] = f"anxiety: {word}"
                        break
        
        # Extract frequency info
        if any(word in user_lower for word in ['frequent', 'always', 'sometimes', 'rarely', 'constant', 'comes and goes']):
            session_state.symptoms_collected['frequency'] = user_message
        
        # Extract triggers
        if any(word in user_lower for word in ['trigger', 'caused by', 'because', 'stress', 'financial', 'work', 'relationship']):
            if 'financial' in user_lower:
                session_state.symptoms_collected['triggers'].append('financial stress')
        
        # Extract specific symptoms
        symptom_keywords = ['eat', 'sleep', 'appetite', 'insomnia', 'reality', 'disconnected', 'panic', 'worry']
        for keyword in symptom_keywords:
            if keyword in user_lower:
                if keyword == 'eat' or keyword == 'appetite':
                    session_state.symptoms_collected['eating_issues'] = True
                elif keyword == 'sleep' or keyword == 'insomnia':
                    session_state.symptoms_collected['sleep_issues'] = True
                elif keyword == 'reality' or keyword == 'disconnected':
                    session_state.symptoms_collected['reality_perception'] = True
        
        # Extract coping mechanisms
        if any(word in user_lower for word in ['outside', 'present with others', 'exercise', 'meditation', 'coping']):
            if 'outside' in user_lower:
                session_state.functional_impact_info['coping_mechanisms'].append('being outside')
            if 'present with others' in user_lower:
                session_state.functional_impact_info['coping_mechanisms'].append('social presence')
        
        # Check if we have enough info to move to step 2
        if _check_step_completion(session_state, 1):
            session_state.current_step = 2
            session_state.step_completion_status[1]['complete'] = True
    
    elif session_state.current_step == 2:  # Duration/Temporal Patterns
        # Extract duration info
        duration_keywords = ['days', 'weeks', 'months', 'years', 'started', 'began', 'since']
        if any(keyword in user_lower for keyword in duration_keywords):
            session_state.duration_info['symptom_duration'] = user_message
        
        # Extract pattern info
        if any(word in user_lower for word in ['episodic', 'continuous', 'comes and goes', 'constant', 'waves']):
            session_state.duration_info['pattern'] = user_message
        
        # Check if we have enough info to move to step 3
        if _check_step_completion(session_state, 2):
            session_state.current_step = 3
            session_state.step_completion_status[2]['complete'] = True
    
    elif session_state.current_step == 3:  # Functional Impact
        # Extract impact info
        if any(word in user_lower for word in ['work', 'job', 'career', 'employment']):
            session_state.functional_impact_info['work_impact'] = user_message
        
        if any(word in user_lower for word in ['relationship', 'family', 'friends', 'social']):
            session_state.functional_impact_info['relationship_impact'] = user_message
        
        if any(word in user_lower for word in ['daily', 'routine', 'activities', 'self-care']):
            session_state.functional_impact_info['daily_activities'] = user_message
        
        # Check if we have enough info to move to step 4
        if _check_step_completion(session_state, 3):
            session_state.current_step = 4
            session_state.step_completion_status[3]['complete'] = True
    
    # Also check if agent explicitly indicates moving to next step
    step_phrases = [
        ("step 1 complete", 2),
        ("moving to step 2", 2),
        ("step 2 complete", 3),
        ("moving to step 3", 3),
        ("step 3 complete", 4),
        ("moving to step 4", 4),
        ("step 4 complete", 5),
        ("moving to step 5", 5),
        ("step 5 complete", 6),
        ("moving to step 6", 6)
    ]
    
    for phrase, next_step in step_phrases:
        if phrase in agent_lower:
            if next_step > session_state.current_step:
                session_state.current_step = next_step
                if next_step > 1:
                    session_state.step_completion_status[next_step - 1]['complete'] = True
            break
    
    # Check for treatment selection in step 5
    if session_state.current_step == 5 and not session_state.selected_treatment:
        treatment_indicators = ['option 1', 'option 2', 'option 3', 'first', 'second', 'third', 'cbt', 'dbt']
        if any(indicator in user_lower for indicator in treatment_indicators):
            session_state.selected_treatment = user_message.strip()
    
    # Check if treatment plan has been generated
    if session_state.current_step == 6 and "treatment plan" in agent_lower:
        session_state.treatment_plan_generated = True
        session_state.assessment_complete = True


def get_conversation_history(session_state: ConversationState) -> List[Dict[str, Any]]:
    """Get formatted conversation history for display"""
    return session_state.conversation_history


def is_assessment_complete(session_state: ConversationState) -> bool:
    """Check if the diagnostic assessment is complete"""
    return session_state.assessment_complete


def get_current_step(session_state: ConversationState) -> int:
    """Get current diagnostic step"""
    return session_state.current_step


def _check_step_completion(session_state: ConversationState, step: int) -> bool:
    """Check if a step has collected enough information to progress"""
    
    if step == 1:  # Symptom Assessment
        # Need at least severity, some triggers, and specific symptoms
        has_severity = session_state.symptoms_collected['severity'] is not None
        has_triggers = len(session_state.symptoms_collected['triggers']) > 0
        has_symptoms = (session_state.symptoms_collected['eating_issues'] is not None or 
                       session_state.symptoms_collected['sleep_issues'] is not None or
                       session_state.symptoms_collected['reality_perception'] is not None)
        has_coping = len(session_state.functional_impact_info['coping_mechanisms']) > 0
        
        return has_severity and has_triggers and has_symptoms and has_coping
    
    elif step == 2:  # Duration/Temporal Patterns
        has_duration = session_state.duration_info['symptom_duration'] is not None
        has_pattern = session_state.duration_info['pattern'] is not None
        return has_duration and has_pattern
    
    elif step == 3:  # Functional Impact
        has_impact = (session_state.functional_impact_info['work_impact'] is not None or
                     session_state.functional_impact_info['daily_activities'] is not None)
        has_coping = len(session_state.functional_impact_info['coping_mechanisms']) > 0
        return has_impact and has_coping
    
    return False