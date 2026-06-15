import os
from flask import Flask, render_template, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from sqlalchemy import text

# =============================================================================
# FLASK APP INITIALISIERUNG
# =============================================================================

app = Flask(__name__)

# Geheimer Schlüssel für Flask-Sessions (wird für Login-Status benötigt)
app.secret_key = 'tiamat_is_rising_secret_key_12345'

# Absoluter Pfad zum aktuellen Verzeichnis (wichtig für PythonAnywhere & portable Nutzung)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# SQLite-Datenbank im selben Ordner wie die App
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'dnd_campaign.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Deaktiviert unnötige Warnungen

# Ordner für hochgeladene Bilder (wird automatisch erstellt)
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# SQLAlchemy-Datenbank-Instanz
db = SQLAlchemy(app)


# =============================================================================
# DATENBANK-MODELLE (Tabellen-Struktur)
# =============================================================================

class Pin(db.Model):
    """Karten-Pins / Marker auf der Weltkarte"""
    id = db.Column(db.Integer, primary_key=True)
    y = db.Column(db.Float, nullable=False)           # Y-Koordinate (Breite)
    x = db.Column(db.Float, nullable=False)           # X-Koordinate (Länge)
    title = db.Column(db.String(100), nullable=False) # Name des Pins
    image = db.Column(db.String(300))                 # Bild-URL (optional)
    description = db.Column(db.Text)                  # Lange Beschreibung
    order_index = db.Column(db.Integer, default=0)    # Reihenfolge auf der Karte


class Character(db.Model):
    """Spieler-Charaktere"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))           # Charakterbild
    description = db.Column(db.Text)
    background = db.Column(db.String(100))      # Herkunft / Hintergrundgeschichte
    age = db.Column(db.String(50))
    appearance = db.Column(db.Text)             # Aussehen
    spellbook_image = db.Column(db.String(300)) # Bild des Zauberbuchs
    char_password = db.Column(db.String(100))   # Optionales Passwort für den Charakter


class NPC(db.Model):
    """Nicht-Spieler-Charaktere"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    reputation = db.Column(db.Integer, default=50)  # Ruf (0-100)
    appearance = db.Column(db.Text)
    faction_alignment = db.Column(db.String(100))   # Fraktion / Gesinnung
    special = db.Column(db.Text)                    # Besondere Eigenschaften / Hooks


class Faction(db.Model):
    """Fraktionen / Organisationen"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    leader = db.Column(db.String(100))
    goal = db.Column(db.Text)
    known_for = db.Column(db.Text)


class Dragon(db.Model):
    """Drachen (sehr detailliert)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)
    physiology = db.Column(db.Text)   # Körperbau / Physiologie
    abilities = db.Column(db.Text)    # Fähigkeiten
    behavior = db.Column(db.Text)     # Verhalten
    habitat = db.Column(db.Text)      # Lebensraum


class Gallery(db.Model):
    """Allgemeine Galerie-Bilder"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)


class Bastion(db.Model):
    """Bastionen / Festungen"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)


class Protocol(db.Model):
    """Protokolle / wichtige Dokumente"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(300))
    description = db.Column(db.Text)


class Spell(db.Model):
    """Zaubersprüche (gehören zu einem Charakter)"""
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
    """Quests / Aufträge"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    is_group = db.Column(db.Boolean, default=True)      # Gruppenquest oder Einzelquest?
    character_id = db.Column(db.Integer, nullable=True) # Bei Einzelquest: welcher Charakter?
    status = db.Column(db.String(50), default='active') # active, completed, failed...


class BastionToken(db.Model):
    """Tokens auf Bastionskarten (z.B. Feinde, NPCs, Schätze)"""
    id = db.Column(db.Integer, primary_key=True)
    bastion_id = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Float, nullable=False)
    x = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(100), nullable=False)
    icon_type = db.Column(db.String(50), nullable=False)  # z.B. "enemy", "npc", "treasure"


# --- NEU: Schatzkammer ---
class Treasury(db.Model):
    """Globale Schatzkammer der Gruppe"""
    id = db.Column(db.Integer, primary_key=True)
    platinum = db.Column(db.Integer, default=0)
    gold = db.Column(db.Integer, default=0)
    silver = db.Column(db.Integer, default=0)
    copper = db.Column(db.Integer, default=0)


