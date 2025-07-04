from db import db
import datetime

# USERS have CHARACTERS which have SESSIONS which have MESSAGES

# User table
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False) # username lol
    date = db.Column(db.DateTime, default=datetime.utcnow)

    characters = db.relationship("Character", backref="user", lazy=True)

# Character table
class Character(db.Model):
    __tablename__ = "characters" # not much to document here, names are pretty self-explanatory.

    ''' this is meant to just be a barebones table for characters. if you just want to give a personality and chat, you can.
    otherwise, you can flesh the story and world out.
    '''

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    personality = db.Column(db.Text, nullable=False)
    backstory = db.Column(db.Text)
    world_info = db.Column(db.Text)
    goals = db.Column(db.Text)
    relationships = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    sessions = db.relationship("Session", backref="character", lazy=True)


# Session table
class Session(db.Model): 
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256)) # optional title for a session, can implement into a session-specific save system later
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    character_id = db.Column(db.Integer, db.ForeignKey("characters.id"), nullable=False)
    messages = db.relationship("Message", backref="session", lazy=True)

# Message table
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False) # message content
    sender = db.Column(db.String(128), nullable=False) # can have user or character, helps for summaries
    is_summary = db.Column(db.Boolean, default=False) # message IS a summary, distinction between below
    summarized = db.Column(db.Boolean, default=False) # message was summarized
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)