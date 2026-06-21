import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

app = Flask(__name__)
app.secret_key = 'tiamat_is_rising_secret_key_12345'
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'dnd_campaign.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db = SQLAlchemy(app)

class Pin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    y, x = db.Column(db.Float, nullable=False), db.Column(db.Float, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    background, age = db.Column(db.String(100)), db.Column(db.String(50))
    appearance, spellbook_image = db.Column(db.Text), db.Column(db.String(300))
    char_password = db.Column(db.String(100))
    race = db.Column(db.String(50))
    size = db.Column(db.String(20))
    char_class = db.Column(db.String(50))

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    reputation = db.Column(db.Integer, default=50)
    appearance, faction_alignment = db.Column(db.Text), db.Column(db.String(100))
    special = db.Column(db.Text)

class Faction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    leader, goal, known_for = db.Column(db.String(100)), db.Column(db.Text), db.Column(db.Text)

class Dragon(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    physiology, abilities = db.Column(db.Text), db.Column(db.Text)
    behavior, habitat = db.Column(db.Text), db.Column(db.Text)

class DiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)

class Bastion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)

class Protocol(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)

class Spell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level_school, casting_time = db.Column(db.String(100)), db.Column(db.String(100))
    range, components = db.Column(db.String(100)), db.Column(db.String(100))
    duration, description = db.Column(db.String(100)), db.Column(db.Text)
    classes, source = db.Column(db.String(200)), db.Column(db.String(100))

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title, description = db.Column(db.String(150), nullable=False), db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=True) 
    character_id = db.Column(db.Integer, nullable=True) 
    status = db.Column(db.String(50), default='active') 

class BastionToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bastion_id = db.Column(db.Integer, nullable=False)
    y, x = db.Column(db.Float, nullable=False), db.Column(db.Float, nullable=False)
    label, icon_type = db.Column(db.String(100), nullable=False), db.Column(db.String(50), nullable=False)

class Treasury(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    platinum, gold = db.Column(db.Integer, default=0), db.Column(db.Integer, default=0)
    silver, copper = db.Column(db.Integer, default=0), db.Column(db.Integer, default=0)

class Loot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description, image = db.Column(db.Text), db.Column(db.String(300))
    holder_id = db.Column(db.Integer, nullable=True)

class CampaignState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day, month = db.Column(db.Integer, default=1), db.Column(db.String(50), default='Flamerule')
    year, weather = db.Column(db.Integer, default=1489), db.Column(db.String(50), default='sunny')

class BestiaryBook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)

class BestiaryEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    image, description = db.Column(db.String(300)), db.Column(db.Text)
    physiology, abilities = db.Column(db.Text), db.Column(db.Text)
    behavior, habitat = db.Column(db.Text), db.Column(db.Text)
    image_x, image_y = db.Column(db.Integer, default=0), db.Column(db.Integer, default=0)

with app.app_context():
    db.create_all()
    if not Treasury.query.first(): db.session.add(Treasury(platinum=0, gold=0, silver=0, copper=0)); db.session.commit()
    if not CampaignState.query.first(): db.session.add(CampaignState(day=1, month='Flamerule', year=1489, weather='sunny')); db.session.commit()
    if not BestiaryBook.query.first():
        db.session.add(BestiaryBook(name="Dragons", image="/static/acc.jpg"))
        db.session.add(BestiaryBook(name="Monsters", image="/static/council.jpg"))
        db.session.add(BestiaryBook(name="Gods", image="/static/bg.jpg"))
        db.session.commit()

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
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN race VARCHAR(50)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN size VARCHAR(20)")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE character ADD COLUMN char_class VARCHAR(50)")); db.session.commit()
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
    try: db.session.execute(text("ALTER TABLE bestiary_entry ADD COLUMN physiology TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE bestiary_entry ADD COLUMN abilities TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE bestiary_entry ADD COLUMN behavior TEXT")); db.session.commit()
    except: db.session.rollback()
    try: db.session.execute(text("ALTER TABLE bestiary_entry ADD COLUMN habitat TEXT")); db.session.commit()
    except: db.session.rollback()

def save_image(file):
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/uploads/{filename}"
    return ""

