from app import app, db
from init import setup
from utils import prompt_claude, build_context_for_prompt, build_system_prompt
from models import Message
from sqlalchemy.exc import IntegrityError

user, character, session = setup()

try:
    with app.app_context():
        
        # refresh the stuff
        db.session.add(user)
        db.session.add(character)
        db.session.add(session)

        # this is purely for the user's sake
        print("\nCHARACTER INFO:")
        print(f"You are chatting with {character.name}!")
        print(f"Personality: {character.personality}")
        character.backstory and print(f"Backstory: {character.backstory}")
        character.world_info and print(f"World Info: {character.world_info}")
        character.goals and print(f"Goals: {character.goals}")
        character.relationships and print(f"Relationships: {character.relationships}")
        user_prompt = input("\nWould you like to enter a custom prompt for Claude? This can determine prose, perspective, and other details. If not, simply press Enter.").strip()
        print("\nWhen you want to end the chat, just reply with \"exit\"!\n")
        print("-" * 50)

        while True:
            user_msg = input("\nYou: ").strip()

            if user_msg == "exit":
                print("\nHave a nice day!")
                exit()

            user_message = Message(content=user_msg,
                                sender=user.username,
                                session_id=session.id,
                                char_name=character.name)
            db.session.add(user_message)
            db.session.commit()

            sys_prompt = build_system_prompt(user.id, session.id, user_prompt)
            context = build_context_for_prompt(session.id, user_msg)
            char_msg = prompt_claude(context, sys_prompt)

            char_message = Message(content=char_msg,
                               sender=character.name,
                               session_id=session.id,
                               char_name=character.name)
            db.session.add(char_message)
            db.session.commit()

            print(f"\n{character.name}: {char_msg}")

except KeyboardInterrupt:
    print("\nHave a nice day!")
    exit()

except IntegrityError:
    print("\nThere was an error with the database. Please run the program again.")
    exit()

except Exception as e:
    print("\nThere was an error in chat.py. Please run the program again.")
    print(f"\n{e}")
    exit()