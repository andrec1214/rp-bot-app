from app import app, db
from models import User, Character, Session
from sqlalchemy.exc import IntegrityError
from utils import init_claude

# GET CHARACTER FUNCTION
def get_character(user):
    print("\nPlease select a character from above.\n")

    while True:
        charname = input("Choose a character: ")
        character = Character.query.filter_by(name=charname, user_id=user.id).first()
        if not character:
            print("Your input did not match any of the listed options. Try again. Enter here: ")
            charname = input().strip()
        else:
            print(f"\nSelected Character: {character.name}")
            return character

# GET SESSION FUNCTION   
def get_session(char):
    print(f"\nYou have the following sessions with {char.name}:")
    for sesh in char.sessions:
        print(sesh.title, sesh.created_at)

    print("\nPlease select a session.")
    title = input().strip()
    session = Session.query.filter_by(title=title, character_id=char.id).first()
    while not session:
        title = input("Your session input was not registered properly, please try again.").strip()
        session = Session.query.filter_by(title=title, character_id=char.id).first()

    return session

# CREATE CHARACTER FUNCTION
def create_character(user):
    print("\nEnter the details for your new character!")

    # name validation
    name = input("Name (Required): ").strip()
    while not name:
        name = input("\nYour character's name is a required field. Please try again. Enter here: ").strip()

    # personality validation
    personality = input("Personality (Required): ").strip()
    while not personality:
        personality = input("\nYour character personality is a required field. Please try again. Enter here: ").strip()
    
    backstory = input("Backstory (Optional): ").strip()
    world_info = input("World Info (Optional): ").strip()
    goals = input("Goals (Optional): ").strip()
    relationships = input("Relationships (Optional): ").strip()
    
    try:
        character = Character(name=name, 
                            personality=personality,
                            backstory=backstory if backstory else None,
                            world_info=world_info if world_info else None,
                            goals=goals if goals else None,
                            relationships=relationships if relationships else None,
                            user_id=user.id)
            
        db.session.add(character)
        db.session.commit()
        return character
        
    except IntegrityError as e:
        db.session.rollback()
        print("Database error. Sorry for the inconvenience. Please run the program again.")
        exit()

# SETUP SEGMENT
def setup():
    try:
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
                    print("\nYour input was not recognized by the system. Please try again.")

            name = input("\nEnter your username. Your username must be between 5 and 15 characters.\n").strip()

            while not name or len(name) < 5 or len(name) > 15:
                if not name:
                    name = input("Your username cannot be blank. Please enter a username: ").strip()

                elif len(name) < 5 or len(name) > 15:
                    name = input("Your username must be between 5 and 15 characters. Please pick a new username: ").strip()

            user = User.query.filter_by(username=name).first()

            # add the user to the db or verify their name
            if not user:
                if first_time:
                    user = User(username=name)
                    db.session.add(user)
                    db.session.commit()

                else:
                    attempts = 0
                    while True:

                        if attempts == 3:
                            print("There was an error processing your information. Have a nice day!")
                            exit()

                        name = input("Your username was not recognized. Please try again!\n").strip()
                        user = User.query.filter_by(username=name).first()
                        if user:
                            print("Thank you!")
                            break
                        
                        else:
                            attempts += 1

            print(f"\nWelcome to the RP Bot application, {user.username}! Thank you for testing!\n")
            print("This RP Bot works through the Anthropic Claude API. Please enter your API key to continue.")
            print("NOTE: YOUR API KEY IS NOT SAVED TO THE DATABASE.")

            key = input("Enter your API key here: ").strip()
            init_claude(key)

            # prior user handling
            if not first_time:
                chars = [char.name for char in user.characters]
                print("\nWould you like to open a session, or create a new character? (Enter 0 for session, 1 for new character): ")

                while True:
                    try:
                        ans = int(input().strip())
                    except:
                        print("Invalid input, please try again.")
                        continue

                    if ans == 0:
                        print("\nHere is a list of characters you have previously interacted with: ")
                        print(" ".join(chars))
                        char = get_character(user)
                        sesh = get_session(char)
                        return user, char, sesh

                    elif ans == 1:
                        char = create_character(user)
                        title = input(f"\nYou may enter a title for your session with {char.name}. This is purely optional. Enter here: ").strip()
                        sesh = Session(character_id=char.id, title=title if title else None)
                        db.session.add(sesh)
                        db.session.commit()
                        return user, char, sesh
                    
                    else:
                        print("Invalid input. Try again.")

            # first time user handling
            else:
                print("\nLet's create your first character!")
                char = create_character(user)
                title = input(f"\nYou may enter a title for your session with {char.name}. This is purely optional. Enter here: ").strip()
                sesh = Session(character_id=char.id, title=title if title else None)
                db.session.add(sesh)
                db.session.commit()
                return user, char, sesh
            
    except KeyboardInterrupt as e:
        print("\nHave a nice day!")
        exit()
    
    except Exception:
        print("Hi! I'm an error message! I'm here to piss you off and provide nothing of value to your debugging! (init.py)")
        exit()