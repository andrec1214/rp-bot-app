from app import app, db
from models import User, Character, Session, Message
from utils import prompt_claude, build_context_for_prompt, build_system_prompt

def get_session(user):
    print("Please select a character from the above.")
    charname = input("Character: ").strip()
    char = Character.query.filter_by(name=charname, user_id=user.id).first()

    while True:
        if not char:
            print("Your entry does not match any of the previously listed, please try again.")
            
        else:
            print(f"Selected Character: {char.name}")
            break
    
    sessions = char.sessions

    print(f"You have the following sessions with {char.name}")
    for sesh in sessions:
        print(sesh.title, sesh.created_at)


def create_character():
    print("Enter the details for your new character!")
    while True:
        try:
            # get the info
            name = input("Name (Required): ").strip()
            personality = input("Personality (Required): ").strip()
            backstory = input("Backstory: ").strip()
            world_info = input("World Info: ").strip()
            goals = input("Goals: ").strip()
            relationships = input("Relationships: ").strip() 
            char = Character(name=name, 
                            personality=personality, 
                            backstory=backstory, 
                            world_info=world_info,
                            goals=goals,
                            relationships=relationships)
            db.session.add(char)
            db.session.commit()
            return char

        except IntegrityError as e:
            db.session.rollback()



with app.app_context():
    
    print("Is this your first time using this service? (y/n)")
    first_time = False

    # user verification
    while True:
        ans = input().lower().strip()
        if ans == "y" or ans == "n":
            if ans == "y":
                first_time = True
            break
        else:
            print("Your input was not recognized by the system. Please try again.")

    name = input("Enter your username.").strip()
    user = User.query.filter_by(username=name).first()

    # add the user to the db or verify their name
    if not user:
        if first_time:
            user = User(username=name)
            db.session.add(user)
            db.session.commit()

        else:
            while True:
                name = input("Your username was not recognized. Please try again!").strip()
                user = User.query.filter_by(username=name).first()
                if user:
                    print("Thank you!")
                    break

    print(f"Welcome to the RP Bot application, {user.username}! Thank you for testing!")
    print("\n")

    if not first_time:
        chars = [char.name for char in user.characters]
        print("Here is a list of characters you have previously interacted with: ")
        print(" ".join(chars))
        print("\nWould you like to open a session, or input a new character? (Enter 0 for session, 1 for new character)")
        ans = int(input())

        if ans == 0:
            get_session(user)

        elif ans == 1:
            char = create_character()