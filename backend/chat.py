from app import app, db
from init import setup
from utils import prompt_claude, build_context_for_prompt, build_system_prompt
from models import User, Character, Session, Message

setup()