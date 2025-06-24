from anthropic import Anthropic
from db import db
from models import User, Character, Session, Message
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("ANTHROPIC_API_KEY") # lol not my wallet
claude = Anthropic(key)

# This is just the abstraction layer. The system prompt will be built by the build_system_prompt function below, and messages
# will be constructed dynamically using lists so I can create a conext window at the same time.
def prompt_claude(messages, system_prompt):
    try:
        response = claude.messages.create(
            model = "claude-sonnet-4-20250514",
            max_tokens = 1000,
            messages = messages,
            system = system_prompt
        )
    except Exception as err:
        return "There was an error generating a response. Please try again." # api-side error handling

    return response.content[0].text.strip()

# System prompt builder. Creates a user and character instance and builds a system prompt out of character info.
def build_system_prompt(user_id, character_id):
    user = db.session.get(User, user_id)
    character = db.session.get(Character, character_id)

    if not user:
        print("User not found.")
        return None
    elif not character:
        print("Character not found.")
        return None

    return f"""Name: {character.name}
Personality: {character.personality}
Backstory: {character.backstory}
World Info: {character.world_info}
Goals: {character.goals}
Relationships: {character.relationships}

CRUCIAL:
Do not break character no matter what.
Do not ever reference being an AI.
Do not speak or do actions for the user.
"""

def get_recent_messages(session_id, limit=30):

    # Get the most recent messages from a session, up to limit
    messages = Message.query.filter_by(session_id=session_id)\
        .filter(Message.is_summary == False)\
        .order_by(Message.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return list(reversed(messages))

def get_session_summaries(session_id):

    # Get all summary messages for a session
    summaries = Message.query.filter_by(session_id=session_id, is_summary=True)\
        .order_by(Message.timestamp.asc())\
        .all()
    return summaries

def create_summary(session_id, messages_to_summarize):

    # Create a summary of older messages and mark them as summarized
    if not messages_to_summarize:
        return None
    
    # Build context for summary
    context = []
    for msg in messages_to_summarize:
        context.append(f"{msg.sender}: {msg.content}")
    
    summary_prompt = [{"role": "user", "content": f"""Please create a concise summary (450-500 words) of this conversation segment. Focus on key plot points, character development, and character relationships:

{chr(10).join(context)}"""}]
    
    system_prompt = "You are a helpful assistant that creates detailed but concise summaries of roleplay conversations." # A separate system prompt for summarizing. Prevents conflicts from character persona.
    summary_text = prompt_claude(summary_prompt, system_prompt)
    
    # Create summary message
    summary_msg = Message(
        content=summary_text,
        sender="system",
        is_summary=True,
        session_id=session_id
    )
    db.session.add(summary_msg)
    
    # Mark original messages as summarized
    for msg in messages_to_summarize:
        msg.summarized = True
    
    db.session.commit()
    return summary_msg

def merge_summaries(summaries):
    # Merge multiple summaries into one comprehensive summary 
    if not summaries:
        return ""
    if len(summaries) == 1:
        return summaries[0].content
    
    summary_texts = [s.content for s in summaries]
    merge_prompt = [{"role": "user", "content": f"""Please merge these conversation summaries into one comprehensive summary (450-500 words). Maintain chronological order and key details:

{chr(10).join([f"Summary {i+1}: {text}" for i, text in enumerate(summary_texts)])}"""}]
    
    system_prompt = "You are a helpful assistant that merges multiple conversation summaries into one comprehensive summary."
    return prompt_claude(merge_prompt, system_prompt)

def build_context_for_prompt(session_id, new_user_message):
    """TODO: Increase message limit for summaries more dynamic. If the conversation gets too long this can potentially become expensive."""
    # Build the complete context: merged summaries + recent messages + new prompt
    # Get recent unsummarized messages
    recent_messages = get_recent_messages(session_id, 30)
    
    # Check if we need to create a summary
    unsummarized_count = Message.query.filter_by(
        session_id=session_id, 
        is_summary=False, 
        summarized=False
    ).count()
    
    if len(recent_messages) >= 30 and unsummarized_count > 60:
        old_messages = Message.query.filter_by(
            session_id=session_id, 
            is_summary=False, 
            summarized=False
        ).order_by(Message.timestamp.asc()).limit(30).all()
        
        create_summary(session_id, old_messages)
        # Refresh recent messages
        recent_messages = get_recent_messages(session_id, 30)
    
    # Get all summaries and merge them
    summaries = get_session_summaries(session_id)
    merged_summary = merge_summaries(summaries)
    
    # Build message list for Claude
    messages = []
    
    # Add merged summary as context if it exists
    if merged_summary:
        messages.append({
            "role": "user", 
            "content": f"[CONVERSATION SUMMARY]: {merged_summary}"
        })
    
    # Add recent messages
    for msg in recent_messages:
        role = "user" if msg.sender != "character" else "assistant"
        messages.append({"role": role, "content": msg.content})
    
    # Add new user message
    messages.append({"role": "user", "content": new_user_message})
    
    return messages