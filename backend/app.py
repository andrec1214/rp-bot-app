from flask import Flask, session, request, jsonify
from models import db, User, Character, Session, Message
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DB_URL", "sqlite:///db.sqlite3")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.secret_key = os.getenv("SECRET_KEY")

db.init_app(app)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

'''
APP ROUTES
I have no idea what this is going to look like as of rn
I don't have any rate limiting on the password attempts bc I don't even know what the front end looks like and
if there are any bugs then it is what it is i'll figure it out as I go.
Thank god I decided to wait until I was a rising junior to try making a full stack project :)
'''

# AUTH routes
@app.route('/api/auth/register', methods=['GET', 'POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # no duplicate usernames
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "This username is taken."}), 400
    
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'Your registration was successful!', 'user_id': user.id})

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        session['user_id'] = user.id
        return jsonify({'message': 'Login successful.', 'user_id': user.id})
    
    return jsonify({'error': 'Your username or password were incorrect.'}), 401

@app.route('/api/auth/logout')
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully.'})

# CHARACTER routes
@app.route('/api/characters', methods=['POST', 'GET'])
def characters():
    user_id = session.get('user_id')

    if not user_id:
        return jsonify({'error': 'User not authenticated.'}), 401
    
    characters = Character.query.filter_by(user_id=user_id).all()

    if request.method == 'GET':
        if not characters:
            return jsonify({'message': 'You do not have any characters.'})
        
        return jsonify([{
            'name': char.name,
            'personality': char.personality,
            'backstory': char.backstory,
            'world_info': char.world_info,
            'goals': char.goals,
            'relationships': char.relationships
        } 
        for char in characters])
    
    elif request.method == 'POST':
        char_info = request.get_json()

        # create char and commit to db then return json
        char = Character(
            name=char_info.get('name'),
            personality=char_info.get('personality'),
            backstory=char_info.get('backstory'),
            world_info=char_info.get('world_info'),
            goals=char_info.get('goals'),
            relationships=char_info.get('relationships'),
            user_id=session.get('user_id')
        )

        db.session.add(char)
        db.session.commit()

        return jsonify({'message': f'{char_info.get('name')} was successfully created!', 'char_id': char.id})
    
@app.route('/api/characters/<int:character_id>', methods=['GET', 'POST', 'DELETE'])
def char_actions(character_id):
    # GET will display char info to the screen, POST will make changes to the char,
    # DELETE will delete (shocker).
    user_id = session.get("user_id")
    user = User.query.filter_by(id=user_id).first()

    if not user:
        return jsonify({'error': 'User not authenticated.'}), 401
    
    char = Character.query.filter_by(id=character_id, user_id=user_id).first()
    if request.method == 'GET':
        return jsonify({
            'name': char.name,
            'personality': char.personality,
            'backstory': char.backstory,
            'world_info': char.world_info,
            'goals': char.goals,
            'relationships': char.relationships,
            'user_id': user.id
        })
    
    elif request.method == 'DELETE':

        db.session.delete(char)
        db.session.commit()

        return jsonify({'message': f'{char.name} was successfully deleted.'})
    
    elif request.method == 'POST':
        data = request.get_json()
        char.name = data.get('name')
        char.personality = data.get('personality')
        char.backstory = data.get('backstory')
        char.world_info = data.get('world_info')
        char.goals = data.get('goals')
        char.relationships = data.get('relationships')

        db.session.commit()

        return jsonify({'message': f'{char.name} was successfully modified.'})
    
@app.route('/api/characters/<int:character_id>/sessions', methods=['POST', 'GET'])
def sessions(character_id):
    