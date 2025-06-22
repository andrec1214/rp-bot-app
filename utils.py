from anthropic import Anthropic
from db import db
from models import User, Character
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
