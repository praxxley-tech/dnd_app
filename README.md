<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Tyranny of Dragons Adventure Log</title>
    
    <!-- Leaflet CSS für die interaktive Karte -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <!-- Schöne Fantasy-Schriftarten -->
    <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">

    <style>
        /* ========== CSS VARIABLEN (Theme) ========== */
        :root {
            --text-color: #e0e0e0;
            --primary-color: #cda434;      /* Goldener Akzent */
            --nav-bg: rgba(17, 17, 17, 0.9);
            --card-bg: rgba(35, 35, 35, 0.85);
            --danger-color: #b33a3a;
        }

        /* ========== GRUNDSTYLING ========== */
        body { 
            margin: 0; 
            font-family: 'Lora', serif; 
            color: var(--text-color); 
            display: flex; 
            flex-direction: column; 
            height: 100vh; 
            background-image: linear-gradient(rgba(15, 15, 15, 0.8), rgba(15, 15, 15, 0.8)), url('/static/bg.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Navigation oben */
        nav { 
            background-color: var(--nav-bg); 
            padding: 15px 20px; 
            display: flex; 
            align-items: center; 
            gap: 8px; 
            border-bottom: 2px solid var(--primary-color); 
            z-index: 1000; 
            backdrop-filter: blur(5px); 
            flex-wrap: wrap;
        }
        
        .nav-brand { display: flex; align-items: center; gap: 15px; margin-right: auto; }
        .nav-brand img { height: 40px; object-fit: contain; }
        .nav-brand h1 { margin: 0; font-family: 'Cinzel', serif; color: var(--primary-color); font-size: 20px; text-shadow: 2px 2px 4px #000;}
        
        /* Tab-Buttons in der Navigation */
        .tab-btn { 
            background: none; 
            border: none; 
            color: var(--text-color); 
            font-family: 'Cinzel', serif; 
            font-size: 15px; 
            cursor: pointer; 
            padding: 5px 8px; 
            transition: color 0.3s; 
            text-shadow: 1px 1px 2px #000; 
        }
        .tab-btn:hover, .tab-btn.active { color: var(--primary-color); border-bottom: 1px solid var(--primary-color); }

        /* Sektionen (die einzelnen Tabs) */
        .section { display: none; flex-grow: 1; padding: 20px; overflow-y: auto; }
        .section.active { display: block; }
        #map-section.active { display: flex; padding: 0; overflow: hidden; position: relative; }
        #map { width: 100%; height: 100%; background-color: #000; }

        /* Leaflet Popup Styling (sehr wichtig für das schöne Aussehen) */
        .leaflet-popup-content-wrapper { 
            background-color: var(--card-bg); 
            color: var(--text-color); 
            border: 1px solid var(--primary-color); 
            border-radius: 8px; 
            width: 280px; 
            backdrop-filter: blur(5px); 
        }
        .leaflet-popup-tip { background-color: var(--card-bg); }
        
        /* Allgemeine Button-Styles */
        .btn { 
            background-color: var(--primary-color); 
            color: #000; 
            border: none; 
            padding: 5px 10px; 
            cursor: pointer; 
            font-family: 'Cinzel', serif; 
            border-radius: 3px; 
            width: 100%; 
            font-weight: bold; 
            box-sizing: border-box;
        }
        .btn-danger { background-color: var(--danger-color); color: white; margin-top: 5px; }

        /* Grid für die Karten */
        .grid-container { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 20px; 
            max-width: 1200px; 
            margin: 0 auto; 
            align-items: start;
        }
        
        /* Karten-Design */
        .card { 
            background-color: var(--card-bg); 
            border: 1px solid #444; 
            border-radius: 8px; 
            overflow: hidden; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); 
            backdrop-filter: blur(3px); 
        }
        .card-content { padding: 15px; }
        .card-content h3 { margin: 0 0 10px 0; font-family: 'Cinzel', serif; color: var(--primary-color); }
        .card-content p { margin: 0; font-size: 14px; line-height: 1.5; white-space: pre-wrap; }
        
        /* "Add New"-Details-Elemente */
        .add-details { margin: 0 auto 20px auto; max-width: 1200px; text-align: center; }
        .add-details summary { 
            display: inline-block; 
            background-color: var(--primary-color); 
            color: #000; 
            padding: 10px 20px; 
            font-family: 'Cinzel', serif; 
            font-weight: bold; 
            border-radius: 4px; 
            cursor: pointer; 
            list-style: none; 
            transition: background-color 0.2s; 
            box-shadow: 0 4px 10px rgba(0,0,0,0.5); 
        }
        .add-details summary:hover { background-color: #e6b800; }
        
        /* Formulare zum Hinzufügen */
        .add-form { 
            background-color: var(--card-bg); 
            padding: 15px; 
            border: 1px dashed var(--primary-color); 
            border-radius: 8px; 
            display: flex; 
            gap: 10px; 
            flex-wrap: wrap; 
            backdrop-filter: blur(5px); 
            margin-top: 15px; 
            text-align: left;
        }
        .add-form input, .add-form textarea, .add-form select { 
            background: rgba(0,0,0,0.6); 
            color: #fff; 
            border: 1px solid #444; 
            padding: 8px; 
            flex-grow: 1; 
            min-width: 200px; 
            font-family: inherit; 
            box-sizing: border-box;
        }
        
        /* Spezielle Styles für Charakter-Details, Reputation-Bars, Bücher etc. */
        .char-details { padding: 15px; }
        .char-details summary { list-style: none; cursor: pointer; outline: none; }
        .char-details summary::-webkit-details-marker { display: none; }
        
        .char-summary-header, .dragon-summary-header, .faction-summary-header { 
            display: flex; 
            align-items: center; 
            gap: 15px; 
            min-height: 95px; 
            padding: 5px 0; 
        }
        
        .char-summary-header img { width: 70px; height: 70px; object-fit: cover; border-radius: 50%; border: 2px solid var(--primary-color); background-color: #000; flex-shrink: 0; }
        .dragon-summary-header img { width: 70px; height: 70px; object-fit: cover; border-radius: 8px; border: 2px solid var(--primary-color); background-color: #000; flex-shrink: 0; }
        .faction-summary-header img { width: 70px; height: 70px; object-fit: scale-down; border-radius: 4px; border: 2px solid var(--primary-color); background-color: #000; flex-shrink: 0; }

        /* D&D Sheet Style für erweiterte Details */
        .dnd-sheet-full { margin-top: 15px; border-top: 1px dashed var(--primary-color); padding-top: 15px; display: flex; flex-direction: column; gap: 12px; }
        .dnd-stat-box { background: rgba(10,10,10,0.6); border: 1px solid #444; padding: 10px; border-radius: 4px; border-left: 3px solid var(--primary-color); }
        .dnd-stat-label { font-size: 10px; color: var(--primary-color); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 3px; font-family: 'Cinzel', serif;}
        .dnd-stat-value { font-size: 14px; white-space: pre-wrap; line-height: 1.4; }

        /* Reputation Bar */
        .rep-container { width: 100%; background: #111; border: 1px solid #444; border-radius: 4px; height: 12px; overflow: hidden; position: relative; }
        .rep-bar { height: 100%; transition: width 0.4s ease, background-color 0.4s ease; }

        /* ========== SPELLBOOK & QUESTBOOK STYLING ========== */
        .spellbook-wrapper, .quest-book-wrapper { grid-column: 1 / -1; display: flex; justify-content: center; width: 100%; padding: 20px 0; }
        
        .spellbook-cover { 
            background: linear-gradient(135deg, #1f0d35, #42236d); 
            border: 4px solid #cda434; 
            border-radius: 5px 18px 18px 5px; 
            box-shadow: inset 10px 0 30px rgba(0,0,0,0.8), 10px 10px 25px rgba(0,0,0,0.7); 
            color: #cda434; 
            text-align: center; 
            padding: 80px 30px; 
            cursor: pointer; 
            transition: transform 0.3s ease, box-shadow 0.3s ease; 
            width: 100%; 
            max-width: 350px; 
            user-select: none; 
        }
        .spellbook-cover:hover { transform: scale(1.03) perspective(500px) rotateY(-5deg); box-shadow: inset 10px 0 30px rgba(0,0,0,0.8), 15px 15px 30px rgba(0,0,0,0.8); }

        .custom-spellbook-cover { border: none; border-radius: 5px 18px 18px 5px; box-shadow: 10px 10px 25px rgba(0,0,0,0.7); cursor: pointer; transition: transform 0.3s ease, box-shadow 0.3s ease; width: 100%; max-width: 350px; overflow: hidden; display: flex; }
        .custom-spellbook-cover:hover { transform: scale(1.03) perspective(500px) rotateY(-5deg); box-shadow: 15px 15px 30px rgba(0,0,0,0.8); }
        .custom-spellbook-cover img { width: 100%; height: 400px; object-fit: cover; display: block; }

        .spellbook-pages { 
            background: #fdf6e3; 
            color: #000; 
            border: 2px solid #8b5a2b; 
            border-radius: 2px 12px 12px 2px; 
            box-shadow: inset 20px 0 25px rgba(0,0,0,0.1), 10px 10px 30px rgba(0,0,0,0.6); 
            padding: 30px; 
            width: 100%; 
            max-width: 650px; 
            position: relative; 
            animation: openBookAnim 0.5s ease-out forwards; 
        }
        @keyframes openBookAnim { 0% { transform: rotateY(-90deg) scale(0.8); opacity: 0; } 100% { transform: rotateY(0) scale(1); opacity: 1; } }

        /* Weitere Buch- und Quest-Styles (gekürzt für Übersichtlichkeit) */
        .quest-cover { background-image: url('/static/acc.jpg'); background-size: cover; background-position: center; border: 4px solid #cda434; border-radius: 8px; box-shadow: 10px 10px 25px rgba(0,0,0,0.8); cursor: pointer; transition: transform 0.4s ease, box-shadow 0.4s ease; width: 100%; max-width: 400px; height: 550px; user-select: none; position: relative; }
        .quest-cover:hover { transform: scale(1.02) perspective(600px) rotateY(-5deg); box-shadow: 15px 15px 35px rgba(0,0,0,0.9); }

        .protocol-cover { background-image: url('/static/council.jpg'); background-size: cover; background-position: center; border: 4px solid #cda434; border-radius: 8px; box-shadow: 10px 10px 25px rgba(0,0,0,0.8); cursor: pointer; transition: transform 0.4s ease, box-shadow 0.4s ease; width: 100%; max-width: 400px; height: 550px; user-select: none; position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; }
        .protocol-cover:hover { transform: scale(1.02) perspective(600px) rotateY(-5deg); box-shadow: 15px 15px 35px rgba(0,0,0,0.9); }

        /* Treasury Styling */
        .treasury-board { background: #1a1a1a; border: 2px solid var(--primary-color); border-radius: 8px; padding: 20px; text-align: center; margin-bottom: 20px; box-shadow: inset 0 0 20px rgba(0,0,0,0.8); }
        .coin-box { background: #000; border: 1px solid #444; padding: 10px 15px; border-radius: 5px; min-width: 100px; box-shadow: 2px 2px 5px rgba(0,0,0,0.5); }
        .coin-box.pp { border-bottom: 4px solid #e5e4e2; }
        .coin-box.gp { border-bottom: 4px solid #ffd700; }
        .coin-box.sp { border-bottom: 4px solid #c0c0c0; }
        .coin-box.cp { border-bottom: 4px solid #b87333; }

        /* Edit-Mode Sichtbarkeit */
        .action-buttons, .route-edit, .add-details, .edit-treasury-btns { display: none !important; }
        body.edit-mode .action-buttons, 
        body.edit-mode .route-edit, 
        body.edit-mode .edit-treasury-btns { display: flex !important; }
        body.edit-mode .add-details { display: block !important; }
    </style>
</head>
<body>

    <!-- ========== NAVIGATION ========== -->
    <nav>
        <div class="nav-brand">
            <img src="/static/logo.jpg" alt="Tyranny of Dragons">
            <h1>Tyranny of Dragons</h1>
        </div>
        
        <!-- Tab-Buttons -->
        <button class="tab-btn active" onclick="switchTab('map-section', this)">World Map</button>
        <button class="tab-btn" onclick="switchTab('chars-section', this)">Characters</button>
        <button class="tab-btn" onclick="switchTab('npcs-section', this)">NPCs</button>
        <button class="tab-btn" onclick="switchTab('factions-section', this)">Factions</button>
        <button class="tab-btn" onclick="switchTab('dragons-section', this)">Dragons</button>
        <button class="tab-btn" onclick="switchTab('gallery-section', this)">Gallery</button>
        <button class="tab-btn" onclick="switchTab('bastion-section', this)">Bastion Maps</button>
        <button class="tab-btn" onclick="switchTab('protocols-section', this)">Council</button>
        <button class="tab-btn" onclick="switchTab('spells-section', this)">Spellbook</button>
        <button class="tab-btn" onclick="switchTab('quests-section', this)">Quests</button>
        <button class="tab-btn" onclick="switchTab('treasury-section', this)">Treasury</button>

        <!-- Login / Edit Mode Buttons -->
        <button id="auth-btn" class="btn" style="width: auto; padding: 5px 15px; background-color: #3ab34a; color: white; border: 1px solid var(--primary-color); margin-left:auto;" onclick="openLogin()">🔒 Login</button>
        <button id="edit-mode-btn" class="btn" style="display: none; width: auto; padding: 5px 15px; background-color: #555; color: white; border: 1px solid var(--primary-color);" onclick="toggleEditMode()">👁️ View Mode</button>
    </nav>

    <main style="display: flex; flex-grow: 1; overflow: hidden;">
        
        <!-- ========== WELTKARTE ========== -->
        <div id="map-section" class="section active">
            <div id="map"></div>
        </div>

        <!-- ========== CHARACTERS ========== -->
        <div id="chars-section" class="section">
            <details class="add-details" id="details-chars">
                <summary>➕ Add New Character</summary>
                <div class="add-form">
                    <!-- Formularfelder für neuen Charakter -->
                    <input type="text" id="char-name" placeholder="Character Name" style="width: 100%;">
                    <!-- ... weitere Felder ... -->
                    <button class="btn" style="width:100%; margin-top: 10px;" onclick="addEntity('chars')">Save Character</button>
                </div>
            </details>
            <div class="grid-container" id="chars-grid"></div>
        </div>

        <!-- Weitere Sektionen (NPCs, Factions, Dragons, Gallery, Bastion, Protocols, Spells, Quests, Treasury) -->
        <!-- ... (ähnliche Struktur wie oben) ... -->

    </main>

    <!-- Login Modal -->
    <div id="login-modal" style="display:none; ...">
        <!-- Login-Formular -->
    </div>

    <!-- Lightbox für Bilder -->
    <div id="lightbox-modal" ... onclick="closeLightbox()">
        <!-- Großes Bild + Titel + Beschreibung -->
    </div>

    <!-- Leaflet JavaScript -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

    <script>
        // ========== GLOBALE VARIABLEN ==========
        let editMode = false;
        let authRole = 'none'; 
        
        let isSpellbookOpen = false;
        let activeSpellId = null;

        let isQuestbookOpen = false;
        let currentQuestPage = 'group'; 
        let allQuests = [];
        let charactersData = [];
        let unlockedCharId = null; 

        let isProtocolBookOpen = false;
        let activeProtocolId = null;
        let allProtocols = [];

        let bastionMap = null;
        let activeBastionId = null;
        let bastionImageOverlay = null;

        // ========== AUTHENTIFIZIERUNG ==========
        async function checkAuth() {
            // Holt den aktuellen Login-Status vom Backend
            const res = await fetch('/api/auth_status');
            const data = await res.json();
            authRole = data.role;
            
            // Passt Login-Button und Edit-Button entsprechend an
            const editBtn = document.getElementById('edit-mode-btn');
            const authBtn = document.getElementById('auth-btn');
            
            if(authRole === 'editor' || authRole === 'admin') {
                editBtn.style.display = 'inline-block';
                authBtn.innerHTML = '🔓 Logout' + (authRole==='admin'?' (DM)':'');
                authBtn.onclick = performLogout;
                authBtn.style.backgroundColor = '#b33a3a';
            } else {
                editBtn.style.display = 'none';
                authBtn.innerHTML = '🔒 Login';
                authBtn.onclick = openLogin;
                authBtn.style.backgroundColor = '#3ab34a';
                if(editMode) toggleEditMode();
            }
        }

        function openLogin() { 
            document.getElementById('login-modal').style.display = 'flex'; 
        }
        
        async function performLogin() {
            // Sendet Login-Daten an das Backend
            const u = document.getElementById('login-user').value;
            const p = document.getElementById('login-pass').value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            if(res.ok) {
                closeLogin();
                checkAuth();
            } else {
                alert('Incorrect Username or Password!');
            }
        }

        async function performLogout() {
            await fetch('/api/logout', { method: 'POST' });
            checkAuth();
        }

        // ========== EDIT MODE TOGGLE ==========
        function toggleEditMode() {
            editMode = !editMode;
            const btn = document.getElementById('edit-mode-btn');
            
            if (editMode) {
                document.body.classList.add('edit-mode');
                btn.innerHTML = '🛠️ Edit Mode';
                btn.style.backgroundColor = 'var(--primary-color)';
                btn.style.color = '#000';
            } else {
                document.body.classList.remove('edit-mode');
                btn.innerHTML = '👁️ View Mode';
                btn.style.backgroundColor = '#555';
                btn.style.color = 'white';
                document.querySelectorAll('.add-details').forEach(el => el.removeAttribute('open'));
                cancelEditTreasury();
            }
            
            // Aktiviert/Deaktiviert das Ziehen von Markern auf der Karte
            if (typeof map !== 'undefined') {
                map.eachLayer(layer => {
                    if (layer instanceof L.Marker) {
                        if (editMode) layer.dragging.enable();
                        else layer.dragging.disable();
                    }
                });
            }
        }

        function switchTab(tabId, btnElement) {
            // Wechselt zwischen den Tabs (Map, Characters, Spells etc.)
            document.querySelectorAll('.section').forEach(sec => sec.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            btnElement.classList.add('active');
            
            if(tabId === 'map-section') setTimeout(() => { map.invalidateSize(); }, 100);
            if(tabId === 'bastion-section' && bastionMap) setTimeout(() => { bastionMap.invalidateSize(); }, 100);
        }

        // ========== WELTKARTE (LEAFLET) ==========
        const map = L.map('map', { crs: L.CRS.Simple, minZoom: -2, maxZoom: 2 });
        const bounds = [[-1000, 0], [0, 800]]; 
        L.imageOverlay('https://media.wizards.com/2015/images/dnd/resources/Sword-Coast-Map_HighRes.jpg', bounds).addTo(map);
        map.fitBounds(bounds);

        const customIcon = L.icon({ /* Roter Marker */ });

        async function loadPins() {
            // Lädt alle Pins vom Backend und zeichnet sie auf die Karte
            const res = await fetch('/api/pins');
            const pins = await res.json();
            // ... Marker + Route-Linie zeichnen ...
        }

        map.on('contextmenu', function(e) {
            // Rechtsklick auf die Karte → Neuer Pin (nur im Edit Mode)
            if (!editMode) return;
            // ... Popup mit Formular öffnen ...
        });

        async function savePin(y, x) {
            // Speichert einen neuen Pin über das Backend
            const formData = new FormData();
            // ... Daten sammeln und POST an /api/pins ...
            await fetch('/api/pins', { method: 'POST', body: formData });
            map.closePopup(); 
            loadPins();
        }

        // ========== PROTOCOL / COUNCIL BUCH ==========
        function renderProtocolBook() {
            // Zeigt entweder das geschlossene Buch-Cover oder die geöffneten Protokolle an
            const gridEl = document.getElementById('protocols-grid');
            
            if(!isProtocolBookOpen) {
                // Geschlossenes Buch anzeigen
                gridEl.innerHTML = `...`;
                return;
            }
            // Geöffnetes Buch mit Inhalt rendern
        }

        // ========== BASTION TACTICAL MAPS ==========
        function openTacticalMap(id, imageUrl, name) {
            // Öffnet eine taktische Karte mit Token-System
            activeBastionId = id;
            // ... Leaflet-Karte initialisieren + Bild als Overlay ...
            loadBastionTokens();
        }

        async function saveBastionToken(y, x) {
            // Speichert ein Token (Enemy, Player, Trap etc.) auf der Bastion-Karte
            await fetch(`/api/bastion/${activeBastionId}/tokens`, { method: 'POST', body: formData });
            loadBastionTokens();
        }

        // ========== TREASURY (SCHATZKAMMER) ==========
        async function loadTreasury() {
            const res = await fetch('/api/treasury');
            const t = await res.json();
            // Werte in die Coin-Boxen schreiben
        }

        async function saveTreasury() {
            // Speichert die geänderten Münzwerte im Backend
            await fetch('/api/treasury', { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
        }

        // ========== GROSSE ENTITY-FUNKTION (Chars, NPCs, Dragons etc.) ==========
        async function loadEntities(type) {
            const res = await fetch('/api/' + type);
            const data = await res.json();
            
            if (type === 'protocols') {
                allProtocols = data;
                renderProtocolBook();
                return;
            }
            
            if (type === 'chars') {
                charactersData = data; 
                // Aktualisiert alle Character-Dropdowns (Spells, Quests, Loot)
            }

            const container = document.getElementById(type + '-grid');
            container.innerHTML = '';
            
            data.forEach(item => {
                // Riesiger Switch für die unterschiedlichen Karten-Typen
                if (type === 'chars') {
                    // Charakter-Karte mit <details> rendern
                } else if (type === 'dragons') {
                    // Drachen-Karte
                } else if (type === 'npcs') {
                    // NPC mit Reputation-Bar
                } 
                // ... weitere Typen ...
            });
        }

        // ========== SPELLBOOK LOGIK ==========
        async function loadSpells() {
            // Lädt Zauber eines Charakters und rendert entweder das geschlossene Buch oder die geöffneten Seiten
        }

        async function searchSpellAPI() {
            // Ruft die offizielle D&D 5e API auf und füllt das Formular automatisch aus
            const res = await fetch(`https://www.dnd5eapi.co/api/spells/${query}`);
            // ... Daten ins Formular schreiben ...
        }

        // ========== QUESTBOOK LOGIK ==========
        function renderQuestBook() {
            // Sehr komplexe Funktion: Zeigt Gruppen-Quests oder persönliche (passwortgeschützte) Quests an
            // Unterscheidet zwischen Admin und normalem User
        }

        async function submitSecretAuth() {
            // Prüft das Charakter-Passwort für persönliche Quests
            const res = await fetch('/api/verify_char_pwd', { method: 'POST', body: JSON.stringify(...) });
        }

        // ========== INITIALISIERUNG ==========
        checkAuth();
        loadPins();
        loadEntities('chars');
        loadEntities('npcs');
        // ... alle anderen loadEntities + loadQuests + loadTreasury ...
    </script>
</body>
</html>



Bereich,Was es macht,Kommentar-Stil
Navigation + Tabs,"Wechselt zwischen Karten, Charakteren, Spellbook etc.",Sehr gut strukturiert
Leaflet Map,"Interaktive Weltkarte mit Pins, Routen und Rechtsklick zum Hinzufügen","loadPins(), Drag & Drop"
loadEntities(),Die große zentrale Funktion – rendert fast alle Karten dynamisch,Sehr mächtig
Spellbook,Schönes animiertes Buch mit API-Import von dnd5eapi.co,toggleSpellbook()
Questbook,Gruppen- vs. persönliche Quests + Passwort-Schutz,Sehr komplex
Bastion Tactical Map,Separate Leaflet-Karte mit Tokens (Enemy/Player/Trap),openTacticalMap()
Treasury,Münzverwaltung mit Edit-Modus,Sehr clean
Edit Mode,Zeigt/versteckt alle Bearbeiten-Buttons global,toggleEditMode()


