class Loot(db.Model):
    """Beute / Items (können Charakteren zugeordnet werden)"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image = db.Column(db.String(300))
    holder_id = db.Column(db.Integer, nullable=True)  # Character-ID des Besitzers


# =============================================================================
# DATENBANK INITIALISIERUNG + MIGRATIONEN
# =============================================================================

with app.app_context():
    db.create_all()  # Erstellt alle Tabellen, falls sie noch nicht existieren

    # Initiale Schatzkammer anlegen (falls noch nicht vorhanden)
    if not Treasury.query.first():
        db.session.add(Treasury(platinum=0, gold=0, silver=0, copper=0))
        db.session.commit()

    # --- Automatische Spalten-Ergänzung (für bestehende Datenbanken) ---
    # Diese TRY-EXCEPT-Blöcke fügen fehlende Spalten hinzu, ohne die DB zu zerstören
    try:
        db.session.execute(text("ALTER TABLE character ADD COLUMN background VARCHAR(100)"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE character ADD COLUMN age VARCHAR(50)"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE character ADD COLUMN appearance TEXT"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE character ADD COLUMN spellbook_image VARCHAR(300)"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE character ADD COLUMN char_password VARCHAR(100)"))
        db.session.commit()
    except:
        db.session.rollback()

    # Weitere Spalten-Ergänzungen für NPC, Faction, Dragon...
    try:
        db.session.execute(text("ALTER TABLE npc ADD COLUMN reputation INTEGER DEFAULT 50"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE npc ADD COLUMN appearance TEXT"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE npc ADD COLUMN faction_alignment VARCHAR(100)"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE npc ADD COLUMN special TEXT"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE faction ADD COLUMN leader VARCHAR(100)"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE faction ADD COLUMN goal TEXT"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE faction ADD COLUMN known_for TEXT"))
        db.session.commit()
    except:
        db.session.rollback()

    try:
        db.session.execute(text("ALTER TABLE dragon ADD COLUMN physiology TEXT"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE dragon ADD COLUMN abilities TEXT"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE dragon ADD COLUMN behavior TEXT"))
        db.session.commit()
    except:
        db.session.rollback()
    try:
        db.session.execute(text("ALTER TABLE dragon ADD COLUMN habitat TEXT"))
        db.session.commit()
    except:
        db.session.rollback()


# =============================================================================
# HILFSFUNKTIONEN
# =============================================================================

def save_image(file):
    """Speichert ein hochgeladenes Bild sicher und gibt den relativen Pfad zurück"""
    if file and file.filename != '':
        filename = secure_filename(file.filename)  # Verhindert gefährliche Dateinamen
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return f"/static/uploads/{filename}"
    return ""


def get_auth_role():
    """Gibt die aktuelle Rolle aus der Session zurück ('admin', 'editor' oder 'none')"""
    return session.get('role', 'none')


def is_auth():
    """Prüft, ob der Benutzer eingeloggt ist (admin oder editor)"""
    return get_auth_role() in ['editor', 'admin']


# =============================================================================
# AUTHENTIFIZIERUNG (sehr einfach gehalten – nur für Demo / intern)
# =============================================================================

@app.route('/api/login', methods=['POST'])
def login():
    """Login-Endpunkt. Aktuell sehr simpel (leere Credentials = Login)"""
    data = request.json
    u = data.get('username')
    p = data.get('password')

    # !!! ACHTUNG: Das ist nur ein Platzhalter für Demo-Zwecke !!!
    if u == '' and p == '':
        session['role'] = 'admin'
        return jsonify({"success": True, "role": "admin"})
    elif u == '' and p == '':
        session['role'] = 'editor'
        return jsonify({"success": True, "role": "editor"})

    return jsonify({"success": False}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout – entfernt die Rolle aus der Session"""
    session.pop('role', None)
    return jsonify({"success": True})


@app.route('/api/auth_status', methods=['GET'])
def auth_status():
    """Gibt die aktuelle Rolle zurück (für Frontend-Checks)"""
    return jsonify({"role": get_auth_role()})


