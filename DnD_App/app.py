import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

app = Flask(__name__)

# Ein geheimer Schlüssel wird benötigt, damit Flask sicheren Login-Status speichern kann
app.secret_key = 'tiamat_is_rising_secret_key_12345'

# Absoluter Pfad für PythonAnywhere
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'dnd_campaign.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# --- DATENBANK MODELLE ---
class Pin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    y = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    background = db.Column(db.String(100))
    age = db.Column(db.String(50))
    appearance = db.Column(db.Text)
    spellbook_image = db.Column(db.String(300))
    char_password = db.Column(db.String(100))

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    reputation = db.Column(db.Integer, default=50)
    appearance = db.Column(db.Text)
    faction_alignment = db.Column(db.String(100))
    special = db.Column(db.Text)

class Faction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    leader = db.Column(db.String(100))
    goal = db.Column(db.Text)
    known_for = db.Column(db.Text)

class Dragon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    physiology = db.Column(db.Text)
    abilities = db.Column(db.Text)
    behavior = db.Column(db.Text)
    habitat = db.Column(db.Text)

class Gallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)

class Bastion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)

class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)

class Spell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level_school = db.Column(db.String(100))
    casting_time = db.Column(db.String(100))
    range = db.Column(db.String(100))
    components = db.Column(db.String(100))
    duration = db.Column(db.String(100))
    description = db.Column(db.Text)
    classes = db.Column(db.String(200))
    source = db.Column(db.String(100))

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=True) 
    character_id = db.Column(db.Integer, nullable=True) 
    status = db.Column(db.String(50), default='active') 

