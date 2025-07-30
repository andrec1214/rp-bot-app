from db import db
from datetime import datetime, timezone
from werkzeug.security import check_password_hash, generate_password_hash

# USERS have CHARACTERS which have SESSIONS which have MESSAGES

# User table
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    password_hash = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), unique=True, nullable=False) # username lol
    date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    characters = db.relationship("Character", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Character table
class Character(db.Model):
    __tablename__ = "characters" # not much to document here, names are pretty self-explanatory.

    ''' this is meant to just be a barebones table for characters. if you just want to give a personality and chat, you can.
    otherwise, you can flesh the story and world out.
    '''

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(64), nullable=False)
    personality = db.Column(db.Text, nullable=False)
    backstory = db.Column(db.Text)
    world_info = db.Column(db.Text)
    goals = db.Column(db.Text)
    relationships = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    sessions = db.relationship("Session", backref="character", lazy=True)


# Session table
class Session(db.Model): 
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    title = db.Column(db.String(256), default=f"Unnamed Session @ {created_at}.") # changed to be required to make life easier

    messages = db.relationship("Message", backref="session", lazy=True)

# Message table
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False) # message content
    sender = db.Column(db.String(128), nullable=False) # can have user or character, helps for summaries
    char_name = db.Column(db.String(128), nullable=False) # char names
    is_summary = db.Column(db.Boolean, default=False) # message IS a summary, distinction between below
    summarized = db.Column(db.Boolean, default=False) # message was summarized
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)