@app.route('/api/verify_char_pwd', methods=['POST'])
def verify_char_pwd():
    """Prüft das optionale Charakter-Passwort"""
    data = request.json
    char_id = data.get('char_id')
    pwd = data.get('password')
    char = Character.query.get(char_id)
    if char and char.char_password == pwd:
        return jsonify({"success": True})
    return jsonify({"success": False})


# =============================================================================
# MAP & TOKENS
# =============================================================================

@app.route('/')
def index():
    """Startseite – lädt das Haupt-Template"""
    return render_template('index.html')


@app.route('/api/pins', methods=['GET', 'POST'])
def handle_pins():
    """Pins auf der Weltkarte verwalten"""
    if request.method == 'POST':
        if not is_auth():
            return jsonify({"error": "Unauthorized"}), 401

        # Neuer Pin wird erstellt
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

    # Alle Pins zurückgeben (sortiert)
    pins = Pin.query.order_by(Pin.order_index).all()
    return jsonify([{
        "id": p.id, "y": p.y, "x": p.x, "title": p.title,
        "image": p.image, "description": p.description, "order_index": p.order_index
    } for p in pins])


@app.route('/api/pins/<int:id>', methods=['PUT', 'DELETE'])
def modify_pin(id):
    """Einzelnen Pin bearbeiten oder löschen"""
    if not is_auth():
        return jsonify({"error": "Unauthorized"}), 401

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
            if 'title' in request.form:
                pin.title = request.form['title']
            if 'description' in request.form:
                pin.description = request.form['description']
            new_image = save_image(request.files.get('image'))
            if new_image:
                pin.image = new_image
        db.session.commit()
        return jsonify({"message": "Pin updated"}), 200

    elif request.method == 'DELETE':
        db.session.delete(pin)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200


# Bastion-Tokens (Tokens auf Bastionskarten)
@app.route('/api/bastion/<int:b_id>/tokens', methods=['GET', 'POST'])
def handle_bastion_tokens(b_id):
    if request.method == 'POST':
        if not is_auth():
            return jsonify({"error": "Unauthorized"}), 401
        new_t = BastionToken(
            bastion_id=b_id,
            y=float(request.form.get('y')),
            x=float(request.form.get('x')),
            label=request.form.get('label', 'Token'),
            icon_type=request.form.get('icon_type', 'enemy')
        )
        db.session.add(new_t)
        db.session.commit()
        return jsonify({"success": True, "id": new_t.id}), 201

    tokens = BastionToken.query.filter_by(bastion_id=b_id).all()
    return jsonify([{
        "id": t.id, "y": t.y, "x": t.x, "label": t.label, "icon_type": t.icon_type
    } for t in tokens])


@app.route('/api/bastion/tokens/<int:t_id>', methods=['PUT', 'DELETE'])
def modify_bastion_token(t_id):
    if not is_auth():
        return jsonify({"error": "Unauthorized"}), 401
    t = BastionToken.query.get_or_404(t_id)

    if request.method == 'PUT':
        data = request.json
        if data:
            if 'y' in data:
                t.y = float(data['y'])
            if 'x' in data:
                t.x = float(data['x'])
        db.session.commit()
        return jsonify({"success": True}), 200
    elif request.method == 'DELETE':
        db.session.delete(t)
        db.session.commit()
        return jsonify({"success": True}), 200


# =============================================================================
# GENERISCHE ENTITY-HANDLER (sehr clever gelöst)
# =============================================================================