with app.app_context():
    db.create_all()
    
    # --- AUTOMATISCHER DATENBANK-SCHUTZ TRICK ---
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN background VARCHAR(100)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN age VARCHAR(50)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN appearance TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN spellbook_image VARCHAR(300)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN char_password VARCHAR(100)")); db.session.commit()
    except: db.session.rollback()
        
    try: db.session.execute(text("ALTER TABLE npc ADD COLUMN reputation INTEGER DEFAULT 50")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE npc ADD COLUMN appearance TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE npc ADD COLUMN faction_alignment VARCHAR(100)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE npc ADD COLUMN special TEXT")); db.session.commit()
    except: db.session.rollback()

    try: db.session.execute(text("ALTER TABLE faction ADD COLUMN leader VARCHAR(100)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE faction ADD COLUMN goal TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE faction ADD COLUMN known_for TEXT")); db.session.commit()
    except: db.session.rollback()

    try: db.session.execute(text("ALTER TABLE dragon ADD COLUMN physiology TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE dragon ADD COLUMN abilities TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE dragon ADD COLUMN behavior TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE dragon ADD COLUMN habitat TEXT")); db.session.commit()
    except: db.session.rollback()

def save_image(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/uploads/{filename}"
    return ""

# --- LOGIN & AUTH ---
def get_auth_role():
    return session.get('role', 'none')

def is_auth():
    return get_auth_role() in ['editor', 'admin']

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u = data.get('username')
    p = data.get('password')
    
    if u == '' and p == '':
        session['role'] = 'admin'
        return jsonify({"success": True, "role": "admin"})
    elif u == '' and p == '':
        session['role'] = 'editor'
        return jsonify({"success": True, "role": "editor"})
        
    return jsonify({"success": False}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('role', None)
    return jsonify({"success": True})

@app.route('/api/auth_status', methods=['GET'])
def auth_status():
    return jsonify({"role": get_auth_role()})

@app.route('/api/verify_char_pwd', methods=['POST'])
def verify_char_pwd():
    data = request.json
    char_id = data.get('char_id')
    pwd = data.get('password')
    char = Character.query.get(char_id)
    if char and char.char_password == pwd:
        return jsonify({"success": True})
    return jsonify({"success": False})

# --- DATA ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/pins', methods=['GET', 'POST'])
def handle_pins():
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        y = float(request.form.get('y'))
        x = float(request.form.get('x'))
        title = request.form.get('title')
        desc = request.form.get('description')
        order_index = int(request.form.get('order_index', 0))
        image_url = save_image(request.files.get('image'))
        new_pin = Pin(y=y, x=x, title=title, image=image_url, description=desc, order_index=order_index)
        db.session.add(new_pin)
        db.session.commit()
        return jsonify({"message": "Pin created", "id": new_pin.id}), 201
        
    pins = Pin.query.order_by(Pin.order_index).all()
    return jsonify([{"id": p.id, "y": p.y, "x": p.x, "title": p.title, "image": p.image, "description": p.description, "order_index": p.order_index} for p in pins])

@app.route('/api/pins/<int:id>', methods=['PUT', 'DELETE'])
def modify_pin(id):
    if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
    pin = Pin.query.get_or_404(id)
    if request.method == 'PUT':
        if request.is_json:
            data = request.json
            if 'y' in data and 'x' in data:
                pin.y = data['y']
                pin.x = data['x']
            if 'order_index' in data:
                pin.order_index = int(data['order_index'])
        else:
            if 'title' in request.form: pin.title = request.form['title']
            if 'description' in request.form: pin.description = request.form['description']
            new_image = save_image(request.files.get('image'))
            if new_image: pin.image = new_image
        db.session.commit()
        return jsonify({"message": "Pin updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(pin)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200

def handle_entities(model):
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        
        if model == Quest:
            is_grp = request.form.get('is_group') == 'true'
            char_id = request.form.get('character_id')
            new_entity = Quest(
                title=request.form.get('title'),
                description=request.form.get('description'),
                is_group=is_grp,
                character_id=int(char_id) if char_id and not is_grp else None,
                status=request.form.get('status', 'active')
            )
            db.session.add(new_entity)
            db.session.commit()
            return jsonify({"message": "Created", "id": new_entity.id}), 201

        kwargs = {
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        image_url = save_image(request.files.get('image'))
        if image_url: kwargs['image'] = image_url
            
        if model == Character:
            kwargs['background'] = request.form.get('background', '')
            kwargs['age'] = request.form.get('age', '')
            kwargs['appearance'] = request.form.get('appearance', '')
            kwargs['char_password'] = request.form.get('char_password', '')
            sb_img = save_image(request.files.get('spellbook_image'))
            if sb_img: kwargs['spellbook_image'] = sb_img
        elif model == NPC:
            rep = request.form.get('reputation')
            kwargs['reputation'] = int(rep) if rep and rep.isdigit() else 50
            kwargs['appearance'] = request.form.get('appearance', '')
            kwargs['faction_alignment'] = request.form.get('faction_alignment', '')
            kwargs['special'] = request.form.get('special', '')
        elif model == Faction:
            kwargs['leader'] = request.form.get('leader', '')
            kwargs['goal'] = request.form.get('goal', '')
            kwargs['known_for'] = request.form.get('known_for', '')
        elif model == Dragon:
            kwargs['physiology'] = request.form.get('physiology', '')
            kwargs['abilities'] = request.form.get('abilities', '')
            kwargs['behavior'] = request.form.get('behavior', '')
            kwargs['habitat'] = request.form.get('habitat', '')
            
        new_entity = model(**kwargs)
        db.session.add(new_entity)
        db.session.commit()
        return jsonify({"message": "Created", "id": new_entity.id}), 201
    
    entities = model.query.all()
    result = []
    for e in entities:
        if model == Quest:
            result.append({"id": e.id, "title": e.title, "description": e.description, "is_group": e.is_group, "character_id": e.character_id, "status": e.status})
            continue

        data = {"id": e.id, "name": e.name, "image": e.image, "description": e.description}
        if model == Character:
            data['background'] = getattr(e, 'background', '')
            data['age'] = getattr(e, 'age', '')
            data['appearance'] = getattr(e, 'appearance', '')
            data['spellbook_image'] = getattr(e, 'spellbook_image', '')
            data['has_password'] = bool(getattr(e, 'char_password', False))
        elif model == NPC:
            data['reputation'] = getattr(e, 'reputation', 50)
            data['appearance'] = getattr(e, 'appearance', '')
            data['faction_alignment'] = getattr(e, 'faction_alignment', '')
            data['special'] = getattr(e, 'special', '')
        elif model == Faction:
            data['leader'] = getattr(e, 'leader', '')
            data['goal'] = getattr(e, 'goal', '')
            data['known_for'] = getattr(e, 'known_for', '')
        elif model == Dragon:
            data['physiology'] = getattr(e, 'physiology', '')
            data['abilities'] = getattr(e, 'abilities', '')
            data['behavior'] = getattr(e, 'behavior', '')
            data['habitat'] = getattr(e, 'habitat', '')
        result.append(data)
    return jsonify(result)

def modify_entity(model, id):
    if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
    entity = model.query.get_or_404(id)
    if request.method == 'PUT':
        if model == Quest:
            if 'title' in request.form: entity.title = request.form['title']
            if 'description' in request.form: entity.description = request.form['description']
            if 'status' in request.form: entity.status = request.form['status']
            db.session.commit()
            return jsonify({"message": "Updated"}), 200

        if 'name' in request.form: entity.name = request.form['name']
        if 'description' in request.form: entity.description = request.form['description']
        
        if model == Character:
            if 'background' in request.form: entity.background = request.form['background']
            if 'age' in request.form: entity.age = request.form['age']
            if 'appearance' in request.form: entity.appearance = request.form['appearance']
            pwd = request.form.get('char_password')
            if pwd: entity.char_password = pwd
            
            new_sb_img = save_image(request.files.get('spellbook_image'))
            if new_sb_img: entity.spellbook_image = new_sb_img
        elif model == NPC:
            if 'reputation' in request.form: entity.reputation = int(request.form['reputation'])
            if 'appearance' in request.form: entity.appearance = request.form['appearance']
            if 'faction_alignment' in request.form: entity.faction_alignment = request.form['faction_alignment']
            if 'special' in request.form: entity.special = request.form['special']
        elif model == Faction:
            if 'leader' in request.form: entity.leader = request.form['leader']
            if 'goal' in request.form: entity.goal = request.form['goal']
            if 'known_for' in request.form: entity.known_for = request.form['known_for']
        elif model == Dragon:
            if 'physiology' in request.form: entity.physiology = request.form['physiology']
            if 'abilities' in request.form: entity.abilities = request.form['abilities']
            if 'behavior' in request.form: entity.behavior = request.form['behavior']
            if 'habitat' in request.form: entity.habitat = request.form['habitat']
        
        new_image = save_image(request.files.get('image'))
        if new_image: entity.image = new_image
            
        db.session.commit()
        return jsonify({"message": "Updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(entity)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200

@app.route('/api/chars', methods=['GET', 'POST'])
def chars(): return handle_entities(Character)
@app.route('/api/chars/<int:id>', methods=['PUT', 'DELETE'])
def modify_char(id): return modify_entity(Character, id)

@app.route('/api/npcs', methods=['GET', 'POST'])
def npcs(): return handle_entities(NPC)
@app.route('/api/npcs/<int:id>', methods=['PUT', 'DELETE'])
def modify_npc(id): return modify_entity(NPC, id)

@app.route('/api/factions', methods=['GET', 'POST'])
def factions(): return handle_entities(Faction)
@app.route('/api/factions/<int:id>', methods=['PUT', 'DELETE'])
def modify_faction(id): return modify_entity(Faction, id)

@app.route('/api/dragons', methods=['GET', 'POST'])
def dragons(): return handle_entities(Dragon)
@app.route('/api/dragons/<int:id>', methods=['PUT', 'DELETE'])
def modify_dragon(id): return modify_entity(Dragon, id)

@app.route('/api/gallery', methods=['GET', 'POST'])
def gallery(): return handle_entities(Gallery)
@app.route('/api/gallery/<int:id>', methods=['PUT', 'DELETE'])
def modify_gallery(id): return modify_entity(Gallery, id)

@app.route('/api/bastion', methods=['GET', 'POST'])
def bastion(): return handle_entities(Bastion)
@app.route('/api/bastion/<int:id>', methods=['PUT', 'DELETE'])
def modify_bastion(id): return modify_entity(Bastion, id)

@app.route('/api/protocols', methods=['GET', 'POST'])
def protocols(): return handle_entities(Protocol)
@app.route('/api/protocols/<int:id>', methods=['PUT', 'DELETE'])
def modify_protocol(id): return modify_entity(Protocol, id)

@app.route('/api/quests', methods=['GET', 'POST'])
def quests(): return handle_entities(Quest)
@app.route('/api/quests/<int:id>', methods=['PUT', 'DELETE'])
def modify_quest(id): return modify_entity(Quest, id)

@app.route('/api/spells', methods=['GET', 'POST'])
def spells():
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        new_spell = Spell(
            character_id=int(request.form.get('character_id')),
            name=request.form.get('name'),
            level_school=request.form.get('level_school', ''),
            casting_time=request.form.get('casting_time', ''),
            range=request.form.get('range', ''),
            components=request.form.get('components', ''),
            duration=request.form.get('duration', ''),
            description=request.form.get('description', ''),
            classes=request.form.get('classes', ''),
            source=request.form.get('source', '')
        )
        db.session.add(new_spell)
        db.session.commit()
        return jsonify({"message": "Spell created"}), 201

    char_id = request.args.get('character_id')
    if char_id:
        spells_query = Spell.query.filter_by(character_id=int(char_id)).all()
    else:
        spells_query = Spell.query.all()
        
    return jsonify([{
        "id": s.id, "character_id": s.character_id, "name": s.name,
        "level_school": s.level_school, "casting_time": s.casting_time,
        "range": s.range, "components": s.components, "duration": s.duration,
        "description": s.description, "classes": s.classes, "source": s.source
    } for s in spells_query])

@app.route('/api/spells/<int:id>', methods=['PUT', 'DELETE'])
def modify_spell(id):
    if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
    spell = Spell.query.get_or_404(id)
    if request.method == 'PUT':
        if 'name' in request.form: spell.name = request.form['name']
        if 'level_school' in request.form: spell.level_school = request.form['level_school']
        if 'casting_time' in request.form: spell.casting_time = request.form['casting_time']
        if 'range' in request.form: spell.range = request.form['range']
        if 'components' in request.form: spell.components = request.form['components']
        if 'duration' in request.form: spell.duration = request.form['duration']
        if 'description' in request.form: spell.description = request.form['description']
        if 'classes' in request.form: spell.classes = request.form['classes']
        if 'source' in request.form: spell.source = request.form['source']
        db.session.commit()
        return jsonify({"message": "Spell updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(spell)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)