def get_auth_role(): return session.get('role', 'none')
def is_auth(): return get_auth_role() in ['editor', 'admin']

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    u, p = data.get('username'), data.get('password')
    if u == 'admin' and p == 'jonas':
        session['role'] = 'admin'
        return jsonify({"success": True, "role": "admin"})
    elif u == 'Tyranny' and p == 'Tyranny':
        session['role'] = 'editor'
        return jsonify({"success": True, "role": "editor"})
    return jsonify({"success": False}), 401

@app.route('/api/logout', methods=['POST'])
def logout(): session.pop('role', None); return jsonify({"success": True})

@app.route('/api/auth_status', methods=['GET'])
def auth_status(): return jsonify({"role": get_auth_role()})

@app.route('/api/verify_char_pwd', methods=['POST'])
def verify_char_pwd():
    data = request.json
    char = Character.query.get(data.get('char_id'))
    if char and char.char_password == data.get('password'): return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/pins', methods=['GET', 'POST'])
def handle_pins():
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        new_pin = Pin(y=float(request.form.get('y')), x=float(request.form.get('x')), title=request.form.get('title'), image=save_image(request.files.get('image')), description=request.form.get('description'), order_index=int(request.form.get('order_index', 0)))
        db.session.add(new_pin); db.session.commit()
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
            if 'y' in data and 'x' in data: pin.y, pin.x = data['y'], data['x']
            if 'order_index' in data: pin.order_index = int(data['order_index'])
        else:
            if 'title' in request.form: pin.title = request.form['title']
            if 'description' in request.form: pin.description = request.form['description']
            new_image = save_image(request.files.get('image'))
            if new_image: pin.image = new_image
        db.session.commit()
        return jsonify({"message": "Pin updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(pin); db.session.commit()
        return jsonify({"message": "Deleted"}), 200

@app.route('/api/bastion/<int:b_id>/tokens', methods=['GET', 'POST'])
def handle_bastion_tokens(b_id):
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        new_t = BastionToken(bastion_id=b_id, y=float(request.form.get('y')), x=float(request.form.get('x')), label=request.form.get('label', 'Token'), icon_type=request.form.get('icon_type', 'enemy'))
        db.session.add(new_t); db.session.commit()
        return jsonify({"success": True, "id": new_t.id}), 201
    tokens = BastionToken.query.filter_by(bastion_id=b_id).all()
    return jsonify([{"id": t.id, "y": t.y, "x": t.x, "label": t.label, "icon_type": t.icon_type} for t in tokens])

@app.route('/api/bastion/tokens/<int:t_id>', methods=['PUT', 'DELETE'])
def modify_bastion_token(t_id):
    if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
    t = BastionToken.query.get_or_404(t_id)
    if request.method == 'PUT':
        data = request.json
        if data:
            if 'y' in data: t.y = float(data['y'])
            if 'x' in data: t.x = float(data['x'])
        db.session.commit()
        return jsonify({"success": True}), 200
    elif request.method == 'DELETE':
        db.session.delete(t); db.session.commit(); return jsonify({"success": True}), 200

def handle_entities(model):
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        if model == Quest:
            is_grp = request.form.get('is_group') == 'true'
            char_id = request.form.get('character_id')
            new_entity = Quest(title=request.form.get('title'), description=request.form.get('description'), is_group=is_grp, character_id=int(char_id) if char_id and not is_grp else None, status=request.form.get('status', 'active'))
            db.session.add(new_entity); db.session.commit()
            return jsonify({"message": "Created", "id": new_entity.id}), 201

        kwargs = {'name': request.form.get('name'), 'description': request.form.get('description')}
        image_url = save_image(request.files.get('image'))
        if image_url: kwargs['image'] = image_url
            
        if model == Character:
            kwargs['background'], kwargs['age'] = request.form.get('background', ''), request.form.get('age', '')
            kwargs['appearance'], kwargs['char_password'] = request.form.get('appearance', ''), request.form.get('char_password', '')
            kwargs['race'] = request.form.get('race', '')
            kwargs['size'] = request.form.get('size', '')
            kwargs['char_class'] = request.form.get('char_class', '')
            sb_img = save_image(request.files.get('spellbook_image'))
            if sb_img: kwargs['spellbook_image'] = sb_img
        elif model == NPC:
            rep = request.form.get('reputation')
            kwargs['reputation'] = int(rep) if rep and rep.isdigit() else 50
            kwargs['appearance'], kwargs['faction_alignment'] = request.form.get('appearance', ''), request.form.get('faction_alignment', '')
            kwargs['special'] = request.form.get('special', '')
        elif model == Faction:
            kwargs['leader'], kwargs['goal'], kwargs['known_for'] = request.form.get('leader', ''), request.form.get('goal', ''), request.form.get('known_for', '')
        elif model == Dragon:
            kwargs['physiology'], kwargs['abilities'] = request.form.get('physiology', ''), request.form.get('abilities', '')
            kwargs['behavior'], kwargs['habitat'] = request.form.get('behavior', ''), request.form.get('habitat', '')
        elif model == Loot:
            h_id = request.form.get('holder_id')
            kwargs['holder_id'] = int(h_id) if h_id else None
        elif model == DiaryEntry:
            kwargs['character_id'] = int(request.form.get('character_id'))
        elif model == BestiaryEntry:
            kwargs['book_id'] = int(request.form.get('book_id'))
            kwargs['physiology'], kwargs['abilities'] = request.form.get('physiology', ''), request.form.get('abilities', '')
            kwargs['behavior'], kwargs['habitat'] = request.form.get('behavior', ''), request.form.get('habitat', '')
            
        new_entity = model(**kwargs)
        db.session.add(new_entity); db.session.commit()
        return jsonify({"message": "Created", "id": new_entity.id}), 201
    
    entities = model.query.all()
    result = []
    for e in entities:
        if model == Quest:
            result.append({"id": e.id, "title": e.title, "description": e.description, "is_group": e.is_group, "character_id": e.character_id, "status": e.status})
            continue

        data = {"id": e.id, "name": e.name, "image": e.image, "description": e.description}
        if model == Character:
            data['background'], data['age'] = getattr(e, 'background', ''), getattr(e, 'age', '')
            data['appearance'], data['spellbook_image'] = getattr(e, 'appearance', ''), getattr(e, 'spellbook_image', '')
            data['has_password'] = bool(getattr(e, 'char_password', False))
            data['race'] = getattr(e, 'race', '')
            data['size'] = getattr(e, 'size', '')
            data['char_class'] = getattr(e, 'char_class', '')
        elif model == NPC:
            data['reputation'], data['appearance'] = getattr(e, 'reputation', 50), getattr(e, 'appearance', '')
            data['faction_alignment'], data['special'] = getattr(e, 'faction_alignment', ''), getattr(e, 'special', '')
        elif model == Faction:
            data['leader'], data['goal'], data['known_for'] = getattr(e, 'leader', ''), getattr(e, 'goal', ''), getattr(e, 'known_for', '')
        elif model == Dragon:
            data['physiology'], data['abilities'] = getattr(e, 'physiology', ''), getattr(e, 'abilities', '')
            data['behavior'], data['habitat'] = getattr(e, 'behavior', ''), getattr(e, 'habitat', '')
        elif model == Loot:
            data['holder_id'] = getattr(e, 'holder_id', None)
        elif model == DiaryEntry:
            data['character_id'] = getattr(e, 'character_id', None)
        elif model == BestiaryEntry:
            data['book_id'] = getattr(e, 'book_id', None)
            data['physiology'], data['abilities'] = getattr(e, 'physiology', ''), getattr(e, 'abilities', '')
            data['behavior'], data['habitat'] = getattr(e, 'behavior', ''), getattr(e, 'habitat', '')
            data['image_x'], data['image_y'] = getattr(e, 'image_x', 0), getattr(e, 'image_y', 0)
            
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
            if 'race' in request.form: entity.race = request.form['race']
            if 'size' in request.form: entity.size = request.form['size']
            if 'char_class' in request.form: entity.char_class = request.form['char_class']
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
        elif model == Loot:
            h_id = request.form.get('holder_id')
            entity.holder_id = int(h_id) if h_id else None
        elif model == BestiaryEntry:
            if 'physiology' in request.form: entity.physiology = request.form['physiology']
            if 'abilities' in request.form: entity.abilities = request.form['abilities']
            if 'behavior' in request.form: entity.behavior = request.form['behavior']
            if 'habitat' in request.form: entity.habitat = request.form['habitat']
            if 'image_x' in request.form: entity.image_x = int(request.form['image_x'])
            if 'image_y' in request.form: entity.image_y = int(request.form['image_y'])
        
        new_image = save_image(request.files.get('image'))
        if new_image: entity.image = new_image
            
        db.session.commit()
        return jsonify({"message": "Updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(entity); db.session.commit()
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

@app.route('/api/bestiary_books', methods=['GET', 'POST'])
def bestiary_books(): return handle_entities(BestiaryBook)
@app.route('/api/bestiary_books/<int:id>', methods=['PUT', 'DELETE'])
def modify_bestiary_book(id): return modify_entity(BestiaryBook, id)

@app.route('/api/bestiary_entries', methods=['GET', 'POST'])
def bestiary_entries(): return handle_entities(BestiaryEntry)
@app.route('/api/bestiary_entries/<int:id>', methods=['PUT', 'DELETE'])
def modify_bestiary_entry(id): return modify_entity(BestiaryEntry, id)

@app.route('/api/diary', methods=['GET', 'POST'])
def diary(): return handle_entities(DiaryEntry)
@app.route('/api/diary/<int:id>', methods=['PUT', 'DELETE'])
def modify_diary(id): return modify_entity(DiaryEntry, id)

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

@app.route('/api/loot', methods=['GET', 'POST'])
def loot(): return handle_entities(Loot)
@app.route('/api/loot/<int:id>', methods=['PUT', 'DELETE'])
def modify_loot(id): return modify_entity(Loot, id)

@app.route('/api/treasury', methods=['GET', 'PUT'])
def handle_treasury():
    t = Treasury.query.first()
    if request.method == 'PUT':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        if 'platinum' in data: t.platinum = int(data['platinum'])
        if 'gold' in data: t.gold = int(data['gold'])
        if 'silver' in data: t.silver = int(data['silver'])
        if 'copper' in data: t.copper = int(data['copper'])
        db.session.commit()
        return jsonify({"message": "Treasury updated"}), 200
    return jsonify({"platinum": t.platinum, "gold": t.gold, "silver": t.silver, "copper": t.copper})

@app.route('/api/campaign_state', methods=['GET', 'PUT'])
def handle_campaign_state():
    state = CampaignState.query.first()
    if request.method == 'PUT':
        if get_auth_role() != 'admin': return jsonify({"error": "Only DM can change weather"}), 401
        data = request.json
        if 'day' in data: state.day = int(data['day'])
        if 'month' in data: state.month = data['month']
        if 'year' in data: state.year = int(data['year'])
        if 'weather' in data: state.weather = data['weather']
        db.session.commit()
        return jsonify({"message": "State updated"}), 200
    return jsonify({"day": state.day, "month": state.month, "year": state.year, "weather": state.weather})

@app.route('/api/spells', methods=['GET', 'POST'])
def spells():
    if request.method == 'POST':
        if not is_auth(): return jsonify({"error": "Unauthorized"}), 401
        new_spell = Spell(
            character_id=int(request.form.get('character_id')),
            name=request.form.get('name'), level_school=request.form.get('level_school', ''),
            casting_time=request.form.get('casting_time', ''), range=request.form.get('range', ''),
            components=request.form.get('components', ''), duration=request.form.get('duration', ''),
            description=request.form.get('description', ''), classes=request.form.get('classes', ''),
            source=request.form.get('source', '')
        )
        db.session.add(new_spell); db.session.commit()
        return jsonify({"message": "Spell created"}), 201

    char_id = request.args.get('character_id')
    spells_query = Spell.query.filter_by(character_id=int(char_id)).all() if char_id else Spell.query.all()
    return jsonify([{"id": s.id, "character_id": s.character_id, "name": s.name, "level_school": s.level_school, "casting_time": s.casting_time, "range": s.range, "components": s.components, "duration": s.duration, "description": s.description, "classes": s.classes, "source": s.source} for s in spells_query])

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
        db.session.delete(spell); db.session.commit()
        return jsonify({"message": "Deleted"}), 200

if __name__ == '__main__':
    app.run(debug=True)