def handle_entities(model):
    """
    Generische Funktion zum Erstellen und Auflisten von Entities.
    Wird von fast allen CRUD-Routen wiederverwendet.
    """
    if request.method == 'POST':
        if not is_auth():
            return jsonify({"error": "Unauthorized"}), 401

        # Spezialfall Quest
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

        # Standard-Entity erstellen
        kwargs = {
            'name': request.form.get('name'),
            'description': request.form.get('description')
        }
        image_url = save_image(request.files.get('image'))
        if image_url:
            kwargs['image'] = image_url

        # Modell-spezifische Felder hinzufügen
        if model == Character:
            kwargs['background'] = request.form.get('background', '')
            kwargs['age'] = request.form.get('age', '')
            kwargs['appearance'] = request.form.get('appearance', '')
            kwargs['char_password'] = request.form.get('char_password', '')
            sb_img = save_image(request.files.get('spellbook_image'))
            if sb_img:
                kwargs['spellbook_image'] = sb_img
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
        elif model == Loot:
            h_id = request.form.get('holder_id')
            kwargs['holder_id'] = int(h_id) if h_id else None

        new_entity = model(**kwargs)
        db.session.add(new_entity)
        db.session.commit()
        return jsonify({"message": "Created", "id": new_entity.id}), 201

    # GET: Alle Einträge zurückgeben (mit modellspezifischen Feldern)
    entities = model.query.all()
    result = []
    for e in entities:
        if model == Quest:
            result.append({
                "id": e.id, "title": e.title, "description": e.description,
                "is_group": e.is_group, "character_id": e.character_id, "status": e.status
            })
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
        elif model == Loot:
            data['holder_id'] = getattr(e, 'holder_id', None)

        result.append(data)
    return jsonify(result)


def modify_entity(model, id):
    """Generische Funktion zum Bearbeiten/Löschen einzelner Entities"""
    if not is_auth():
        return jsonify({"error": "Unauthorized"}), 401

    entity = model.query.get_or_404(id)

    if request.method == 'PUT':
        if model == Quest:
            if 'title' in request.form:
                entity.title = request.form['title']
            if 'description' in request.form:
                entity.description = request.form['description']
            if 'status' in request.form:
                entity.status = request.form['status']
            db.session.commit()
            return jsonify({"message": "Updated"}), 200

        # Standard-Felder
        if 'name' in request.form:
            entity.name = request.form['name']
        if 'description' in request.form:
            entity.description = request.form['description']

        # Modell-spezifische Felder
        if model == Character:
            if 'background' in request.form:
                entity.background = request.form['background']
            if 'age' in request.form:
                entity.age = request.form['age']
            if 'appearance' in request.form:
                entity.appearance = request.form['appearance']
            pwd = request.form.get('char_password')
            if pwd:
                entity.char_password = pwd
            new_sb_img = save_image(request.files.get('spellbook_image'))
            if new_sb_img:
                entity.spellbook_image = new_sb_img
        elif model == NPC:
            if 'reputation' in request.form:
                entity.reputation = int(request.form['reputation'])
            if 'appearance' in request.form:
                entity.appearance = request.form['appearance']
            if 'faction_alignment' in request.form:
                entity.faction_alignment = request.form['faction_alignment']
            if 'special' in request.form:
                entity.special = request.form['special']
        elif model == Faction:
            if 'leader' in request.form:
                entity.leader = request.form['leader']
            if 'goal' in request.form:
                entity.goal = request.form['goal']
            if 'known_for' in request.form:
                entity.known_for = request.form['known_for']
        elif model == Dragon:
            if 'physiology' in request.form:
                entity.physiology = request.form['physiology']
            if 'abilities' in request.form:
                entity.abilities = request.form['abilities']
            if 'behavior' in request.form:
                entity.behavior = request.form['behavior']
            if 'habitat' in request.form:
                entity.habitat = request.form['habitat']
        elif model == Loot:
            h_id = request.form.get('holder_id')
            entity.holder_id = int(h_id) if h_id else None

        new_image = save_image(request.files.get('image'))
        if new_image:
            entity.image = new_image

        db.session.commit()
        return jsonify({"message": "Updated"}), 200

    elif request.method == 'DELETE':
        db.session.delete(entity)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200


# =============================================================================
# SPEZIFISCHE API-ROUTEN (CRUD)
# =============================================================================

@app.route('/api/chars', methods=['GET', 'POST'])
def chars():
    return handle_entities(Character)

@app.route('/api/chars/<int:id>', methods=['PUT', 'DELETE'])
def modify_char(id):
    return modify_entity(Character, id)

@app.route('/api/npcs', methods=['GET', 'POST'])
def npcs():
    return handle_entities(NPC)

@app.route('/api/npcs/<int:id>', methods=['PUT', 'DELETE'])
def modify_npc(id):
    return modify_entity(NPC, id)

@app.route('/api/factions', methods=['GET', 'POST'])
def factions():
    return handle_entities(Faction)

@app.route('/api/factions/<int:id>', methods=['PUT', 'DELETE'])
def modify_faction(id):
    return modify_entity(Faction, id)

@app.route('/api/dragons', methods=['GET', 'POST'])
def dragons():
    return handle_entities(Dragon)

@app.route('/api/dragons/<int:id>', methods=['PUT', 'DELETE'])
def modify_dragon(id):
    return modify_entity(Dragon, id)

@app.route('/api/gallery', methods=['GET', 'POST'])
def gallery():
    return handle_entities(Gallery)

@app.route('/api/gallery/<int:id>', methods=['PUT', 'DELETE'])
def modify_gallery(id):
    return modify_entity(Gallery, id)

@app.route('/api/bastion', methods=['GET', 'POST'])
def bastion():
    return handle_entities(Bastion)

@app.route('/api/bastion/<int:id>', methods=['PUT', 'DELETE'])
def modify_bastion(id):
    return modify_entity(Bastion, id)

@app.route('/api/protocols', methods=['GET', 'POST'])
def protocols():
    return handle_entities(Protocol)

@app.route('/api/protocols/<int:id>', methods=['PUT', 'DELETE'])
def modify_protocol(id):
    return modify_entity(Protocol, id)

@app.route('/api/quests', methods=['GET', 'POST'])
def quests():
    return handle_entities(Quest)

@app.route('/api/quests/<int:id>', methods=['PUT', 'DELETE'])
def modify_quest(id):
    return modify_entity(Quest, id)

@app.route('/api/loot', methods=['GET', 'POST'])
def loot():
    return handle_entities(Loot)

@app.route('/api/loot/<int:id>', methods=['PUT', 'DELETE'])
def modify_loot(id):
    return modify_entity(Loot, id)


# =============================================================================
# TREASURY (Schatzkammer)
# =============================================================================

@app.route('/api/treasury', methods=['GET', 'PUT'])
def handle_treasury():
    t = Treasury.query.first()
    if request.method == 'PUT':
        if not is_auth():
            return jsonify({"error": "Unauthorized"}), 401
        data = request.json
        if 'platinum' in data:
            t.platinum = int(data['platinum'])
        if 'gold' in data:
            t.gold = int(data['gold'])
        if 'silver' in data:
            t.silver = int(data['silver'])
        if 'copper' in data:
            t.copper = int(data['copper'])
        db.session.commit()
        return jsonify({"message": "Treasury updated"}), 200

    return jsonify({
        "platinum": t.platinum,
        "gold": t.gold,
        "silver": t.silver,
        "copper": t.copper
    })


# =============================================================================
# SPELLS (Zaubersprüche)
# =============================================================================

@app.route('/api/spells', methods=['GET', 'POST'])
def spells():
    if request.method == 'POST':
        if not is_auth():
            return jsonify({"error": "Unauthorized"}), 401
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
    if not is_auth():
        return jsonify({"error": "Unauthorized"}), 401
    spell = Spell.query.get_or_404(id)

    if request.method == 'PUT':
        if 'name' in request.form:
            spell.name = request.form['name']
        if 'level_school' in request.form:
            spell.level_school = request.form['level_school']
        if 'casting_time' in request.form:
            spell.casting_time = request.form['casting_time']
        if 'range' in request.form:
            spell.range = request.form['range']
        if 'components' in request.form:
            spell.components = request.form['components']
        if 'duration' in request.form:
            spell.duration = request.form['duration']
        if 'description' in request.form:
            spell.description = request.form['description']
        if 'classes' in request.form:
            spell.classes = request.form['classes']
        if 'source' in request.form:
            spell.source = request.form['source']
        db.session.commit()
        return jsonify({"message": "Spell updated"}), 200
    elif request.method == 'DELETE':
        db.session.delete(spell)
        db.session.commit()
        return jsonify({"message": "Deleted"}), 200


# =============================================================================
# APP START
# =============================================================================

if __name__ == '__main__':
    app.run(debug=True)