import json
import os
import sys
import urllib.request
import urllib.error
import hashlib
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 3000
DATA_FILE = "app_data.json"

# Compact seed data to keep the script light and high-density
DEFAULT_ROUTINE = {
    "objective": "Rendimiento y Enduro Profesional",
    "level": "Avanzado",
    "days": [
        {
            "id": "day-0",
            "label": "Lun",
            "name": "Lunes",
            "title": "Fuerza tren superior",
            "focus": "Tracción + empuje + grip",
            "warmup": "5 min: band pull-apart, rotación torácica, dead hang 3x10s",
            "cool": "Estiramiento pecho y hombro: 5 min",
            "completed": False,
            "trainingTime": "08:00",
            "exercises": [
                { "id": "ex-0-1", "name": "Dominadas neutras", "sets": "5 x máx", "detail": "Pausa 1s arriba. Baja lento.", "why": "Fuerza de tracción = control del manillar", "completed": False },
                { "id": "ex-0-2", "name": "Remo Pendlay", "sets": "4 x 8", "detail": "Barra al ombligo, explota al subir.", "why": "Postura de ataque: dorsal + romboides", "completed": False },
                { "id": "ex-0-3", "name": "Farmer carry pesado", "sets": "5 x 40m", "detail": "Paso firme sin balanceo.", "why": "Grip y resistencia para enduro largo", "completed": False }
            ]
        },
        {
            "id": "day-1",
            "label": "Mar",
            "name": "Martes",
            "title": "Core antirotacional",
            "focus": "Estabilidad con TRX y Pesos libres",
            "warmup": "5 min: cat-cow, glute bridge, plancha frontal",
            "cool": "Pigeon stretch 2 min por lado",
            "completed": False,
            "trainingTime": "18:00",
            "exercises": [
                { "id": "ex-1-1", "name": "Kettlebell drag en plancha", "sets": "4 x 8/lado", "detail": "Plancha estricta sin girar cadera.", "why": "Core antirotacional extremo para dominar inercias", "completed": False },
                { "id": "ex-1-2", "name": "Sierra en TRX", "sets": "4 x 12", "detail": "Posición de plancha. Empuja cuerpo atrás.", "why": "Evita extensión lumbar en saltos de moto", "completed": False }
            ]
        },
        {
            "id": "day-2",
            "label": "Mié",
            "name": "Miércoles",
            "title": "Potencia piernas",
            "focus": "Fuerza unilateral explosiva",
            "warmup": "Sentadilla goblet, saltos suaves",
            "cool": "Piramidal, cuádriceps en pie",
            "completed": False,
            "trainingTime": "08:15",
            "exercises": [
                { "id": "ex-2-1", "name": "Sentadilla búlgara", "sets": "5 x 8/lado", "detail": "Baja en 3 segundos controlados.", "why": "Posición de pie asimétrica en las estriberas", "completed": False },
                { "id": "ex-2-2", "name": "Hip thrust", "sets": "4 x 12", "detail": "Pausa de 2 segundos arriba apretando.", "why": "Motor principal al ir de pie sobre baches", "completed": False }
            ]
        },
        {
            "id": "day-3",
            "label": "Jue",
            "name": "Jueves",
            "title": "Descanso activo",
            "focus": "Recuperación de tejidos",
            "warmup": "",
            "cool": "",
            "completed": False,
            "trainingTime": "10:00",
            "exercises": [
                { "id": "ex-3-1", "name": "Foam roller completo", "sets": "12 min", "detail": "Cuádriceps, glúteos y dorsal.", "why": "Liberar tensión muscular acumulada", "completed": False },
                { "id": "ex-3-2", "name": "Box breathing", "sets": "5 min", "detail": "Inhala 4s, retén 4s, exhala 4s, retén 4s.", "why": "Recuperación del sistema nervioso central", "completed": False }
            ]
        },
        {
            "id": "day-4",
            "label": "Vie",
            "name": "Viernes",
            "title": "Core dinámico",
            "focus": "Superficies inestables",
            "warmup": "Movilidad torácica, rotación con palo",
            "cool": "Estiramiento flexor de cadera",
            "completed": False,
            "trainingTime": "17:30",
            "exercises": [
                { "id": "ex-4-1", "name": "Landmine press", "sets": "4 x 10/lado", "detail": "Empuje diagonal de pie a un brazo.", "why": "Estabilidad asimétrica en el manillar", "completed": False },
                { "id": "ex-4-2", "name": "Suitcase carry", "sets": "4 x 40m/lado", "detail": "Carga a un solo lado. Torso vertical.", "why": "Control de inercias laterales al tumbar", "completed": False }
            ]
        },
        {
            "id": "day-5",
            "label": "Sáb",
            "name": "Sábado",
            "title": "Práctica en Moto",
            "focus": "Técnica y resistencia específica",
            "warmup": "Movilidad general antes de casco (muñecas, cuello)",
            "cool": "Hidratación profunda, estiramiento antebrazos",
            "completed": False,
            "trainingTime": "09:30",
            "exercises": [
                { "id": "ex-5-1", "name": "Drills de equilibrio", "sets": "20 min", "detail": "Concentración en postura y control de embrague.", "why": "Base del control y balance a baja velocidad", "completed": False },
                { "id": "ex-5-2", "name": "Manga de resistencia", "sets": "40 min", "detail": "80% de pulsaciones fluidas.", "why": "Simula el esfuerzo continuo de carrera o ruta", "completed": False }
            ]
        },
        {
            "id": "day-6",
            "label": "Dom",
            "name": "Domingo",
            "title": "Recuperación activa",
            "focus": "Regeneración y movilidad",
            "warmup": "Paseo muy suave o caminata",
            "cool": "Preparación del equipo para la semana",
            "completed": False,
            "trainingTime": "10:30",
            "exercises": [
                { "id": "ex-6-1", "name": "Yoga para riders", "sets": "15 min", "detail": "Perro boca abajo, postura de niño.", "why": "Revierte postura encogida al ir en moto", "completed": False }
            ]
        }
    ]
}

DAYS_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
DEFAULT_MEALS = {}
for d in DAYS_NAMES:
    DEFAULT_MEALS[d] = {
        "desayuno": { "id": f"d-{d}", "name": "Avena caliente con frutos rojos y almendras", "calories": 350, "protein": 12, "carbs": 55, "fat": 8, "completed": False },
        "almuerzo": { "id": f"a-{d}", "name": "Pollo a la plancha con arroz integral y brócoli", "calories": 580, "protein": 42, "carbs": 45, "fat": 15, "completed": False },
        "merienda": { "id": f"m-{d}", "name": "Yogur griego con nueces y una manzana", "calories": 220, "protein": 18, "carbs": 15, "fat": 10, "completed": False },
        "cena": { "id": f"c-{d}", "name": "Salmón al horno con espárragos trileros", "calories": 450, "protein": 35, "carbs": 20, "fat": 12, "completed": False }
    }

DEFAULT_TRANSACTIONS = [
    { "id": "t-1", "title": "Sueldo Mensual Recibido", "amount": 1600.00, "type": "ingreso", "category": "Sueldo", "date": "2026-05-25" },
    { "id": "t-2", "title": "Compra de víveres saludables", "amount": 110.50, "type": "gasto", "category": "Comida", "date": "2026-05-26" },
    { "id": "t-3", "title": "Pago gimnasio mensual", "amount": 45.00, "type": "gasto", "category": "Gimnasio", "date": "2026-05-26" },
    { "id": "t-4", "title": "Cena saludable fuera", "amount": 35.00, "type": "gasto", "category": "Ocio", "date": "2026-05-27" }
]

DEFAULT_WATER_LOG = { d: 0 for d in DAYS_NAMES }

INITIAL_DATA = {
    "routine": DEFAULT_ROUTINE,
    "meals": DEFAULT_MEALS,
    "calorieTarget": 2100,
    "waterLog": DEFAULT_WATER_LOG,
    "transactions": DEFAULT_TRANSACTIONS
}

DEFAULT_USER = "admin"
DEFAULT_PASS_HASH = "vitalisesalt1234:ef09c87d33f145463c01676da372b245575f009594fc95164d60b0630452936b" # "vitalise1234"

def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16).hex()
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}:{hashed}"

def verify_password(stored_password_field, provided_password):
    try:
        salt, hashed = stored_password_field.split(":")
        check = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return check == hashed
    except Exception:
        return False

def generate_auth_token(username, password_hash):
    secret = "vitalise_cryptographic_secret_key_2026"
    return hashlib.sha256(f"{username}:{password_hash}:{secret}".encode('utf-8')).hexdigest()

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    if not DATABASE_URL:
        return None
    try:
        import psycopg2
        url = DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(url)
    except Exception as e:
        print("Database connection error:", e)
        return None

def load_data():
    db_conn = get_db_connection()
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS vitalise_store (id VARCHAR(50) PRIMARY KEY, data JSONB);")
                db_conn.commit()
                cur.execute("SELECT data FROM vitalise_store WHERE id = 'global_state';")
                row = cur.fetchone()
                if row:
                    data = row[0]
                    dirty = False
                    if "security_username" not in data:
                        data["security_username"] = DEFAULT_USER
                        dirty = True
                    if "security_password_hash" not in data:
                        data["security_password_hash"] = DEFAULT_PASS_HASH
                        dirty = True
                    if "security_enabled" not in data:
                        data["security_enabled"] = data.get("pin_security_enabled", True)
                        dirty = True
                    if dirty:
                        cur.execute(
                            "INSERT INTO vitalise_store (id, data) VALUES ('global_state', %s) "
                            "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data;",
                            (json.dumps(data, ensure_ascii=False),)
                        )
                        db_conn.commit()
                    return data
        except Exception as e:
            print("Error loading from database, falling back to local file:", e)
        finally:
            db_conn.close()

    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                dirty = False
                if "security_username" not in data:
                    data["security_username"] = DEFAULT_USER
                    dirty = True
                if "security_password_hash" not in data:
                    data["security_password_hash"] = DEFAULT_PASS_HASH
                    dirty = True
                if "security_enabled" not in data:
                    data["security_enabled"] = data.get("pin_security_enabled", True)
                    dirty = True
                if dirty:
                    save_data(data)
                return data
        except Exception:
            pass
    init_data = INITIAL_DATA.copy()
    init_data["security_username"] = DEFAULT_USER
    init_data["security_password_hash"] = DEFAULT_PASS_HASH
    init_data["security_enabled"] = True
    save_data(init_data)
    return init_data

def save_data(data):
    db_conn = get_db_connection()
    if db_conn:
        try:
            with db_conn.cursor() as cur:
                cur.execute("CREATE TABLE IF NOT EXISTS vitalise_store (id VARCHAR(50) PRIMARY KEY, data JSONB);")
                cur.execute(
                    "INSERT INTO vitalise_store (id, data) VALUES ('global_state', %s) "
                    "ON CONFLICT (id) DO UPDATE SET data = EXCLUDED.data;",
                    (json.dumps(data, ensure_ascii=False),)
                )
                db_conn.commit()
        except Exception as e:
            print("Error saving to database:", e)
        finally:
            db_conn.close()

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving to local backup file:", e)

def call_gemini_api(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=12) as res:
            res_json = json.loads(res.read().decode("utf-8"))
            text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Extracción robusta de JSON de la respuesta de Gemini
            if "```" in text:
                parts = text.split("```")
                for part in parts:
                    part_clean = part.strip()
                    if part_clean.startswith("json"):
                        part_clean = part_clean[4:].strip()
                    if part_clean.startswith("{") and part_clean.endswith("}"):
                        try:
                            return json.loads(part_clean)
                        except Exception:
                            pass
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                try:
                    return json.loads(text[start:end+1])
                except Exception:
                    pass
            return json.loads(text)
    except Exception as e:
        print("Gemini API Error:", e)
        return None

# Combined single script HTML page
HTML_CONTENT = """<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-950">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vitalise - Manejo de Entrenamiento, Dieta y Finanzas</title>
    <link rel="icon" type="image/png" href="/assets/logo.png">
    <link rel="manifest" href="/manifest.json">
    
    <!-- Apple Web App Standalone Meta Tags (PWA for iOS) -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Vitalise">
    <link rel="apple-touch-icon" href="/assets/logo.png">

    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        slate: {
                            50: 'var(--color-slate-50)',
                            100: 'var(--color-slate-100)',
                            200: 'var(--color-slate-200)',
                            300: 'var(--color-slate-300)',
                            350: 'var(--color-slate-350)',
                            400: 'var(--color-slate-400)',
                            450: 'var(--color-slate-450)',
                            500: 'var(--color-slate-500)',
                            700: 'var(--color-slate-700)',
                            750: 'var(--color-slate-750)',
                            800: 'var(--color-slate-800)',
                            850: 'var(--color-slate-850)',
                            900: 'var(--color-slate-900)',
                            950: 'var(--color-slate-950)',
                        },
                        brand: {
                            DEFAULT: 'var(--color-brand)',
                            hover: 'var(--color-brand-hover)'
                        }
                    }
                }
            }
        }
    </script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            /* Default dark theme variables */
            --color-slate-50: #f8fafc;
            --color-slate-100: #f1f5f9;
            --color-slate-200: #e2e8f0;
            --color-slate-300: #cbd5e1;
            --color-slate-350: #cbd5e1;
            --color-slate-400: #94a3b8;
            --color-slate-450: #94a3b8;
            --color-slate-500: #64748b;
            --color-slate-700: #334155;
            --color-slate-750: #1e293b;
            --color-slate-800: #1e293b;
            --color-slate-850: #1e293b;
            --color-slate-900: #0f172a;
            --color-slate-950: #090d16;
            --color-brand: #185FA5;
            --color-brand-hover: #1e70c0;
        }

        body.theme-sepia {
            /* Warm sepia theme variables */
            --color-slate-50: #ffffff;
            --color-slate-100: #433422;
            --color-slate-200: #433422;
            --color-slate-300: #433422;
            --color-slate-350: #5c4c3b;
            --color-slate-400: #705f4c;
            --color-slate-450: #786551;
            --color-slate-500: #8a755d;
            --color-slate-700: #ebdcb9;
            --color-slate-750: #ebdcb9;
            --color-slate-800: #e4d5be;
            --color-slate-850: #ebdcb9;
            --color-slate-900: #fbf6eb;
            --color-slate-950: #f5ebd5;
            --color-brand: #b24a2c; /* warm terracotta orange */
            --color-brand-hover: #c95c3e;
        }

        body.theme-light {
            /* Soft light theme variables */
            --color-slate-50: #0f172a;
            --color-slate-100: #0f172a;
            --color-slate-200: #1e293b;
            --color-slate-300: #1e293b;
            --color-slate-350: #334155;
            --color-slate-400: #475569;
            --color-slate-450: #475569;
            --color-slate-500: #64748b;
            --color-slate-700: #cbd5e1;
            --color-slate-750: #e2e8f0;
            --color-slate-800: #cbd5e1;
            --color-slate-850: #e2e8f0;
            --color-slate-900: #ffffff;
            --color-slate-950: #f1f5f9;
            --color-brand: #185FA5;
            --color-brand-hover: #1b6cb8;
        }

        /* High contrast overrides for sepia and light themes (eye comfort) */
        body.theme-sepia h1,
        body.theme-sepia h2,
        body.theme-sepia h3,
        body.theme-sepia h4,
        body.theme-sepia .text-white:not(button):not(a):not([class*="bg-"]):not([class*="active"]) {
            color: #2c1e11 !important;
        }

        body.theme-light h1,
        body.theme-light h2,
        body.theme-light h3,
        body.theme-light h4,
        body.theme-light .text-white:not(button):not(a):not([class*="bg-"]):not([class*="active"]) {
            color: #0f172a !important;
        }

        /* Ensure text-white stays white inside colored backgrounds/buttons/links in sepia and light themes */
        body.theme-sepia button .text-white,
        body.theme-sepia a .text-white,
        body.theme-sepia [class*="bg-"] .text-white,
        body.theme-sepia [class*="bg-"] h1,
        body.theme-sepia [class*="bg-"] h2,
        body.theme-sepia [class*="bg-"] h3,
        body.theme-sepia [class*="bg-"] h4 {
            color: #ffffff !important;
        }

        body.theme-light button .text-white,
        body.theme-light a .text-white,
        body.theme-light [class*="bg-"] .text-white,
        body.theme-light [class*="bg-"] h1,
        body.theme-light [class*="bg-"] h2,
        body.theme-light [class*="bg-"] h3,
        body.theme-light [class*="bg-"] h4 {
            color: #ffffff !important;
        }

        /* Placeholders & Inputs contrast guarantees */
        body.theme-sepia ::placeholder {
            color: #8a755d !important;
            opacity: 0.8;
        }
        body.theme-light ::placeholder {
            color: #64748b !important;
            opacity: 0.8;
        }

        /* For transparent inputs/textareas to inherit proper colors */
        input.bg-transparent, textarea.bg-transparent {
            color: inherit !important;
        }

        /* Guarantee inputs/selects on light/sepia have rich dark colors and borders */
        body.theme-sepia input:not(.bg-transparent), 
        body.theme-sepia textarea:not(.bg-transparent), 
        body.theme-sepia select,
        body.theme-sepia option {
            color: #2c1e11 !important;
            background-color: #f5ebd5 !important;
            border-color: #e4d5be !important;
        }

        body.theme-light input:not(.bg-transparent), 
        body.theme-light textarea:not(.bg-transparent), 
        body.theme-light select,
        body.theme-light option {
            color: #0f172a !important;
            background-color: #f1f5f9 !important;
            border-color: #cbd5e1 !important;
        }

        /* Fix fire alarm overlay text contrast (always light text as it has a dark bg) */
        #alarm-fire-overlay h1,
        #alarm-fire-overlay h2,
        #alarm-fire-overlay h3,
        #alarm-fire-overlay h4,
        #alarm-fire-overlay p,
        #alarm-fire-overlay span {
            color: #ffffff !important;
        }
        #alarm-fire-overlay p#alarm-wo-focus {
            color: #94a3b8 !important;
        }

        /* Direct utility overrides for brand color hexes used in existing DOM */
        .text-\[\#185FA5\] { color: var(--color-brand) !important; }
        .bg-\[\#185FA5\] { background-color: var(--color-brand) !important; }
        .border-\[\#185FA5\] { border-color: var(--color-brand) !important; }
        .focus\:border-\[\#185FA5\]:focus { border-color: var(--color-brand) !important; }
        .focus\:ring-\[\#185FA5\]:focus { --tw-ring-color: var(--color-brand) !important; }
        .selection\:bg-\[\#185FA5\]::selection { background-color: var(--color-brand) !important; }

        body { font-family: 'Inter', sans-serif; }
        .font-display { font-family: 'Space Grotesk', sans-serif; }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-6px); }
            75% { transform: translateX(6px); }
        }
        .animate-shake {
            animation: shake 0.15s ease-in-out 0s 2;
        }
    </style>
</head>
<body class="h-full bg-slate-950 text-slate-100 flex flex-col overflow-x-hidden antialiased selection:bg-brand selection:text-white">

    <!-- Lock Screen Container -->
    <div id="lock-screen-container" class="fixed inset-0 bg-slate-950/98 backdrop-blur-md z-50 flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 max-w-sm w-full rounded-2xl p-6 md:p-8 shadow-2xl text-center space-y-6 relative overflow-hidden">
            <div class="absolute -top-10 -right-10 w-32 h-32 bg-blue-500/10 rounded-full blur-2xl"></div>
            <div class="absolute -bottom-10 -left-10 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
            
            <img src="/assets/logo.png" class="w-20 h-20 object-contain mx-auto rounded-xl shadow-lg border border-slate-800 bg-white p-1" alt="Vitalise Logo" />
            
            <div class="space-y-2">
                <h2 class="text-xl font-black text-white font-display uppercase tracking-wider">Vitalise</h2>
                <p class="text-xs text-slate-400 max-w-xs mx-auto">Tus rutinas de alto rendimiento, alimentación y registros financieros se encuentran resguardados de forma segura.</p>
            </div>
            
            <div class="space-y-3 text-left">
                <div class="space-y-1">
                    <label class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Nickname / Usuario</label>
                    <input type="text" id="input-lock-user" class="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl focus:ring-2 focus:ring-[#185FA5] focus:outline-none focus:border-transparent text-white text-xs placeholder-slate-700 transition" placeholder="Ingresa tu nickname" onkeydown="if(event.key === 'Enter') attemptUnlock()" />
                </div>
                <div class="space-y-1">
                    <label class="text-[10px] font-bold uppercase tracking-wider text-slate-400">Contraseña</label>
                    <input type="password" id="input-lock-pass" class="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl focus:ring-2 focus:ring-[#185FA5] focus:outline-none focus:border-transparent text-white text-xs placeholder-slate-700 transition" placeholder="••••••••" onkeydown="if(event.key === 'Enter') attemptUnlock()" />
                </div>
                <p id="lock-error-msg" class="text-[11px] font-bold text-rose-500 hidden text-center animate-bounce">⚠️ Usuario o contraseña incorrectos</p>
                <button onclick="attemptUnlock()" id="btn-unlock-submit" class="w-full py-3 bg-[#185FA5] hover:bg-blue-600 active:bg-blue-700 text-white font-bold rounded-xl text-xs shadow-lg transition flex items-center justify-center gap-1.5 uppercase tracking-wider font-display">
                    <i data-lucide="key-round" class="w-4 h-4"></i> Iniciar Sesión
                </button>
            </div>
            
            <div class="pt-2 text-[10px] text-slate-500 font-mono text-center">
                <span>Predeterminado: </span><span class="text-slate-400 font-bold">admin / vitalise1234</span>
            </div>
        </div>
    </div>

    <!-- App Content Wrapper -->
    <div id="app-wrapper" class="hidden h-full flex flex-col">

        <!-- App Header banner -->
    <header class="border-b border-slate-800 bg-slate-900/95 sticky top-0 z-40 backdrop-blur-md">
        <div class="max-w-7xl mx-auto px-4 py-4 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div class="flex items-center gap-3">
                <img src="/assets/logo.png" class="w-10 h-10 object-contain rounded-xl shadow-lg border border-slate-800 bg-white p-1" alt="Vitalise Logo" />
                <div>
                    <h1 class="text-base sm:text-lg font-black tracking-tight text-white font-display">Vitalise</h1>
                    <p class="text-[11px] font-bold text-slate-400 font-mono flex items-center gap-1 uppercase tracking-wider">
                        <span>MANEJO DE ENTRENAMIENTO, DIETA Y FINANZAS</span>
                        <span class="text-[#185FA5]">•</span>
                        <span class="text-[#185FA5]">SISTEMA DE ALARMAS INTEGRADO</span>
                    </p>
                </div>
            </div>

            <!-- Centralized Tab Selector & Security controls -->
            <div class="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
                <nav class="flex bg-slate-950 p-1 rounded-xl border border-slate-800/80 w-full sm:w-auto shrink-0">
                    <button onclick="switchTab('workouts')" id="tab-workouts" class="flex-1 sm:flex-initial px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all text-slate-400 hover:text-white">
                        <i data-lucide="dumbbell" class="w-3.5 h-3.5"></i> Entrenamiento
                    </button>
                    <button onclick="switchTab('meals')" id="tab-meals" class="flex-1 sm:flex-initial px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all text-slate-400 hover:text-white">
                        <i data-lucide="salad" class="w-3.5 h-3.5"></i> Dieta y Comidas
                    </button>
                    <button onclick="switchTab('finances')" id="tab-finances" class="flex-1 sm:flex-initial px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all text-slate-400 hover:text-white">
                        <i data-lucide="wallet" class="w-3.5 h-3.5"></i> Finanzas
                    </button>
                </nav>
                
                <div class="flex items-center gap-2 w-full sm:w-auto justify-end">
                    <!-- Segmented Theme Selector for Eye Comfort -->
                    <div class="flex bg-slate-950 p-1 rounded-lg border border-slate-850 items-center shrink-0">
                        <button onclick="setTheme('dark')" id="btn-theme-dark" title="Tema Oscuro Cósmico" class="p-1.5 rounded transition-all text-slate-400 hover:text-white">
                            <i data-lucide="moon" class="w-3.5 h-3.5"></i>
                        </button>
                        <button onclick="setTheme('sepia')" id="btn-theme-sepia" title="Tema Cálido Sepia" class="p-1.5 rounded transition-all text-slate-400 hover:text-white">
                            <i data-lucide="eye" class="w-3.5 h-3.5"></i>
                        </button>
                        <button onclick="setTheme('light')" id="btn-theme-light" title="Tema Claro Suave" class="p-1.5 rounded transition-all text-slate-400 hover:text-white">
                            <i data-lucide="sun" class="w-3.5 h-3.5"></i>
                        </button>
                    </div>

                    <button onclick="manualSaveState()" id="btn-header-save" title="Guardar Estado de la Aplicación" class="p-2 bg-slate-950 border border-slate-850 hover:bg-slate-900 text-slate-400 hover:text-emerald-400 rounded-lg transition-all flex items-center gap-1.5 text-xs font-medium">
                        <i data-lucide="save" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">Guardar Estado</span>
                    </button>

                    <button onclick="openSecurityModal()" id="btn-header-security" title="Configurar Seguridad" class="p-2 bg-slate-950 border border-slate-850 hover:bg-slate-900 text-slate-400 hover:text-blue-400 rounded-lg transition-all flex items-center gap-1.5 text-xs font-medium">
                        <i data-lucide="shield" class="w-3.5 h-3.5"></i> <span id="text-header-security">Seguridad</span>
                    </button>
                    <button onclick="logoutSecure()" id="btn-header-logout" title="Cerrar Sesión" class="p-2 bg-slate-950 border border-slate-850 hover:bg-slate-900 text-slate-400 hover:text-rose-400 rounded-lg transition-all flex items-center gap-1.5 text-xs font-medium hidden">
                        <i data-lucide="log-out" class="w-3.5 h-3.5"></i> <span class="hidden lg:inline">Cerrar Sesión</span>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- Widgets Bar (Clock & Weather) -->
    <div class="bg-slate-900/60 border-b border-slate-800/80 backdrop-blur-sm py-2 px-4 shadow-inner">
        <div class="max-w-7xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-2 text-xs">
            <!-- Clock section -->
            <div class="flex items-center gap-2 font-mono text-slate-350">
                <i data-lucide="clock" class="w-4 h-4 text-brand"></i>
                <span id="widget-date-time" class="font-semibold text-slate-200">Cargando fecha y hora...</span>
            </div>
            <!-- Weather section -->
            <div id="widget-weather" class="flex items-center gap-2 text-slate-350 transition-opacity duration-300">
                <i data-lucide="cloud-sun" class="w-4 h-4 text-amber-400 animate-pulse"></i>
                <span id="widget-weather-text" class="text-slate-200">Cargando clima de Concepción...</span>
            </div>
        </div>
    </div>

    <!-- Main Container -->
    <main class="flex-1 max-w-7xl mx-auto w-full px-4 py-6 md:py-8">

        <!-- 1. WORKOUT SECTION -->
        <div id="section-workouts" class="tab-content space-y-6 hidden">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Left panel: Day Selector + Active Day Details -->
                <div class="lg:col-span-8 space-y-5">
                    <!-- Week calendar days row -->
                    <div id="workouts-calendar" class="flex items-center gap-2 overflow-x-auto pb-1"></div>

                    <!-- Active Workout routine container -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 md:p-6 space-y-6">
                        <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 pb-4 border-b border-slate-800">
                            <div class="space-y-1.5 flex-1 w-full">
                                <div class="flex flex-wrap items-center gap-2">
                                    <span id="wo-focus" class="text-[10px] font-bold font-mono px-2 py-0.5 bg-slate-950 border border-slate-800 rounded text-slate-350"></span>
                                    <span class="flex items-center gap-1 text-[10px] font-bold font-mono px-2 py-0.5 bg-brand/10 text-brand border border-brand/20 rounded">
                                        <i data-lucide="clock" class="w-3 h-3"></i> Alarma: <span id="wo-time"></span>
                                    </span>
                                </div>
                                <input type="text" id="wo-title" onchange="updateDayTitle(this.value)" class="text-lg font-black text-slate-100 border-b border-transparent hover:border-slate-400 focus:border-brand focus:outline-none bg-transparent w-full pt-1" />
                            
                                <div class="flex items-center gap-2 pt-1.5">
                                    <label class="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5 bg-slate-950 px-2.5 py-1 rounded-lg border border-slate-800">
                                        <i data-lucide="alarm-clock" class="w-3.5 h-3.5 text-brand"></i>
                                        <span>Configurar Alarma:</span>
                                        <input type="time" id="input-alarm-time" onchange="updateAlarmTime(this.value)" class="bg-slate-950 text-slate-100 font-bold font-mono text-xs border border-slate-400 rounded px-1.5 py-0.5 focus:outline-none focus:ring-1 focus:ring-brand" />
                                    </label>
                                </div>
                            </div>
                        </div>

                        <!-- Warmup & Cooldown details -->
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="p-4 bg-slate-950 rounded-xl border border-slate-850 space-y-1">
                                <span class="text-[10px] font-bold text-[#185FA5] uppercase tracking-wider block">Calentamiento / Movilidad</span>
                                <textarea id="wo-warmup" onchange="updateWarmup(this.value)" class="text-xs text-slate-300 bg-transparent border-0 focus:ring-0 focus:outline-none w-full resize-none h-16 leading-relaxed" placeholder="Describir calentamiento..."></textarea>
                            </div>
                            <div class="p-4 bg-slate-950 rounded-xl border border-slate-850 space-y-1">
                                <span class="text-[10px] font-bold text-amber-500 uppercase tracking-wider block">Vuelta a la Calma / Estiramiento</span>
                                <textarea id="wo-cool" onchange="updateCool(this.value)" class="text-xs text-slate-300 bg-transparent border-0 focus:ring-0 focus:outline-none w-full resize-none h-16 leading-relaxed" placeholder="Describir estiramiento..."></textarea>
                            </div>
                        </div>

                        <!-- Exercises checklist -->
                        <div class="space-y-3">
                            <div class="flex justify-between items-center">
                                <h3 class="text-xs font-black uppercase tracking-wider text-slate-400">Lista de Ejercicios</h3>
                                <button onclick="addNewExercise()" class="text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1 px-2.5 py-1 bg-blue-950/40 rounded-lg border border-blue-900/50 transition">
                                    <i data-lucide="plus" class="w-3 h-3"></i> Añadir Ejercicio
                                </button>
                            </div>

                            <!-- Progress Bar for Workout Completion -->
                            <div class="bg-slate-950 rounded-xl p-3.5 border border-slate-850 space-y-2">
                                <div class="flex justify-between items-center text-[11px] font-bold uppercase tracking-wider">
                                    <span class="text-slate-400">Progreso de la rutina diaria</span>
                                    <span id="wo-progress-percent" class="text-brand font-mono text-xs">0%</span>
                                </div>
                                <div class="w-full h-2.5 bg-slate-900 border border-slate-800 rounded-full overflow-hidden p-[1px]">
                                    <div id="wo-progress-bar" class="h-full bg-brand rounded-full transition-all duration-500 ease-out" style="width: 0%"></div>
                                </div>
                            </div>

                            <div id="exercises-list" class="space-y-3"></div>
                        </div>
                    </div>
                </div>

                <!-- Right panel: Alarms Controller & Info -->
                <div class="lg:col-span-4 space-y-5">
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-2">
                                <div class="p-1.5 bg-slate-950 border border-slate-850 text-[#185FA5] rounded-lg">
                                    <i data-lucide="bell" class="w-4 h-4"></i>
                                </div>
                                <span class="text-xs font-black uppercase tracking-wider text-white">Notificaciones de Alarma</span>
                            </div>
                            
                            <!-- Switch -->
                            <button onclick="toggleNotificationsMaster()" id="btn-master-alarm" class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-slate-800">
                                <span id="toggle-circle" class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out translate-x-0"></span>
                            </button>
                        </div>

                        <div class="text-xs text-slate-400 space-y-2 leading-relaxed">
                            <p>Recibe alertas visuales y sonoras locales al cumplirse la hora programada para tus rutinas del día.</p>
                            <div id="notif-badge-state" class="p-2 bg-slate-950 border border-slate-800 rounded-lg font-bold text-[10px] uppercase tracking-wider text-center text-amber-500">
                                🔴 Alarmas Inactivas
                            </div>
                        </div>

                        <div class="pt-2 border-t border-slate-800 space-y-2">
                            <button onclick="testAlarmDemo()" id="btn-test-alarm" class="w-full py-2 bg-slate-800 hover:bg-slate-750 text-slate-100 rounded-lg text-xs font-bold transition flex items-center justify-center gap-1.5">
                                <i data-lucide="volume-2" class="w-3.5 h-3.5 text-blue-400"></i>
                                <span id="test-btn-text">Probar Alarma de Prueba 📣</span>
                            </button>
                            <p class="text-[9.5px] text-slate-400 text-center italic">Prueba la alarma interactiva con un temporizador rápido de 5 segundos.</p>
                        </div>
                    </div>

                    <!-- Dynamic Workout Progress Chart Card -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex items-center justify-between pb-2 border-b border-slate-800">
                            <h3 class="font-black text-white text-sm flex items-center gap-2 font-display">
                                <i data-lucide="trending-up" class="w-4 h-4 text-[#185FA5]"></i> Rendimiento Semanal
                            </h3>
                            <span class="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider">EJERCICIOS %</span>
                        </div>
                        <div class="relative w-full h-44 flex items-center justify-center" id="workout-chart-container">
                            <canvas id="workoutProgressChart" class="max-h-full"></canvas>
                        </div>
                        <div class="pt-1.5 border-t border-slate-800/80 text-[11px] text-slate-450 space-y-1.5 font-mono">
                            <div class="flex justify-between items-center">
                                <span>Ejercicios Hoy:</span>
                                <span id="txt-workout-today-status" class="font-bold text-slate-200">0/0</span>
                            </div>
                            <div class="flex justify-between items-center">
                                <span>Rendimiento Semanal:</span>
                                <span id="txt-workout-week-status" class="font-bold text-emerald-400">0%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <!-- 2. DIET & MEALS SECTION -->
        <div id="section-meals" class="tab-content space-y-6 hidden">
            <!-- Day select tabs -->
            <div id="meals-calendar-tabs" class="flex items-center gap-2 overflow-x-auto pb-1"></div>

            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Meals logs: 2 spans -->
                <div class="lg:col-span-2 space-y-4">
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 md:p-6 space-y-5">
                        <div class="flex justify-between items-center pb-3 border-b border-slate-800">
                            <h3 class="text-base font-black text-white font-display flex items-center gap-2">
                                <i data-lucide="salad" class="w-4 h-4 text-emerald-400"></i> Plan Alimenticio Diario
                            </h3>
                            <button onclick="resetDayMeals()" class="text-xs font-bold text-slate-400 hover:text-white flex items-center gap-1 px-2.5 py-1 bg-slate-950 border border-slate-850 rounded-lg transition">
                                <i data-lucide="rotate-ccw" class="w-3.5 h-3.5"></i> Reiniciar Día
                            </button>
                        </div>

                        <div id="meals-list" class="space-y-4"></div>
                    </div>

                    <!-- AI Meals Generator -->
                    <div class="bg-gradient-to-r from-emerald-950/40 to-blue-950/40 border border-emerald-900/40 rounded-xl p-5 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                        <div class="space-y-1">
                            <h4 class="text-xs font-black uppercase tracking-wider text-emerald-400 flex items-center gap-1">
                                <i data-lucide="sparkles" class="w-3.5 h-3.5"></i> Asistente de Nutrición Inteligente
                            </h4>
                            <p class="text-xs text-slate-300 leading-relaxed max-w-xl">
                                ¿Necesitas recetas fitness personalizadas? Genera una planificación completa de calorías y macronutrientes para deportistas.
                            </p>
                        </div>
                        <button onclick="openMealGenerator()" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold rounded-lg shadow transition shrink-0 flex items-center gap-1.5">
                            <i data-lucide="sparkles" class="w-4 h-4"></i> Generar Menú con IA
                        </button>
                    </div>
                </div>

                <!-- Hydration, goals & stats: 1 span -->
                <div class="space-y-6">
                    <!-- Target Tracker Widget -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black uppercase tracking-wider text-slate-350">Límite de Calorías Diario</span>
                            <div class="flex items-center gap-1.5">
                                <input type="number" id="input-calorie-target" onchange="updateCalorieTarget(this.value)" class="w-16 text-center font-mono font-bold bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-xs text-emerald-400" />
                                <span class="text-xs text-slate-400">kcal</span>
                            </div>
                        </div>

                        <!-- Progress indicators -->
                        <div class="space-y-3">
                            <div>
                                <div class="flex justify-between text-[11px] font-bold text-slate-400 mb-1">
                                    <span>Consumidas hoy</span>
                                    <span id="txt-calories-progress">0%</span>
                                </div>
                                <div class="w-full bg-slate-950 rounded-full h-2 border border-slate-850">
                                    <div id="bar-calories-progress" class="bg-emerald-500 h-2 rounded-full transition-all duration-300" style="width: 0%"></div>
                                </div>
                            </div>
                            <div class="grid grid-cols-3 gap-2 pt-2 text-center text-xs">
                                <div class="p-2 bg-slate-950 border border-slate-850 rounded-lg">
                                    <div class="text-[9px] uppercase font-bold text-red-400">Proteína</div>
                                    <div id="txt-macro-prot" class="font-mono font-black mt-0.5 text-white">0g</div>
                                </div>
                                <div class="p-2 bg-slate-950 border border-slate-850 rounded-lg">
                                    <div class="text-[9px] uppercase font-bold text-amber-400">Carbohidratos</div>
                                    <div id="txt-macro-carb" class="font-mono font-black mt-0.5 text-white">0g</div>
                                </div>
                                <div class="p-2 bg-slate-950 border border-slate-850 rounded-lg">
                                    <div class="text-[9px] uppercase font-bold text-blue-400">Grasas</div>
                                    <div id="txt-macro-fat" class="font-mono font-black mt-0.5 text-white">0g</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Water log Widget -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-black uppercase tracking-wider text-slate-350 flex items-center gap-1.5">
                                <i data-lucide="droplet" class="w-4 h-4 text-sky-400"></i> Registro de Hidratación
                            </span>
                            <span id="txt-water-count" class="font-mono text-xs font-black text-white">0 / 8 vasos</span>
                        </div>

                        <div class="flex flex-wrap gap-2 justify-center py-2" id="water-glasses-container"></div>

                        <div class="flex gap-2">
                            <button onclick="adjustWater(-1)" class="flex-1 py-1.5 bg-slate-950 hover:bg-slate-850 border border-slate-800 text-slate-300 font-bold rounded-lg text-xs transition">- 1 Vaso</button>
                            <button onclick="adjustWater(1)" class="flex-1 py-1.5 bg-sky-900/30 hover:bg-sky-900/50 border border-sky-800 text-sky-300 font-bold rounded-lg text-xs transition">+ 1 Vaso</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <!-- 3. FINANCES SECTION -->
        <div id="section-finances" class="tab-content space-y-6 hidden">
            <!-- Summary cards top panel -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                    <div class="p-3 bg-emerald-950/50 border border-emerald-900/50 rounded-xl text-emerald-400 shadow-inner">
                        <i data-lucide="trending-up" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span class="text-xs text-slate-400 font-bold block">Ingresos Totales</span>
                        <div id="txt-total-income" class="text-xl font-black font-mono text-emerald-400">$0.00</div>
                    </div>
                </div>
                <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-4">
                    <div class="p-3 bg-rose-950/50 border border-rose-900/50 rounded-xl text-rose-400 shadow-inner">
                        <i data-lucide="trending-down" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span class="text-xs text-slate-400 font-bold block">Gastos Totales</span>
                        <div id="txt-total-expenses" class="text-xl font-black font-mono text-rose-400">$0.00</div>
                    </div>
                </div>
                <div id="card-balance" class="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-4 transition-all">
                    <div id="icon-balance-bg" class="p-3 rounded-xl shadow-inner">
                        <i data-lucide="dollar-sign" class="w-6 h-6"></i>
                    </div>
                    <div>
                        <span class="text-xs text-slate-400 font-bold block">Balance Neto</span>
                        <div id="txt-net-balance" class="text-xl font-black font-mono">$0.00</div>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <!-- Left panel: Register movement & Analytics -->
                <div class="lg:col-span-7 space-y-6">
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <h3 class="font-black text-white text-sm flex items-center gap-2 font-display">
                            <i data-lucide="bookmark" class="w-4 h-4 text-[#185FA5]"></i> Registrar Movimiento Financiero
                        </h3>

                        <form onsubmit="saveNewTransaction(event)" class="grid grid-cols-1 sm:grid-cols-12 gap-3 text-xs">
                            <div class="sm:col-span-8 space-y-1">
                                <label class="text-[10px] uppercase font-bold text-slate-400">Concepto o Descripción *</label>
                                <input type="text" id="tx-title" required placeholder="Ej. Compra supermercado, Pago sueldo" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-lg focus:outline-none focus:border-slate-600" />
                            </div>
                            <div class="sm:col-span-4 space-y-1">
                                <label class="text-[10px] uppercase font-bold text-slate-400">Monto ($) *</label>
                                <input type="number" step="0.01" min="0.01" id="tx-amount" required placeholder="0.00" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white font-mono rounded-lg focus:outline-none focus:border-slate-600" />
                            </div>

                            <div class="sm:col-span-4 space-y-1">
                                <label class="text-[10px] uppercase font-bold text-slate-400">Tipo de Flujo</label>
                                <div class="flex bg-slate-950 p-1 rounded-lg border border-slate-800">
                                    <button type="button" onclick="setTxFormType('gasto')" id="btn-tx-gasto" class="flex-1 py-1.5 rounded-md font-bold text-center text-rose-500 bg-slate-900 shadow">Gasto</button>
                                    <button type="button" onclick="setTxFormType('ingreso')" id="btn-tx-ingreso" class="flex-1 py-1.5 rounded-md font-bold text-center text-slate-400 hover:text-white">Ingreso</button>
                                </div>
                            </div>
                            <div class="sm:col-span-4 space-y-1">
                                <label class="text-[10px] uppercase font-bold text-slate-400">Categoría</label>
                                <select id="tx-category" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-lg focus:outline-none focus:border-slate-600">
                                    <option value="Comida">Comida</option>
                                    <option value="Gimnasio">Gimnasio</option>
                                    <option value="Alquiler">Alquiler</option>
                                    <option value="Sueldo">Sueldo</option>
                                    <option value="Ocio">Ocio</option>
                                    <option value="Varios">Varios</option>
                                </select>
                            </div>
                            <div class="sm:col-span-4 space-y-1">
                                <label class="text-[10px] uppercase font-bold text-slate-400">Fecha</label>
                                <input type="date" id="tx-date" required class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-white rounded-lg focus:outline-none focus:border-slate-600" />
                            </div>

                            <div class="sm:col-span-12 pt-1">
                                <button type="submit" class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg transition text-xs flex items-center justify-center gap-1">
                                    <i data-lucide="plus" class="w-4 h-4"></i> Guardar Movimiento
                                </button>
                            </div>
                        </form>
                    </div>

                    <!-- Interactive charts with dynamic sub-tabs -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
                            <div class="flex bg-slate-950 p-1 rounded-xl border border-slate-850">
                                <button onclick="setFinanceChartTab('expenses')" id="btn-fin-tab-expenses" class="px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all bg-slate-900 text-white shadow flex items-center gap-1.5">
                                    <i data-lucide="pie-chart" class="w-3.5 h-3.5 text-indigo-400"></i> Desglose de Gastos
                                </button>
                                <button onclick="setFinanceChartTab('summary')" id="btn-fin-tab-summary" class="px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5">
                                    <i data-lucide="bar-chart-3" class="w-3.5 h-3.5"></i> Balance Mensual
                                </button>
                            </div>
                            
                            <div id="expenses-chart-controls" class="flex gap-1.5 bg-slate-950 p-0.5 rounded-lg border border-slate-850">
                                <button onclick="setChartType('pie')" id="btn-chart-pie" class="px-2.5 py-1 text-[10px] font-bold rounded bg-slate-900 text-white shadow">Pie</button>
                                <button onclick="setChartType('bar')" id="btn-chart-bar" class="px-2.5 py-1 text-[10px] font-bold rounded text-slate-400 hover:text-slate-200">Barras</button>
                            </div>
                        </div>
                        <div class="relative w-full h-64 flex items-center justify-center" id="chart-container">
                            <canvas id="financeChart" class="max-h-full"></canvas>
                        </div>
                    </div>
                </div>

                <!-- Right panel: Ledger list & AI advisor -->
                <div class="lg:col-span-5 space-y-6">
                    <!-- AI finance advisor -->
                    <div class="bg-gradient-to-br from-indigo-950/40 to-slate-900/80 border border-indigo-900/40 rounded-xl p-5 space-y-4">
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-black uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                                <i data-lucide="sparkles" class="w-4 h-4"></i> Asesor Financiero IA
                            </span>
                            <button onclick="runFinancialAnalysis()" class="px-3 py-1 bg-indigo-600 hover:bg-indigo-500 text-white text-[10px] font-bold rounded shadow transition flex items-center gap-1">
                                <i data-lucide="refresh-cw" class="w-3 h-3"></i> Analizar
                            </button>
                        </div>

                        <div id="finance-ai-card-content" class="text-xs space-y-3">
                            <p class="text-slate-400 italic">Haz clic en el botón superior para realizar un análisis estratégico inteligente de tus movimientos por la IA.</p>
                        </div>
                    </div>

                    <!-- Meta de Ahorro (Savings Goal) Widget -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex justify-between items-center">
                            <span class="text-xs font-black uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                                <i data-lucide="target" class="w-4 h-4 text-emerald-400"></i> Meta de Ahorro Mensual
                            </span>
                            <div class="flex items-center gap-2">
                                <button onclick="toggleEditSavingsGoal()" id="btn-edit-savings-goal" class="text-slate-400 hover:text-white p-1 transition">
                                    <i data-lucide="edit-3" class="w-3.5 h-3.5"></i>
                                </button>
                            </div>
                        </div>

                        <!-- Progress Section -->
                        <div class="space-y-3">
                            <div class="flex justify-between items-end">
                                <div>
                                    <span class="text-[10px] uppercase font-bold text-slate-400 block">Acumulado Neto</span>
                                    <span id="savings-current-amount" class="text-lg font-mono font-black text-white">$0.00</span>
                                </div>
                                <div class="text-right">
                                    <span class="text-[10px] uppercase font-bold text-slate-400 block">Meta</span>
                                    <!-- Display Mode -->
                                    <span id="savings-goal-display" class="text-sm font-mono font-black text-emerald-400">$1,000.00</span>
                                    <!-- Edit Mode -->
                                    <div id="savings-goal-edit-container" class="hidden flex items-center gap-1 mt-1">
                                        <span class="text-xs text-slate-400 font-mono">$</span>
                                        <input type="number" id="input-savings-goal" class="w-20 px-1.5 py-0.5 bg-slate-950 border border-slate-750 text-slate-100 rounded text-xs font-mono font-bold focus:outline-none focus:border-emerald-500" />
                                        <button onclick="saveSavingsGoal()" class="p-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded text-[10px] transition font-bold">✓</button>
                                    </div>
                                </div>
                            </div>

                            <!-- Progress Bar Container -->
                            <div class="space-y-1.5">
                                <div class="w-full h-3 bg-slate-950 border border-slate-850 rounded-full overflow-hidden p-[2px]">
                                    <div id="savings-progress-bar" class="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-1000 ease-out" style="width: 0%"></div>
                                </div>
                                <div class="flex justify-between items-center text-[10px] font-bold">
                                    <span id="savings-progress-status" class="text-slate-400">Progreso hacia tu meta</span>
                                    <span id="savings-progress-percent" class="font-mono text-emerald-400">0%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Ledger list -->
                    <div class="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
                        <div class="flex flex-col gap-2 pb-2 border-b border-slate-800">
                            <span class="text-xs font-black uppercase tracking-wider text-slate-350">Historial de Transacciones</span>
                            <input type="text" id="tx-search" oninput="renderTransactions()" placeholder="Buscar descripción..." class="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-850 rounded text-xs text-white focus:outline-none" />
                        </div>
                        <div id="tx-ledger-list" class="space-y-2.5 max-h-[300px] overflow-y-auto pr-1"></div>
                    </div>
                </div>
            </div>
        </div>

    </main>

    <!-- Clean Bottom Footer -->
    <footer class="py-6 border-t border-slate-800 bg-slate-950 text-center text-[11px] text-slate-500 font-medium">
        <div class="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>Vitalise &copy; 2026. Todos los derechos reservados.</span>
            <span class="flex items-center gap-1">
                <i data-lucide="shield-check" class="w-3.5 h-3.5 text-emerald-500"></i> Servidor Seguro y Encriptado
            </span>
        </div>
    </footer>

    </div> <!-- Close #app-wrapper -->


    <!-- MODALS & OVERLAYS -->

    <!-- In-App Alarms Alarm Popup Alert Overlay -->
    <div id="alarm-fire-overlay" class="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-[100] flex items-center justify-center p-4 hidden">
        <div class="bg-gradient-to-b from-slate-900 to-zinc-950 border border-slate-750 max-w-sm w-full rounded-2xl shadow-2xl p-6 text-center space-y-4 scale-95 transition-all">
            <div class="w-16 h-16 bg-blue-500/10 border border-blue-500/30 text-blue-400 rounded-full flex items-center justify-center mx-auto animate-pulse">
                <i data-lucide="alarm-clock" class="w-8 h-8 animate-bounce"></i>
            </div>
            <div class="space-y-1">
                <h4 class="text-[10px] font-bold uppercase tracking-widest text-blue-400">¡Alerta de Alarma Fired!</h4>
                <h3 class="text-lg font-black text-white font-display" id="alarm-wo-day">Lunes de Entrenamiento</h3>
                <p class="text-sm font-bold text-slate-200" id="alarm-wo-title">Fuerza tren superior</p>
                <p class="text-xs text-slate-400" id="alarm-wo-focus">Enfoque: Tracción + empuje + grip</p>
            </div>
            <div class="pt-2">
                <button onclick="dismissAlarmOverlay()" class="w-full py-2 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-lg text-xs shadow-lg transition">
                    ¡Entendido, Empezar Entreno! 🔥
                </button>
            </div>
        </div>
    </div>

    <!-- AI Meals Generator Dialog Modal -->
    <div id="ai-meals-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-2xl shadow-2xl p-5 md:p-6 space-y-4">
            <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                <h3 class="text-sm font-black text-white uppercase tracking-wider flex items-center gap-1.5 font-display">
                    <i data-lucide="sparkles" class="w-4 h-4 text-emerald-400 animate-spin"></i> Parámetros de Dieta IA
                </h3>
                <button onclick="closeMealGenerator()" class="text-slate-400 hover:text-white font-bold text-xs">✕</button>
            </div>
            <div class="space-y-3 text-xs">
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-400 uppercase">Preferencia de Dieta</label>
                    <select id="diet-preference" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg">
                        <option value="Omnívoro">Omnívoro (Todo tipo de alimentos)</option>
                        <option value="Keto">Keto / Cetogénico</option>
                        <option value="Vegetariano">Vegetariano</option>
                        <option value="Vegano">Vegano</option>
                        <option value="Alto en Proteínas">Alto en Proteínas (Riders)</option>
                    </select>
                </div>
                <div class="space-y-1">
                    <label class="text-[10px] font-bold text-slate-400 uppercase">Objetivo Físico</label>
                    <select id="diet-goal" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg">
                        <option value="Mantener peso saludable">Mantener peso saludable</option>
                        <option value="Ganar masa muscular">Ganar masa muscular y resistencia</option>
                        <option value="Perder grasa corporal">Definición / Perder grasa</option>
                    </select>
                </div>
            </div>
            <div id="ai-meals-err" class="p-2.5 bg-red-950/40 text-red-400 rounded-lg text-xs border border-red-900/50 hidden"></div>
            <div class="pt-2 flex gap-2">
                <button onclick="closeMealGenerator()" class="flex-1 py-2 bg-slate-950 border border-slate-800 hover:bg-slate-850 text-slate-300 rounded-lg font-bold text-xs transition">Cancelar</button>
                <button onclick="triggerAIPlanGeneration()" id="btn-ai-meals-submit" class="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold text-xs shadow-lg transition flex items-center justify-center gap-1.5">
                    <i data-lucide="sparkles" class="w-4.5 h-4.5"></i> Generar Menú
                </button>
            </div>
        </div>
    </div>

    <!-- Security Settings Modal -->
    <div id="security-settings-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-sm z-50 flex items-center justify-center p-4 hidden">
        <div class="bg-slate-900 border border-slate-800 max-w-sm w-full rounded-2xl shadow-2xl p-5 md:p-6 space-y-4">
            <div class="flex justify-between items-center pb-2 border-b border-slate-800">
                <h3 class="text-sm font-black text-white uppercase tracking-wider flex items-center gap-1.5 font-display">
                    <i data-lucide="shield" class="w-4 h-4 text-blue-500"></i> Ajustes de Seguridad
                </h3>
                <button onclick="closeSecurityModal()" class="text-slate-400 hover:text-white font-bold text-xs">✕</button>
            </div>
            
            <!-- Status indicator -->
            <div id="sec-status-container" class="flex items-center justify-between p-3 bg-slate-950 rounded-xl border border-slate-850">
                <span class="text-xs text-slate-400 font-medium">Seguridad de Acceso:</span>
                <span id="sec-status-badge" class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider"></span>
            </div>

            <!-- Inactive security view -->
            <div id="sec-inactive-view" class="space-y-3.5 hidden">
                <p class="text-[11px] text-slate-400">El acceso es libre. Activa credenciales de usuario para proteger tus entrenamientos, dieta y finanzas.</p>
                <div class="space-y-2 text-xs text-left">
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase">Nickname / Usuario</label>
                        <input type="text" id="input-sec-new-user" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Ej: admin" />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase">Definir Contraseña (mínimo 8 caracteres)</label>
                        <input type="password" id="input-sec-new-pass" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="••••••••" />
                    </div>
                </div>
                <button onclick="triggerEnableSecurity()" id="btn-sec-enable" class="w-full py-2.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold text-xs shadow-lg transition flex items-center justify-center gap-1.5">
                    <i data-lucide="shield-alert" class="w-4 h-4"></i> Activar Seguridad
                </button>
            </div>

            <!-- Active security view -->
            <div id="sec-active-view" class="space-y-3.5 hidden">
                <div class="space-y-2 text-xs text-left">
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase">Contraseña Actual</label>
                        <input type="password" id="input-sec-old-pass" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-rose-500" placeholder="••••••••" />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase">Nuevo Nickname / Usuario (Opcional)</label>
                        <input type="text" id="input-sec-change-user" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="Nuevo usuario" />
                    </div>
                    <div class="space-y-1">
                        <label class="text-[10px] font-bold text-slate-400 uppercase">Nueva Contraseña (Opcional, mínimo 8 caracteres)</label>
                        <input type="password" id="input-sec-change-pass" class="w-full px-3 py-2 bg-slate-950 border border-slate-800 text-slate-200 rounded-lg focus:outline-none focus:ring-1 focus:ring-blue-500" placeholder="••••••••" />
                    </div>
                </div>
                
                <div class="flex gap-2 pt-1">
                    <button onclick="triggerDisableSecurity()" id="btn-sec-disable" class="flex-1 py-2 bg-rose-950/40 hover:bg-rose-900/50 border border-rose-900 text-rose-300 rounded-lg font-bold text-xs transition flex items-center justify-center gap-1">
                        <i data-lucide="shield-off" class="w-3.5 h-3.5"></i> Desactivar
                    </button>
                    <button onclick="triggerChangeCredentials()" id="btn-sec-change" class="flex-1 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold text-xs shadow-lg transition flex items-center justify-center gap-1">
                        <i data-lucide="key-round" class="w-3.5 h-3.5"></i> Guardar Cambios
                    </button>
                </div>
            </div>

            <div id="sec-err" class="p-2.5 bg-red-950/40 text-red-400 rounded-lg text-xs border border-red-900/50 hidden"></div>
        </div>
    </div>


    <!-- APP CORE LOGIC SCRIPT (Vivid and Interactive) -->
    <script>
        const DAYS_NAMES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"];
        let state = {
            routine: {},
            meals: {},
            calorieTarget: 2100,
            waterLog: {},
            transactions: []
        };

        let currentTab = 'workouts';
        let currentWorkoutDayIdx = 0;
        let currentMealsDay = 'Lunes';
        let isNotificationsEnabled = false;
        let chartInstance = null;
        let chartType = 'pie';
        let workoutChartInstance = null;
        let activeFinanceChartTab = 'expenses';
        let testTimer = null;
        let lastAlarmFiredKey = '';
        let txFormType = 'gasto';

        function setTheme(themeName) {
            // Remove all theme classes from body
            document.body.classList.remove('theme-dark', 'theme-sepia', 'theme-light');
            
            // Add selected theme class
            if (themeName === 'sepia') {
                document.body.classList.add('theme-sepia');
            } else if (themeName === 'light') {
                document.body.classList.add('theme-light');
            } else {
                document.body.classList.add('theme-dark');
            }
            
            // Save to localStorage
            localStorage.setItem('app_theme', themeName);
            
            // Update segmented control buttons UI
            const btnDark = document.getElementById('btn-theme-dark');
            const btnSepia = document.getElementById('btn-theme-sepia');
            const btnLight = document.getElementById('btn-theme-light');
            
            if (btnDark && btnSepia && btnLight) {
                // Reset classes
                btnDark.className = "p-1.5 rounded transition-all text-slate-400 hover:text-white";
                btnSepia.className = "p-1.5 rounded transition-all text-slate-400 hover:text-white";
                btnLight.className = "p-1.5 rounded transition-all text-slate-400 hover:text-white";
                
                // Clear inline style colors
                btnDark.style.color = '';
                btnSepia.style.color = '';
                btnLight.style.color = '';
                
                // Set active class
                if (themeName === 'dark') {
                    btnDark.className = "p-1.5 rounded transition-all bg-slate-900 shadow";
                    btnDark.style.color = "var(--color-brand)";
                } else if (themeName === 'sepia') {
                    btnSepia.className = "p-1.5 rounded transition-all bg-slate-900 shadow";
                    btnSepia.style.color = "var(--color-brand)";
                } else if (themeName === 'light') {
                    btnLight.className = "p-1.5 rounded transition-all bg-slate-900 shadow";
                    btnLight.style.color = "var(--color-brand)";
                }
            }
            
            // Re-render charts to apply new color styles
            if (typeof renderCharts === 'function' && document.getElementById('financeChart')) {
                renderCharts();
            }
            if (typeof renderWorkoutProgressChart === 'function' && document.getElementById('workoutProgressChart')) {
                renderWorkoutProgressChart();
            }
        }

        // WMO Weather Code Mappers
        function getWeatherIcon(code, isDay) {
            if (code === 0) return isDay ? 'sun' : 'moon';
            if (code >= 1 && code <= 3) return isDay ? 'cloud-sun' : 'cloud-moon';
            if (code === 45 || code === 48) return 'cloud-fog';
            if ((code >= 51 && code <= 55) || (code >= 80 && code <= 82)) return 'cloud-drizzle';
            if (code >= 61 && code <= 65) return 'cloud-rain';
            if (code >= 71 && code <= 77) return 'snowflake';
            if (code >= 95) return 'cloud-lightning';
            return 'cloud';
        }

        function getWeatherDesc(code) {
            const map = {
                0: "Despejado",
                1: "Despejado parcial",
                2: "Parcialmente nublado",
                3: "Cubierto",
                45: "Niebla",
                48: "Niebla de escarcha",
                51: "Llovizna ligera",
                53: "Llovizna moderada",
                55: "Llovizna densa",
                61: "Lluvia débil",
                63: "Lluvia moderada",
                65: "Lluvia fuerte",
                71: "Nevada débil",
                73: "Nevada moderada",
                75: "Nevada fuerte",
                77: "Granizo",
                80: "Chubascos ligeros",
                81: "Chubascos moderados",
                82: "Chubascos fuertes",
                95: "Tormenta eléctrica",
                96: "Tormenta con granizo débil",
                99: "Tormenta con granizo fuerte"
            };
            return map[code] || "Variable";
        }

        async function fetchWeather() {
            try {
                // Concepción, Chile coordinates: lat=-36.8269, lon=-73.0498
                const url = "https://api.open-meteo.com/v1/forecast?latitude=-36.8269&longitude=-73.0498&current=temperature_2m,relative_humidity_2m,apparent_temperature,is_day,weather_code";
                const res = await fetch(url);
                if (!res.ok) throw new Error("Weather request failed");
                const data = await res.json();
                const cur = data.current;
                
                const temp = Math.round(cur.temperature_2m);
                const appTemp = Math.round(cur.apparent_temperature);
                const code = cur.weather_code;
                const isDay = cur.is_day === 1;
                const humidity = cur.relative_humidity_2m;
                
                const desc = getWeatherDesc(code);
                const iconName = getWeatherIcon(code, isDay);
                
                const weatherEl = document.getElementById('widget-weather');
                if (weatherEl) {
                    weatherEl.innerHTML = `
                        <div class="flex items-center gap-1.5 hover:text-emerald-400 cursor-pointer transition-colors" title="Sensación térmica: ${appTemp}°C | Humedad: ${humidity}% | Clic para actualizar" onclick="fetchWeather()">
                            <i data-lucide="map-pin" class="w-3.5 h-3.5 text-rose-500"></i>
                            <span class="font-bold text-slate-350">Concepción:</span>
                            <span class="text-slate-100 font-semibold">${temp}°C</span>
                            <span class="text-slate-400">•</span>
                            <i data-lucide="${iconName}" class="w-3.5 h-3.5 text-sky-400"></i>
                            <span class="text-slate-300">${desc}</span>
                        </div>
                    `;
                    lucide.createIcons();
                }
            } catch (e) {
                console.error("Error fetching weather:", e);
                const weatherTextEl = document.getElementById('widget-weather-text');
                if (weatherTextEl) {
                    weatherTextEl.innerHTML = `<span class="text-rose-400">Error al cargar clima de Concepción</span>`;
                }
            }
        }

        function updateClock() {
            const now = new Date();
            const days = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
            const months = [
                "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ];
            
            const dayName = days[now.getDay()];
            const dayNum = now.getDate();
            const monthName = months[now.getMonth()];
            const year = now.getFullYear();
            
            const hrs = String(now.getHours()).padStart(2, '0');
            const mins = String(now.getMinutes()).padStart(2, '0');
            const secs = String(now.getSeconds()).padStart(2, '0');
            
            const timeString = `${hrs}:${mins}:${secs}`;
            const dateString = `${dayName}, ${dayNum} de ${monthName} de ${year}`;
            
            const clockEl = document.getElementById('widget-date-time');
            if (clockEl) {
                clockEl.innerHTML = `
                    <span class="text-slate-400">${dateString}</span>
                    <span class="text-slate-400">|</span>
                    <span class="text-emerald-400 font-black text-sm tracking-widest">${timeString}</span>
                `;
            }
        }

        let widgetClockInterval = null;
        let widgetWeatherInterval = null;

        function startWidgets() {
            if (widgetClockInterval) clearInterval(widgetClockInterval);
            if (widgetWeatherInterval) clearInterval(widgetWeatherInterval);

            updateClock();
            widgetClockInterval = setInterval(updateClock, 1000);

            fetchWeather();
            widgetWeatherInterval = setInterval(fetchWeather, 600000); // 10 minutes
        }

        // Master App Initialization
        async function init() {
            try {
                // Load and apply theme
                const savedTheme = localStorage.getItem('app_theme') || 'dark';
                setTheme(savedTheme);

                // Set default form date to today
                document.getElementById('tx-date').value = new Date().toISOString().substring(0, 10);
                
                // Check security PIN activation status
                const statusRes = await fetch('/api/auth/status');
                const authStatus = await statusRes.json();
                
                updateSecurityStatusUI(authStatus.enabled);
                
                let headers = {};
                if (authStatus.enabled) {
                    const token = localStorage.getItem('app_auth_token');
                    if (!token) {
                        showLockScreen();
                        return;
                    }
                    headers['Authorization'] = `Bearer ${token}`;
                }

                // Load master state from Python backend
                const res = await fetch('/api/data', { headers });
                
                if (res.status === 401) {
                    localStorage.removeItem('app_auth_token');
                    showLockScreen();
                    return;
                }

                state = await res.json();
                if (!state.savingsGoal) {
                    state.savingsGoal = 1000;
                }
                hideLockScreen();
                
                // Load local notifications switch state
                isNotificationsEnabled = localStorage.getItem('power_notifications_enabled') === 'true';
                updateMasterNotificationUI();

                // Select current weekday by default
                const currentDayOfWeekIdx = (new Date().getDay() + 6) % 7; // Convert Sun-Sat to Mon-Sun
                currentWorkoutDayIdx = currentDayOfWeekIdx;
                currentMealsDay = DAYS_NAMES[currentDayOfWeekIdx];

                // Synchronize alarms checker loop
                setInterval(checkSystemAlarmHours, 10000);

                // Render first layout view
                switchTab(currentTab);

                // Start widgets (Clock & Weather)
                startWidgets();
            } catch (e) {
                console.error("App setup error:", e);
                showLockScreen();
            }
        }

        // Navigation Controller
        function switchTab(tabId) {
            currentTab = tabId;
            document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
            document.getElementById(`section-${tabId}`).classList.remove('hidden');

            document.querySelectorAll('nav button').forEach(btn => {
                btn.className = "flex-1 sm:flex-initial px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all text-slate-400 hover:text-white";
            });
            const activeBtn = document.getElementById(`tab-${tabId}`);
            if (activeBtn) {
                activeBtn.className = "flex-1 sm:flex-initial px-3 py-2 rounded-lg text-xs font-bold flex items-center justify-center gap-1.5 transition-all bg-[#185FA5] text-white shadow-lg";
            }

            if (tabId === 'workouts') renderWorkoutsView();
            if (tabId === 'meals') renderMealsView();
            if (tabId === 'finances') renderFinancesView();
            lucide.createIcons();
        }

        // BACKEND SYNCHRONIZER
        async function syncState() {
            try {
                const token = localStorage.getItem('app_auth_token');
                const res = await fetch('/api/data', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify(state)
                });
                return res.ok;
            } catch (e) {
                console.warn("Backend synchronization offline. Using client state cache.", e);
                return false;
            }
        }

        async function manualSaveState() {
            const btn = document.getElementById('btn-header-save');
            if (btn) {
                btn.disabled = true;
                btn.innerHTML = `<i data-lucide="loader" class="w-3.5 h-3.5 animate-spin"></i> Sincronizando...`;
                lucide.createIcons();
            }
            const success = await syncState();
            if (success) {
                triggerToastAlert("💾 Estado Guardado", "Tus datos se han guardado con éxito en la base de datos.");
            } else {
                triggerToastAlert("⚠️ Error al Guardar", "No se pudo sincronizar el estado con el servidor.");
            }
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = `<i data-lucide="save" class="w-3.5 h-3.5"></i> <span class="hidden sm:inline">Guardar Estado</span>`;
                lucide.createIcons();
            }
        }


        // ==========================================
        // 1. WORKOUT CONTROLLERS & VIEWS
        // ==========================================

        function renderWorkoutsView() {
            const calendar = document.getElementById('workouts-calendar');
            calendar.innerHTML = '';
            
            state.routine.days.forEach((day, idx) => {
                const isSelected = idx === currentWorkoutDayIdx;
                const totalEx = day.exercises.length;
                const completedEx = day.exercises.filter(e => e.completed).length;
                const isAllCompleted = totalEx > 0 && totalEx === completedEx;

                const btn = document.createElement('button');
                btn.onclick = () => { currentWorkoutDayIdx = idx; renderWorkoutsView(); };
                btn.className = `p-3 rounded-xl border flex flex-col items-center justify-center min-w-[70px] transition-all select-none ${
                    isSelected 
                        ? 'bg-brand border-brand text-white shadow-md' 
                        : 'bg-slate-950 border-slate-850 hover:border-slate-700 text-slate-400'
                }`;

                let badgeHtml = '';
                if (isAllCompleted) {
                    badgeHtml = `<span class="text-[10px] ${isSelected ? 'text-white' : 'text-green-400'}">✓</span>`;
                } else if (completedEx > 0) {
                    badgeHtml = `<span class="text-[9px] font-black ${isSelected ? 'text-white' : 'text-slate-100'}">${completedEx}/${totalEx}</span>`;
                } else {
                    badgeHtml = `<span class="text-[9px] ${isSelected ? 'text-white/70' : 'text-slate-500'}">${totalEx} ex</span>`;
                }

                btn.innerHTML = `
                    <span class="text-xs font-black uppercase font-display">${day.label}</span>
                    <span class="text-[9px] font-mono ${isSelected ? 'text-white/85' : 'text-slate-400'}">${day.trainingTime || 'No alarm'}</span>
                    <div class="mt-1">${badgeHtml}</div>
                `;
                calendar.appendChild(btn);
            });

            const activeDay = state.routine.days[currentWorkoutDayIdx];
            document.getElementById('wo-focus').innerText = `Enfoque: ${activeDay.focus || 'N/A'}`;
            document.getElementById('wo-time').innerText = activeDay.trainingTime || 'Sin hora';
            document.getElementById('wo-title').value = activeDay.title || activeDay.name;
            document.getElementById('input-alarm-time').value = activeDay.trainingTime || '08:00';
            document.getElementById('wo-warmup').value = activeDay.warmup || '';
            document.getElementById('wo-cool').value = activeDay.cool || '';

            // Update active day progress bar
            const totalActiveEx = activeDay.exercises.length;
            const completedActiveEx = activeDay.exercises.filter(e => e.completed).length;
            const activePercent = totalActiveEx > 0 ? Math.round((completedActiveEx / totalActiveEx) * 100) : 0;

            const progressPercentEl = document.getElementById('wo-progress-percent');
            const progressBarEl = document.getElementById('wo-progress-bar');
            
            if (progressPercentEl && progressBarEl) {
                progressPercentEl.innerText = `${activePercent}%`;
                progressBarEl.style.width = `${activePercent}%`;
                
                if (activePercent === 100) {
                    progressBarEl.className = "h-full bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)] transition-all duration-500 ease-out";
                    progressPercentEl.className = "font-mono text-emerald-400 text-xs font-black transition-all duration-300";
                } else {
                    progressBarEl.className = "h-full bg-brand rounded-full transition-all duration-500 ease-out";
                    progressPercentEl.className = "text-brand font-mono text-xs transition-all duration-300";
                }
            }

            // Exercises checklist
            const listContainer = document.getElementById('exercises-list');
            listContainer.innerHTML = '';

            if (activeDay.exercises.length === 0) {
                listContainer.innerHTML = '<p class="text-slate-500 text-xs italic py-4 text-center">No hay ejercicios registrados en esta rutina diaria.</p>';
            } else {
                activeDay.exercises.forEach((ex, exIdx) => {
                    const card = document.createElement('div');
                    card.className = `p-3.5 rounded-xl border transition-all ${
                        ex.completed 
                            ? 'bg-slate-950/40 border-slate-850 text-slate-400' 
                            : 'bg-slate-950 border-slate-850 text-slate-100 hover:border-slate-800'
                    }`;

                    card.innerHTML = `
                        <div class="flex items-start gap-3">
                            <input type="checkbox" ${ex.completed ? 'checked' : ''} onchange="toggleExerciseCompletion(${exIdx})" class="w-4 h-4 text-brand bg-slate-900 border-slate-700 rounded focus:ring-brand focus:ring-offset-slate-950 mt-1 cursor-pointer" />
                            <div class="flex-1 space-y-1 min-w-0 text-xs">
                                <div class="flex justify-between items-start gap-2">
                                    <input type="text" value="${ex.name}" onchange="editExerciseField(${exIdx}, 'name', this.value)" class="font-bold bg-transparent border-b border-transparent hover:border-slate-400 focus:border-brand focus:outline-none w-full text-current" />
                                    <button onclick="deleteExercise(${exIdx})" class="text-slate-500 hover:text-rose-400 p-0.5"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button>
                                </div>
                                <div class="flex items-center gap-1 text-slate-400">
                                    <span class="font-bold uppercase tracking-wider text-[10px] text-brand">Sets/Reps:</span>
                                    <input type="text" value="${ex.sets}" onchange="editExerciseField(${exIdx}, 'sets', this.value)" class="bg-transparent border-b border-transparent hover:border-slate-400 focus:border-brand focus:outline-none font-mono text-[11px] text-current" />
                                </div>
                                <div class="text-[11px] text-slate-350">
                                    <textarea onchange="editExerciseField(${exIdx}, 'detail', this.value)" class="bg-transparent border-0 focus:ring-0 focus:outline-none resize-none leading-relaxed h-10 w-full text-current" placeholder="Detalle técnico del ejercicio...">${ex.detail || ''}</textarea>
                                </div>
                                <div class="p-2 bg-slate-900/60 rounded-lg text-[10.5px] border border-slate-850/50 text-slate-350 flex items-start gap-1">
                                    <i data-lucide="shield-alert" class="w-3.5 h-3.5 text-brand mt-0.5 shrink-0"></i>
                                    <div class="flex-1">
                                        <span class="font-bold text-brand">Por qué para Rider:</span>
                                        <input type="text" value="${ex.why}" onchange="editExerciseField(${exIdx}, 'why', this.value)" class="bg-transparent border-b border-transparent hover:border-slate-400 focus:border-brand focus:outline-none w-full italic text-[11.5px] text-current" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    listContainer.appendChild(card);
                });
            }
            lucide.createIcons();
            renderWorkoutProgressChart();
        }

        function toggleExerciseCompletion(exIdx) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.exercises[exIdx].completed = !day.exercises[exIdx].completed;
            syncState();
            renderWorkoutsView();
        }

        function editExerciseField(exIdx, field, val) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.exercises[exIdx][field] = val;
            syncState();
        }

        function deleteExercise(exIdx) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.exercises.splice(exIdx, 1);
            syncState();
            renderWorkoutsView();
        }

        function addNewExercise() {
            const day = state.routine.days[currentWorkoutDayIdx];
            const newEx = {
                id: `ex-${Date.now()}`,
                name: "Nuevo ejercicio customizable",
                sets: "4 x 10",
                detail: "Agrega las instrucciones aquí haciendo click.",
                why: "Añade por qué sirve para la postura del rider aquí.",
                completed: false
            };
            day.exercises.push(newEx);
            syncState();
            renderWorkoutsView();
        }

        function updateDayTitle(val) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.title = val;
            day.name = val;
            syncState();
        }

        function updateAlarmTime(val) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.trainingTime = val;
            document.getElementById('wo-time').innerText = val;
            syncState();
            renderWorkoutsView();
        }

        function updateWarmup(val) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.warmup = val;
            syncState();
        }

        function updateCool(val) {
            const day = state.routine.days[currentWorkoutDayIdx];
            day.cool = val;
            syncState();
        }


        // ==========================================
        // ALARMS MECHANISM & WEB AUDIO SYNTH
        // ==========================================

        function toggleNotificationsMaster() {
            isNotificationsEnabled = !isNotificationsEnabled;
            localStorage.setItem('power_notifications_enabled', String(isNotificationsEnabled));
            updateMasterNotificationUI();
            
            if (isNotificationsEnabled) {
                // Request native web notification permissions
                if ('Notification' in window) {
                    Notification.requestPermission();
                }
                playHighFreqAlarmBeep();
                triggerToastAlert("🔔 Alarma Activada", "Has habilitado el sistema de alertas de entrenamiento diarias en esta ventana.");
            } else {
                triggerToastAlert("🔕 Alarma Desactivada", "Notificaciones y recordatorios apagados.");
            }
        }

        function updateMasterNotificationUI() {
            const toggleCircle = document.getElementById('toggle-circle');
            const toggleBtn = document.getElementById('btn-master-alarm');
            const badge = document.getElementById('notif-badge-state');

            if (isNotificationsEnabled) {
                toggleBtn.className = "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-emerald-600";
                toggleCircle.className = "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out translate-x-5";
                badge.className = "p-2 bg-emerald-950/40 border border-emerald-900 text-emerald-400 rounded-lg font-bold text-[10px] uppercase tracking-wider text-center";
                badge.innerHTML = "🟢 Alarmas Activas";
            } else {
                toggleBtn.className = "relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none bg-slate-800";
                toggleCircle.className = "pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition duration-200 ease-in-out translate-x-0";
                badge.className = "p-2 bg-slate-950 border border-slate-800 text-amber-500 rounded-lg font-bold text-[10px] uppercase tracking-wider text-center";
                badge.innerHTML = "🔴 Alarmas Inactivas";
            }
        }

        function playHighFreqAlarmBeep() {
            try {
                const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                function beep(freq, duration, delay) {
                    setTimeout(() => {
                        const osc = audioCtx.createOscillator();
                        const gain = audioCtx.createGain();
                        osc.connect(gain);
                        gain.connect(audioCtx.destination);
                        
                        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
                        gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
                        gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + duration - 0.05);
                        
                        osc.start(audioCtx.currentTime);
                        osc.stop(audioCtx.currentTime + duration);
                    }, delay);
                }
                beep(880, 0.25, 0);
                beep(1200, 0.35, 250);
            } catch (e) {
                console.warn("Audio Context blocked or not supported:", e);
            }
        }

        function testAlarmDemo() {
            const btn = document.getElementById('btn-test-alarm');
            const txt = document.getElementById('test-btn-text');
            
            if (testTimer) return;
            
            let count = 5;
            txt.innerText = `Probando en ${count}s...`;
            btn.disabled = true;

            testTimer = setInterval(() => {
                count--;
                if (count <= 0) {
                    clearInterval(testTimer);
                    testTimer = null;
                    txt.innerText = "Probar Alarma de Prueba 📣";
                    btn.disabled = false;
                    
                    // Trigger actual alarm behavior
                    fireActiveAlarmOverlay(
                        state.routine.days[currentWorkoutDayIdx].name,
                        state.routine.days[currentWorkoutDayIdx].title || "Entrenamiento Pro",
                        state.routine.days[currentWorkoutDayIdx].focus || "Fuerza y movilidad"
                    );
                } else {
                    txt.innerText = `Probando en ${count}s...`;
                }
            }, 1000);
        }

        function checkSystemAlarmHours() {
            if (!isNotificationsEnabled) return;
            
            const now = new Date();
            const hrs = String(now.getHours()).padStart(2, '0');
            const mins = String(now.getMinutes()).padStart(2, '0');
            const curTime = `${hrs}:${mins}`;

            // Map standard js Sunday-Saturday to index
            const daysMap = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
            const currentDayName = daysMap[now.getDay()];

            state.routine.days.forEach(day => {
                const normalizedDayName = (day.name || '').split(" ")[0].trim();
                if (normalizedDayName === currentDayName && day.trainingTime === curTime) {
                    const uniqueKey = `${day.id}-${curTime}-${now.toDateString()}`;
                    if (lastAlarmFiredKey !== uniqueKey) {
                        lastAlarmFiredKey = uniqueKey;
                        fireActiveAlarmOverlay(day.name, day.title || "Entrenamiento", day.focus || "Acondicionamiento");
                    }
                }
            });
        }

        function fireActiveAlarmOverlay(day, title, focus) {
            playHighFreqAlarmBeep();
            
            // Native HTML5 system notifications
            if ('Notification' in window && Notification.permission === 'granted') {
                new Notification(`🏁 ¡Es hora de entrenar! 🏁`, {
                    body: `Tu rutina programada: "${title}". ¡Dalo todo hoy! 💪`,
                    requireInteraction: true
                });
            }

            // In-app Popup Overlay Modal
            document.getElementById('alarm-wo-day').innerText = day;
            document.getElementById('alarm-wo-title').innerText = title;
            document.getElementById('alarm-wo-focus').innerText = `Enfoque: ${focus}`;
            document.getElementById('alarm-fire-overlay').classList.remove('hidden');
        }

        function dismissAlarmOverlay() {
            document.getElementById('alarm-fire-overlay').classList.add('hidden');
        }


        // ==========================================
        // 2. DIET & MEALS CONTROLLERS & VIEWS
        // ==========================================

        function renderMealsView() {
            // Days calendar selector tabs
            const container = document.getElementById('meals-calendar-tabs');
            container.innerHTML = '';

            DAYS_NAMES.forEach(d => {
                const isSelected = d === currentMealsDay;
                const btn = document.createElement('button');
                btn.onclick = () => { currentMealsDay = d; renderMealsView(); };
                btn.className = `px-4 py-2 text-xs font-bold rounded-lg shrink-0 transition-all ${
                    isSelected 
                        ? 'bg-[#185FA5] text-white shadow-md' 
                        : 'bg-slate-950 hover:bg-slate-850 text-slate-400 border border-slate-850'
                }`;
                btn.innerText = d;
                container.appendChild(btn);
            });

            // Set Calorie Target Input
            document.getElementById('input-calorie-target').value = state.calorieTarget;

            // Render current meals list
            const mealsList = document.getElementById('meals-list');
            mealsList.innerHTML = '';

            const currentPlan = state.meals[currentMealsDay] || {};
            const mealTypes = ['desayuno', 'almuerzo', 'merienda', 'cena'];

            let totalCaloriesPlanned = 0;
            let totalCaloriesConsumed = 0;
            let totalProt = 0;
            let totalCarb = 0;
            let totalFat = 0;

            mealTypes.forEach(m => {
                const item = currentPlan[m] || { name: 'Por planificar', calories: 0, protein: 0, carbs: 0, fat: 0, completed: false };
                
                totalCaloriesPlanned += item.calories;
                if (item.completed) {
                    totalCaloriesConsumed += item.calories;
                    totalProt += item.protein;
                    totalCarb += item.carbs;
                    totalFat += item.fat;
                }

                const card = document.createElement('div');
                card.className = `p-4 rounded-xl border transition-all ${
                    item.completed 
                        ? 'bg-slate-950/40 border-slate-850/60 text-slate-400' 
                        : 'bg-slate-950 border-slate-850 text-slate-100 hover:border-slate-800'
                }`;

                let ingredientsHtml = '';
                if (item.ingredients && item.ingredients.length > 0) {
                    ingredientsHtml = `
                        <div class="mt-2.5 pt-2 border-t border-slate-900 text-[11px] text-slate-400">
                            <span class="font-bold text-emerald-400 uppercase text-[9px] block mb-1">Ingredientes:</span>
                            <ul class="list-disc list-inside space-y-0.5">
                                ${item.ingredients.map(ing => `<li>${ing}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }

                let prepHtml = '';
                if (item.recipeInstructions) {
                    prepHtml = `
                        <div class="mt-2 text-[11px] text-slate-400 bg-slate-900/60 p-2 rounded-lg border border-slate-850">
                            <span class="font-bold text-blue-400 uppercase text-[9px] block mb-0.5">Instrucciones de Cocina:</span>
                            <p class="leading-relaxed">${item.recipeInstructions}</p>
                        </div>
                    `;
                }

                card.innerHTML = `
                    <div class="flex items-start gap-3">
                        <input type="checkbox" ${item.completed ? 'checked' : ''} onchange="toggleMealCompletion('${m}')" class="w-4 h-4 text-emerald-500 bg-slate-900 border-slate-700 rounded focus:ring-emerald-500 mt-1 cursor-pointer" />
                        <div class="flex-1 text-xs">
                            <div class="flex justify-between items-start gap-2">
                                <div class="space-y-0.5">
                                    <span class="text-[9px] uppercase font-bold text-emerald-400 block">${m}</span>
                                    <input type="text" value="${item.name}" onchange="editMealName('${m}', this.value)" class="font-bold text-slate-200 bg-transparent border-b border-transparent hover:border-slate-750 focus:border-emerald-500 focus:outline-none w-full" />
                                </div>
                                <span class="font-mono font-bold text-slate-350 text-[11px] shrink-0 bg-slate-900 border border-slate-800 px-2 py-0.5 rounded">${item.calories} kcal</span>
                            </div>

                            <div class="flex flex-wrap items-center gap-4 mt-2 text-[10.5px] font-mono text-slate-400">
                                <span>P: <input type="number" value="${item.protein}" onchange="editMealMacro('${m}', 'protein', this.value)" class="w-8 bg-transparent text-center border-b border-transparent hover:border-slate-750 focus:border-emerald-500 font-bold" />g</span>
                                <span>HC: <input type="number" value="${item.carbs}" onchange="editMealMacro('${m}', 'carbs', this.value)" class="w-8 bg-transparent text-center border-b border-transparent hover:border-slate-750 focus:border-emerald-500 font-bold" />g</span>
                                <span>G: <input type="number" value="${item.fat}" onchange="editMealMacro('${m}', 'fat', this.value)" class="w-8 bg-transparent text-center border-b border-transparent hover:border-slate-750 focus:border-emerald-500 font-bold" />g</span>
                                <span>Kcal: <input type="number" value="${item.calories}" onchange="editMealMacro('${m}', 'calories', this.value)" class="w-12 bg-transparent text-center border-b border-transparent hover:border-slate-750 focus:border-emerald-500 font-bold" /></span>
                            </div>

                            ${ingredientsHtml}
                            ${prepHtml}
                        </div>
                    </div>
                `;
                mealsList.appendChild(card);
            });

            // Update Calories statistics widget
            const target = state.calorieTarget || 2100;
            const progressPercent = Math.min(100, Math.round((totalCaloriesConsumed / target) * 100));
            document.getElementById('txt-calories-progress').innerText = `${progressPercent}%`;
            document.getElementById('bar-calories-progress').style.width = `${progressPercent}%`;

            document.getElementById('txt-macro-prot').innerText = `${totalProt}g`;
            document.getElementById('txt-macro-carb').innerText = `${totalCarb}g`;
            document.getElementById('txt-macro-fat').innerText = `${totalFat}g`;

            // Hydration widget state
            const waterVal = state.waterLog[currentMealsDay] || 0;
            document.getElementById('txt-water-count').innerText = `${waterVal} / 8 vasos`;

            const waterContainer = document.getElementById('water-glasses-container');
            waterContainer.innerHTML = '';
            for (let i = 1; i <= 8; i++) {
                const glass = document.createElement('div');
                glass.onclick = () => { selectWaterDirect(i); };
                if (i <= waterVal) {
                    glass.className = "w-6 h-8 bg-sky-500 border border-sky-400 rounded-b-md rounded-t-sm cursor-pointer shadow flex items-center justify-center text-[10px] text-white font-black animate-pulse";
                    glass.innerText = "💧";
                } else {
                    glass.className = "w-6 h-8 bg-slate-950 border border-slate-800 hover:border-slate-700 rounded-b-md rounded-t-sm cursor-pointer transition-all";
                }
                waterContainer.appendChild(glass);
            }
            lucide.createIcons();
        }

        function toggleMealCompletion(mealType) {
            const plan = state.meals[currentMealsDay];
            plan[mealType].completed = !plan[mealType].completed;
            syncState();
            renderMealsView();
        }

        function editMealName(mealType, val) {
            const plan = state.meals[currentMealsDay];
            plan[mealType].name = val;
            syncState();
        }

        function editMealMacro(mealType, field, val) {
            const plan = state.meals[currentMealsDay];
            plan[mealType][field] = parseInt(val) || 0;
            syncState();
            renderMealsView();
        }

        function updateCalorieTarget(val) {
            state.calorieTarget = parseInt(val) || 2100;
            syncState();
            renderMealsView();
        }

        function adjustWater(modifier) {
            const current = state.waterLog[currentMealsDay] || 0;
            state.waterLog[currentMealsDay] = Math.max(0, Math.min(8, current + modifier));
            syncState();
            renderMealsView();
        }

        function selectWaterDirect(val) {
            state.waterLog[currentMealsDay] = val;
            syncState();
            renderMealsView();
        }

        function resetDayMeals() {
            if (confirm("¿Quieres restablecer el plan de comidas de este día?")) {
                state.meals[currentMealsDay] = {
                    "desayuno": { "id": `d-${Date.now()}`, "name": "Por planificar", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "completed": false },
                    "almuerzo": { "id": `a-${Date.now()}`, "name": "Por planificar", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "completed": false },
                    "merienda": { "id": `m-${Date.now()}`, "name": "Por planificar", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "completed": false },
                    "cena": { "id": `c-${Date.now()}`, "name": "Por planificar", "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "completed": false }
                };
                syncState();
                renderMealsView();
            }
        }

        function openMealGenerator() {
            document.getElementById('ai-meals-err').classList.add('hidden');
            document.getElementById('ai-meals-modal').classList.remove('hidden');
        }

        function closeMealGenerator() {
            document.getElementById('ai-meals-modal').classList.add('hidden');
        }

        async function triggerAIPlanGeneration() {
            const pref = document.getElementById('diet-preference').value;
            const goal = document.getElementById('diet-goal').value;
            const errDiv = document.getElementById('ai-meals-err');
            const submitBtn = document.getElementById('btn-ai-meals-submit');
            
            errDiv.classList.add('hidden');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="animate-spin mr-1">⚡</span> Generando...';

            try {
                const token = localStorage.getItem('app_auth_token');
                const res = await fetch('/api/meals/generate', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        dietPreference: pref,
                        calorieGoal: state.calorieTarget,
                        objective: goal
                    })
                });

                if (!res.ok) throw new Error("No se pudo obtener el menú de la IA.");

                const generatedPlan = await res.json();
                
                // Set the generated plan as current day's meals
                state.meals[currentMealsDay] = {
                    desayuno: { ...generatedPlan.desayuno, id: `des-${Date.now()}`, completed: false },
                    almuerzo: { ...generatedPlan.almuerzo, id: `alm-${Date.now()}`, completed: false },
                    merienda: { ...generatedPlan.merienda, id: `mer-${Date.now()}`, completed: false },
                    cena: { ...generatedPlan.cena, id: `cen-${Date.now()}`, completed: false }
                };

                syncState();
                renderMealsView();
                closeMealGenerator();
                triggerToastAlert("🟢 Menú Generado", "El asistente nutricional ha diseñado tus recetas para hoy.");
            } catch (e) {
                errDiv.innerText = "Error: El servidor de IA está ocupado. Usaremos un plan optimizado predeterminado de deportista.";
                errDiv.classList.remove('hidden');

                // Auto fallback to healthy templates so it always works beautifully
                state.meals[currentMealsDay] = {
                    "desayuno": { "id": `des-fb-${Date.now()}`, "name": "Tortilla de claras de huevo con aguacate y té verde", "calories": 380, "protein": 30, "carbs": 12, "fat": 15, "ingredients": ["4 Claras de huevo", "1 Huevo entero", "50g Aguacate fresco", "1 Taza de té verde"], "recipeInstructions": "Bate los huevos, haz la tortilla y sirve con rodajas de aguacate al lado.", "completed": false },
                    "almuerzo": { "id": `alm-fb-${Date.now()}`, "name": "Arroz con ternera magra troceada y pimientos asados", "calories": 620, "protein": 45, "carbs": 65, "fat": 12, "ingredients": ["150g Ternera magra", "80g Arroz integral en seco", "1 Pimiento rojo grande", "Aceite de oliva"], "recipeInstructions": "Cuece el arroz. Cocina la ternera a fuego rápido con tiras de pimiento y junta todo.", "completed": false },
                    "merienda": { "id": `mer-fb-${Date.now()}`, "name": "Licuado de proteínas con plátano y avena", "calories": 310, "protein": 28, "carbs": 40, "fat": 5, "ingredients": ["1 Cazo proteína de suero", "1 Plátano mediano", "30g Copos de avena", "250ml Agua"], "recipeInstructions": "Licúa todos los ingredientes juntos en batidora hasta obtener un batido cremoso.", "completed": false },
                    "cena": { "id": `cen-fb-${Date.now()}`, "name": "Guiso de merluza al vapor con puré de calabaza", "calories": 400, "protein": 38, "carbs": 25, "fat": 8, "ingredients": ["200g Lomo de merluza", "150g Calabaza cocida", "1 Patata pequeña", "Especias al gusto"], "recipeInstructions": "Cocina el pescado al vapor. Tritura la calabaza y patata cocidas con pimienta negra para el puré.", "completed": false }
                };
                syncState();
                renderMealsView();
                setTimeout(() => {
                    closeMealGenerator();
                    triggerToastAlert("🟡 Menú de Respaldo", "Plan de alto rendimiento optimizado cargado con éxito.");
                }, 2000);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-lucide="sparkles" class="w-4.5 h-4.5"></i> Generar Menú';
                lucide.createIcons();
            }
        }


        // ==========================================
        // 3. FINANCES CONTROLLERS & VIEWS
        // ==========================================

        function setTxFormType(type) {
            txFormType = type;
            const btnGasto = document.getElementById('btn-tx-gasto');
            const btnIngreso = document.getElementById('btn-tx-ingreso');
            if (type === 'gasto') {
                btnGasto.className = "flex-1 py-1.5 rounded-md font-bold text-center text-rose-500 bg-slate-900 shadow";
                btnIngreso.className = "flex-1 py-1.5 rounded-md font-bold text-center text-slate-400 hover:text-white";
            } else {
                btnGasto.className = "flex-1 py-1.5 rounded-md font-bold text-center text-slate-400 hover:text-white";
                btnIngreso.className = "flex-1 py-1.5 rounded-md font-bold text-center text-emerald-500 bg-slate-900 shadow";
            }
        }

        function renderFinancesView() {
            // Stats calculations
            const totalIncome = state.transactions
                .filter(t => t.type === 'ingreso')
                .reduce((acc, t) => acc + (t.amount || 0), 0);

            const totalExpenses = state.transactions
                .filter(t => t.type === 'gasto')
                .reduce((acc, t) => acc + (t.amount || 0), 0);

            const netBalance = totalIncome - totalExpenses;

            document.getElementById('txt-total-income').innerText = `$${totalIncome.toFixed(2)}`;
            document.getElementById('txt-total-expenses').innerText = `$${totalExpenses.toFixed(2)}`;
            
            const balDiv = document.getElementById('txt-net-balance');
            const cardBal = document.getElementById('card-balance');
            const iconBalBg = document.getElementById('icon-balance-bg');

            balDiv.innerText = `$${netBalance.toFixed(2)}`;

            if (netBalance >= 0) {
                balDiv.className = "text-xl font-black font-mono text-emerald-400";
                cardBal.className = "bg-slate-900 border border-emerald-900/30 rounded-xl p-5 flex items-center gap-4 shadow-lg";
                iconBalBg.className = "p-3 bg-emerald-950/40 text-emerald-400 rounded-xl";
            } else {
                balDiv.className = "text-xl font-black font-mono text-rose-400";
                cardBal.className = "bg-slate-900 border border-rose-900/30 rounded-xl p-5 flex items-center gap-4 shadow-lg";
                iconBalBg.className = "p-3 bg-rose-950/40 text-rose-400 rounded-xl";
            }

            // Update Savings Goal UI
            if (!state.savingsGoal) {
                state.savingsGoal = 1000;
            }
            const savingsGoal = state.savingsGoal;
            document.getElementById('savings-goal-display').innerText = `$${savingsGoal.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            document.getElementById('input-savings-goal').value = savingsGoal;
            document.getElementById('savings-current-amount').innerText = `$${netBalance.toLocaleString('es-ES', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

            const savingsPercent = savingsGoal > 0 ? Math.max(0, Math.round((netBalance / savingsGoal) * 100)) : 0;
            const savingsBar = document.getElementById('savings-progress-bar');
            const savingsPercentText = document.getElementById('savings-progress-percent');
            const savingsStatusText = document.getElementById('savings-progress-status');

            if (savingsBar && savingsPercentText && savingsStatusText) {
                const boundedPercent = Math.min(100, savingsPercent);
                savingsBar.style.width = `${boundedPercent}%`;
                savingsPercentText.innerText = `${savingsPercent}%`;

                if (savingsPercent >= 100) {
                    savingsBar.className = "h-full bg-gradient-to-r from-emerald-400 to-teal-400 rounded-full shadow-[0_0_12px_rgba(16,185,129,0.6)] animate-pulse transition-all duration-1000 ease-out";
                    savingsStatusText.innerText = "¡Meta de Ahorro Alcanzada! 🎉";
                    savingsStatusText.className = "text-emerald-400 font-bold animate-bounce transition-all duration-300";
                    savingsPercentText.className = "font-mono text-emerald-400 font-black scale-110 transition-all duration-300";
                } else {
                    savingsBar.className = "h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all duration-1000 ease-out";
                    savingsStatusText.innerText = "Progreso hacia tu meta de ahorro";
                    savingsStatusText.className = "text-slate-400 transition-all duration-300";
                    savingsPercentText.className = "font-mono text-emerald-400 transition-all duration-300";
                }
            }

            renderTransactions();
            renderCharts();
        }

        let isEditingSavingsGoal = false;
        function toggleEditSavingsGoal() {
            isEditingSavingsGoal = !isEditingSavingsGoal;
            const displayEl = document.getElementById('savings-goal-display');
            const editContainerEl = document.getElementById('savings-goal-edit-container');
            const btnEl = document.getElementById('btn-edit-savings-goal');

            if (isEditingSavingsGoal) {
                displayEl.classList.add('hidden');
                editContainerEl.classList.remove('hidden');
                const inputEl = document.getElementById('input-savings-goal');
                inputEl.value = state.savingsGoal || 1000;
                inputEl.focus();
                btnEl.innerHTML = `<i data-lucide="x" class="w-3.5 h-3.5"></i>`;
            } else {
                displayEl.classList.remove('hidden');
                editContainerEl.classList.add('hidden');
                btnEl.innerHTML = `<i data-lucide="edit-3" class="w-3.5 h-3.5"></i>`;
            }
            lucide.createIcons();
        }

        async function saveSavingsGoal() {
            const newVal = parseFloat(document.getElementById('input-savings-goal').value);
            if (!isNaN(newVal) && newVal > 0) {
                state.savingsGoal = newVal;
                await syncState();
                renderFinancesView();
                toggleEditSavingsGoal();
                triggerToastAlert("🎯 Meta Actualizada", `Tu nueva meta de ahorro es de $${newVal.toLocaleString('es-ES')}`);
            }
        }

        function renderTransactions() {
            const list = document.getElementById('tx-ledger-list');
            list.innerHTML = '';

            const query = document.getElementById('tx-search').value.toLowerCase();
            const filtered = state.transactions.filter(t => t.title.toLowerCase().includes(query));

            if (filtered.length === 0) {
                list.innerHTML = '<p class="text-slate-500 text-xs italic py-4 text-center">No hay transacciones registradas.</p>';
            } else {
                filtered.forEach(t => {
                    const item = document.createElement('div');
                    item.className = "p-3 bg-slate-950 rounded-xl border border-slate-850 flex items-center justify-between text-xs";

                    const isGasto = t.type === 'gasto';
                    const symbol = isGasto ? '-' : '+';
                    const colorClass = isGasto ? 'text-rose-400' : 'text-emerald-400';
                    const badgeBg = isGasto ? 'bg-rose-950/30 text-rose-400 border-rose-900/50' : 'bg-emerald-950/30 text-emerald-400 border-emerald-900/50';

                    item.innerHTML = `
                        <div class="space-y-1 min-w-0">
                            <div class="flex items-center gap-1.5 flex-wrap">
                                <span class="font-bold text-slate-200">${t.title}</span>
                                <span class="text-[9px] font-mono font-bold uppercase border px-1.5 rounded ${badgeBg}">${t.category || 'Varios'}</span>
                            </div>
                            <span class="text-[10px] text-slate-500 block">${t.date}</span>
                        </div>
                        <div class="flex items-center gap-3 shrink-0">
                            <span class="font-mono font-black ${colorClass}">${symbol}$${t.amount.toFixed(2)}</span>
                            <button onclick="deleteTransaction('${t.id}')" class="text-slate-500 hover:text-rose-400 p-1"><i data-lucide="trash-2" class="w-3.5 h-3.5"></i></button>
                        </div>
                    `;
                    list.appendChild(item);
                });
            }
            lucide.createIcons();
        }

        function saveNewTransaction(e) {
            e.preventDefault();
            const title = document.getElementById('tx-title').value;
            const amount = parseFloat(document.getElementById('tx-amount').value) || 0;
            const cat = document.getElementById('tx-category').value;
            const date = document.getElementById('tx-date').value;

            if (!title || amount <= 0) return;

            const newTx = {
                id: `tx-${Date.now()}`,
                title: title.trim(),
                amount,
                type: txFormType,
                category: cat,
                date
            };

            state.transactions.unshift(newTx);
            syncState();

            // Reset form fields
            document.getElementById('tx-title').value = '';
            document.getElementById('tx-amount').value = '';

            renderFinancesView();
            triggerToastAlert("💰 Ledger Actualizado", "El movimiento se ha añadido con éxito.");
        }

        function deleteTransaction(id) {
            state.transactions = state.transactions.filter(t => t.id !== id);
            syncState();
            renderFinancesView();
        }

        function setChartType(type) {
            chartType = type;
            document.getElementById('btn-chart-pie').className = type === 'pie' ? "px-2.5 py-1 text-[10px] font-bold rounded bg-slate-900 text-white shadow" : "px-2.5 py-1 text-[10px] font-bold rounded text-slate-400 hover:text-slate-200";
            document.getElementById('btn-chart-bar').className = type === 'bar' ? "px-2.5 py-1 text-[10px] font-bold rounded bg-slate-900 text-white shadow" : "px-2.5 py-1 text-[10px] font-bold rounded text-slate-400 hover:text-slate-200";
            renderCharts();
        }

        function setFinanceChartTab(tab) {
            activeFinanceChartTab = tab;
            
            // Update button styles
            const btnExpenses = document.getElementById('btn-fin-tab-expenses');
            const btnSummary = document.getElementById('btn-fin-tab-summary');
            const controls = document.getElementById('expenses-chart-controls');
            
            if (tab === 'expenses') {
                btnExpenses.className = "px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all bg-slate-900 text-white shadow flex items-center gap-1.5";
                btnSummary.className = "px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5";
                controls.classList.remove('hidden');
            } else {
                btnExpenses.className = "px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all text-slate-400 hover:text-white flex items-center gap-1.5";
                btnSummary.className = "px-3.5 py-1.5 rounded-lg text-[10.5px] font-bold transition-all bg-slate-900 text-white shadow flex items-center gap-1.5";
                controls.classList.add('hidden');
            }
            
            renderCharts();
        }

        function renderCharts() {
            if (!document.getElementById('financeChart')) return;
            if (!state || !state.transactions) return;
            const ctx = document.getElementById('financeChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();

            if (activeFinanceChartTab === 'expenses') {
                document.getElementById('expenses-chart-controls').classList.remove('hidden');

                // Prepare data by category
                const categories = ['Comida', 'Gimnasio', 'Alquiler', 'Sueldo', 'Ocio', 'Varios'];
                const colors = ['#10b981', '#6366f1', '#f59e0b', '#3b82f6', '#ec4899', '#8b5cf6'];
                const categoryTotals = categories.reduce((acc, c) => ({ ...acc, [c]: 0 }), {});

                state.transactions
                    .filter(t => t.type === 'gasto')
                    .forEach(t => {
                        const cat = t.category || 'Varios';
                        if (categoryTotals[cat] !== undefined) {
                            categoryTotals[cat] += t.amount;
                        } else {
                            categoryTotals['Varios'] += t.amount;
                        }
                    });

                const labels = [];
                const dataVals = [];
                const bgColors = [];

                categories.forEach((cat, idx) => {
                    const total = categoryTotals[cat];
                    if (total > 0) {
                        labels.push(cat);
                        dataVals.push(total);
                        bgColors.push(colors[idx]);
                    }
                });

                if (dataVals.length === 0) {
                    document.getElementById('chart-container').innerHTML = `
                        <div class="text-center text-slate-500 text-xs italic">
                            Agrega gastos en el panel superior para ver las gráficas de desglose financiero de inmediato.
                        </div>
                        <canvas id="financeChart" class="max-h-full hidden"></canvas>
                    `;
                    return;
                } else {
                    if (!document.getElementById('financeChart')) {
                        document.getElementById('chart-container').innerHTML = '<canvas id="financeChart" class="max-h-full"></canvas>';
                    }
                }

                chartInstance = new Chart(document.getElementById('financeChart'), {
                    type: chartType,
                    data: {
                        labels: labels,
                        datasets: [{
                            data: dataVals,
                            backgroundColor: bgColors,
                            borderColor: '#0f172a',
                            borderWidth: 2
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    color: '#94a3b8',
                                    font: { size: 10, weight: 'bold' },
                                    boxWidth: 10
                                }
                            }
                        }
                    }
                });
            } else {
                document.getElementById('expenses-chart-controls').classList.add('hidden');

                const totalIncome = state.transactions
                    .filter(t => t.type === 'ingreso')
                    .reduce((acc, t) => acc + (t.amount || 0), 0);

                const totalExpenses = state.transactions
                    .filter(t => t.type === 'gasto')
                    .reduce((acc, t) => acc + (t.amount || 0), 0);

                const netBalance = totalIncome - totalExpenses;

                if (!document.getElementById('financeChart')) {
                    document.getElementById('chart-container').innerHTML = '<canvas id="financeChart" class="max-h-full"></canvas>';
                }

                chartInstance = new Chart(document.getElementById('financeChart'), {
                    type: 'bar',
                    data: {
                        labels: ['Ingresos Totales', 'Gastos Totales', 'Balance Neto'],
                        datasets: [{
                            label: 'Monto ($)',
                            data: [totalIncome, totalExpenses, netBalance],
                            backgroundColor: ['#10b981', '#f43f5e', netBalance >= 0 ? '#3b82f6' : '#f59e0b'],
                            borderColor: '#0f172a',
                            borderWidth: 1.5,
                            borderRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: { color: '#1e293b' },
                                ticks: {
                                    color: '#94a3b8',
                                    font: { size: 10, weight: 'bold' },
                                    callback: function(value) { return '$' + value; }
                                }
                            },
                            x: {
                                grid: { display: false },
                                ticks: {
                                    color: '#94a3b8',
                                    font: { size: 10, weight: 'bold' }
                                }
                            }
                        },
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        return ` $${context.parsed.y.toFixed(2)}`;
                                    }
                                }
                            }
                        }
                    }
                });
            }
        }

        function renderWorkoutProgressChart() {
            if (!document.getElementById('workoutProgressChart')) return;
            if (!state || !state.routine || !state.routine.days) return;

            const days = state.routine.days;
            const labels = days.map(d => d.label);
            const dataVals = days.map(day => {
                const total = day.exercises.length;
                if (total === 0) return 0;
                const completed = day.exercises.filter(e => e.completed).length;
                return Math.round((completed / total) * 100);
            });

            const activeDay = days[currentWorkoutDayIdx];
            const activeTotal = activeDay.exercises.length;
            const activeCompleted = activeDay.exercises.filter(e => e.completed).length;
            document.getElementById('txt-workout-today-status').innerText = `${activeCompleted}/${activeTotal} (${activeTotal > 0 ? Math.round((activeCompleted / activeTotal) * 100) : 0}%)`;

            const totalAllExercises = days.reduce((acc, d) => acc + d.exercises.length, 0);
            const completedAllExercises = days.reduce((acc, d) => acc + d.exercises.filter(e => e.completed).length, 0);
            const overallPerformance = totalAllExercises > 0 ? Math.round((completedAllExercises / totalAllExercises) * 100) : 0;
            document.getElementById('txt-workout-week-status').innerText = `${overallPerformance}%`;

            const ctx = document.getElementById('workoutProgressChart').getContext('2d');
            if (workoutChartInstance) workoutChartInstance.destroy();

            workoutChartInstance = new Chart(document.getElementById('workoutProgressChart'), {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Completado %',
                        data: dataVals,
                        backgroundColor: dataVals.map((v, idx) => idx === currentWorkoutDayIdx ? '#185FA5' : '#1e293b'),
                        borderColor: dataVals.map((v, idx) => idx === currentWorkoutDayIdx ? '#3b82f6' : '#475569'),
                        borderWidth: 1.5,
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100,
                            grid: {
                                color: '#1e293b'
                            },
                            ticks: {
                                color: '#94a3b8',
                                font: { size: 9, weight: 'bold' },
                                callback: function(value) { return value + '%'; }
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            },
                            ticks: {
                                color: '#94a3b8',
                                font: { size: 10, weight: 'bold' }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return `Completado: ${context.parsed.y}%`;
                                }
                            }
                        }
                    }
                }
            });
        }

        async function runFinancialAnalysis() {
            const container = document.getElementById('finance-ai-card-content');
            container.innerHTML = `
                <div class="flex items-center gap-2 py-4 justify-center">
                    <span class="animate-spin text-indigo-400">⚡</span>
                    <span class="text-xs text-slate-400 font-bold">Asesor Financiero analizando transacciones...</span>
                </div>
            `;

            try {
                const token = localStorage.getItem('app_auth_token');
                const res = await fetch('/api/finances/analyze', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({ transactions: state.transactions })
                });

                if (!res.ok) throw new Error("Could not load financial advice.");

                const report = await res.json();
                renderFinancialReportUI(report);
            } catch (e) {
                // Rich smart calculated fallback report
                const totalIncome = state.transactions.filter(t => t.type === 'ingreso').reduce((acc, t) => acc + t.amount, 0);
                const totalExpenses = state.transactions.filter(t => t.type === 'gasto').reduce((acc, t) => acc + t.amount, 0);
                const ratio = totalIncome > 0 ? (totalExpenses / totalIncome) : 1;
                const score = Math.max(10, Math.min(100, Math.round(100 - (ratio * 80))));

                let summary = "Buen control del ledger. Tienes un balance superavitario, lo cual es óptimo para mantener tus metas deportivas y equipo de moto al día.";
                let advice = [
                    "Considera apartar un 15% fijo de tus ingresos mensuales para refacciones de la moto y desgaste mecánico.",
                    "Felicidades por mantener los gastos de ocio bajo control durante esta semana.",
                    "Optimiza tus compras de comida saludable comprando lotes a granel de avena y proteínas para reducir gastos recurrentes."
                ];

                if (score < 50) {
                    summary = "Atención: Tus gastos representan un porcentaje muy elevado de tus ingresos actuales. Se recomienda recortar gastos no esenciales de inmediato.";
                    advice = [
                        "Evalúa si puedes reducir las membresías recurrentes inactivas.",
                        "Reorganiza las salidas a comer fuera (ocio) cocinando más menús de alto rendimiento en casa.",
                        "Crea una cuenta de ahorro separada de retiro inmediato."
                    ];
                }

                renderFinancialReportUI({
                    summary,
                    savingTips: advice,
                    financialHealthScore: score
                });
            }
        }

        function renderFinancialReportUI(report) {
            const container = document.getElementById('finance-ai-card-content');
            
            let badgeColor = 'text-emerald-400 border-emerald-900 bg-emerald-950/20';
            if (report.financialHealthScore < 50) {
                badgeColor = 'text-red-400 border-red-900 bg-red-950/20';
            } else if (report.financialHealthScore < 75) {
                badgeColor = 'text-amber-400 border-amber-900 bg-amber-950/20';
            }

            container.innerHTML = `
                <div class="space-y-3.5">
                    <div class="flex items-center justify-between border-b border-slate-800 pb-2.5">
                        <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Índice de Salud Financiera:</span>
                        <span class="font-mono font-black border px-2.5 py-0.5 rounded text-xs ${badgeColor}">${report.financialHealthScore} / 100</span>
                    </div>
                    <div class="p-3 bg-slate-950/80 rounded-xl border border-slate-850 text-slate-300 leading-relaxed text-[11px]">
                        ${report.summary}
                    </div>
                    <div class="space-y-1.5">
                        <span class="text-[9px] font-black uppercase tracking-widest text-indigo-400 block">Recomendaciones Estratégicas:</span>
                        <ul class="space-y-1 text-[11px] text-slate-350">
                            ${report.savingTips.map(tip => `
                                <li class="flex items-start gap-1.5 p-1.5 bg-slate-950 rounded-lg border border-slate-850/45">
                                    <span class="text-indigo-400 shrink-0">•</span>
                                    <span>${tip}</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }


        // ==========================================
        // TOAST NOTIFICATIONS DRAWER
        // ==========================================

        function triggerToastAlert(title, body) {
            // Simple visual log alert on main screen
            const notificationCard = document.createElement('div');
            notificationCard.className = "fixed bottom-5 right-5 z-[80] max-w-xs w-full bg-slate-900 border border-slate-800 text-white rounded-xl p-4 shadow-2xl flex items-start gap-2.5 animate-bounce";
            notificationCard.innerHTML = `
                <div class="p-1.5 bg-blue-950 text-blue-400 rounded-lg shrink-0">
                    <i data-lucide="bell" class="w-4 h-4"></i>
                </div>
                <div class="flex-1 text-xs">
                    <p class="font-bold text-white">${title}</p>
                    <p class="text-[11px] text-slate-400 leading-normal mt-0.5">${body}</p>
                </div>
                <button onclick="this.parentElement.remove()" class="text-slate-500 hover:text-white font-black">✕</button>
            `;
            document.body.appendChild(notificationCard);
            lucide.createIcons();
            
            setTimeout(() => {
                notificationCard.remove();
            }, 6000);
        }

        // ==========================================
        // SECURITY GATE SYSTEM
        // ==========================================

        function showLockScreen() {
            document.getElementById('lock-screen-container').classList.remove('hidden');
            document.getElementById('app-wrapper').classList.add('hidden');
            lucide.createIcons();
        }

        function hideLockScreen() {
            document.getElementById('lock-screen-container').classList.add('hidden');
            document.getElementById('app-wrapper').classList.remove('hidden');
            lucide.createIcons();
        }

        async function attemptUnlock() {
            const user = document.getElementById('input-lock-user').value;
            const pass = document.getElementById('input-lock-pass').value;
            const errDiv = document.getElementById('lock-error-msg');
            errDiv.classList.add('hidden');
            
            try {
                const res = await fetch('/api/auth/verify', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username: user, password: pass })
                });
                
                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.error || "Credenciales Incorrectas");
                }
                
                const data = await res.json();
                localStorage.setItem('app_auth_token', data.token);
                
                // Clear inputs
                document.getElementById('input-lock-user').value = '';
                document.getElementById('input-lock-pass').value = '';
                
                // Initialize app with correct token
                await init();
            } catch (e) {
                errDiv.innerText = `⚠️ ${e.message}`;
                errDiv.classList.remove('hidden');
                const userField = document.getElementById('input-lock-user');
                const passField = document.getElementById('input-lock-pass');
                userField.classList.add('border-red-500', 'animate-shake');
                passField.classList.add('border-red-500', 'animate-shake');
                setTimeout(() => {
                    userField.classList.remove('border-red-500', 'animate-shake');
                    passField.classList.remove('border-red-500', 'animate-shake');
                }, 500);
            }
        }

        function logoutSecure() {
            localStorage.removeItem('app_auth_token');
            showLockScreen();
            triggerToastAlert("🔒 Sesión Cerrada", "Tu acceso ha sido bloqueado con éxito.");
        }

        function updateSecurityStatusUI(enabled) {
            const badge = document.getElementById('sec-status-badge');
            const hText = document.getElementById('text-header-security');
            const hBtn = document.getElementById('btn-header-security');
            const logoutBtn = document.getElementById('btn-header-logout');

            if (enabled) {
                badge.innerText = "Activo";
                badge.className = "px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20";
                hText.innerText = "Seguridad (Activa)";
                hBtn.classList.add('text-emerald-400');
                hBtn.classList.remove('text-slate-400');
                logoutBtn.classList.remove('hidden');
            } else {
                badge.innerText = "Inactivo (Acceso Libre)";
                badge.className = "px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20";
                hText.innerText = "Configurar Credenciales";
                hBtn.classList.remove('text-emerald-400');
                hBtn.classList.add('text-slate-400');
                logoutBtn.classList.add('hidden');
            }
        }

        async function openSecurityModal() {
            document.getElementById('input-sec-new-user').value = '';
            document.getElementById('input-sec-new-pass').value = '';
            document.getElementById('input-sec-old-pass').value = '';
            document.getElementById('input-sec-change-user').value = '';
            document.getElementById('input-sec-change-pass').value = '';
            document.getElementById('sec-err').classList.add('hidden');

            try {
                const res = await fetch('/api/auth/status');
                const authStatus = await res.json();
                
                updateSecurityStatusUI(authStatus.enabled);

                if (authStatus.enabled) {
                    document.getElementById('sec-active-view').classList.remove('hidden');
                    document.getElementById('sec-inactive-view').classList.add('hidden');
                } else {
                    document.getElementById('sec-active-view').classList.add('hidden');
                    document.getElementById('sec-inactive-view').classList.remove('hidden');
                }

                document.getElementById('security-settings-modal').classList.remove('hidden');
                lucide.createIcons();
            } catch (e) {
                console.error("No se pudo cargar el estado de seguridad:", e);
            }
        }

        function closeSecurityModal() {
            document.getElementById('security-settings-modal').classList.add('hidden');
        }

        async function triggerEnableSecurity() {
            const newUser = document.getElementById('input-sec-new-user').value;
            const newPass = document.getElementById('input-sec-new-pass').value;
            const errDiv = document.getElementById('sec-err');
            const submitBtn = document.getElementById('btn-sec-enable');

            errDiv.classList.add('hidden');

            if (!newUser) {
                errDiv.innerText = "Por favor ingresa un Nickname.";
                errDiv.classList.remove('hidden');
                return;
            }

            if (newPass.length < 8) {
                errDiv.innerText = "La contraseña debe tener al menos 8 caracteres.";
                errDiv.classList.remove('hidden');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '⚡ Activando...';

            try {
                const res = await fetch('/api/auth/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'enable', new_username: newUser, new_password: newPass })
                });

                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || "No se pudo activar las credenciales.");
                }

                localStorage.setItem('app_auth_token', data.token);
                closeSecurityModal();
                triggerToastAlert("🔒 Seguridad Activada", "Tu panel ahora está protegido por credenciales de usuario.");
                await init();
            } catch (e) {
                errDiv.innerText = e.message;
                errDiv.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-lucide="shield-alert" class="w-4 h-4"></i> Activar Seguridad';
                lucide.createIcons();
            }
        }

        async function triggerDisableSecurity() {
            const oldPass = document.getElementById('input-sec-old-pass').value;
            const errDiv = document.getElementById('sec-err');
            const submitBtn = document.getElementById('btn-sec-disable');

            errDiv.classList.add('hidden');

            if (!oldPass) {
                errDiv.innerText = "Por favor ingresa tu contraseña actual para verificar.";
                errDiv.classList.remove('hidden');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Desactivando...';

            try {
                const res = await fetch('/api/auth/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'disable', old_password: oldPass })
                });

                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || "No se pudo desactivar la seguridad.");
                }

                localStorage.removeItem('app_auth_token');
                closeSecurityModal();
                triggerToastAlert("🔓 Seguridad Desactivada", "Se ha removido la contraseña de protección.");
                await init();
            } catch (e) {
                errDiv.innerText = e.message;
                errDiv.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-lucide="shield-off" class="w-3.5 h-3.5"></i> Desactivar';
                lucide.createIcons();
            }
        }

        async function triggerChangeCredentials() {
            const oldPass = document.getElementById('input-sec-old-pass').value;
            const changeUser = document.getElementById('input-sec-change-user').value;
            const changePass = document.getElementById('input-sec-change-pass').value;
            const errDiv = document.getElementById('sec-err');
            const submitBtn = document.getElementById('btn-sec-change');

            errDiv.classList.add('hidden');

            if (!oldPass) {
                errDiv.innerText = "Por favor ingresa tu contraseña actual.";
                errDiv.classList.remove('hidden');
                return;
            }

            if (changePass && changePass.length < 8) {
                errDiv.innerText = "La nueva contraseña debe tener al menos 8 caracteres.";
                errDiv.classList.remove('hidden');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = 'Guardando...';

            try {
                const res = await fetch('/api/auth/config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        action: 'change', 
                        old_password: oldPass, 
                        new_username: changeUser || undefined, 
                        new_password: changePass || undefined 
                    })
                });

                const data = await res.json();
                if (!res.ok) {
                    throw new Error(data.error || "No se pudo actualizar las credenciales.");
                }

                localStorage.setItem('app_auth_token', data.token);
                closeSecurityModal();
                triggerToastAlert("🔒 Credenciales Actualizadas", "Tus datos de acceso han sido actualizados con éxito.");
                await init();
            } catch (e) {
                errDiv.innerText = e.message;
                errDiv.classList.remove('hidden');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i data-lucide="key-round" class="w-3.5 h-3.5"></i> Guardar Cambios';
                lucide.createIcons();
            }
        }

        // Boot system
        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

class WorkoutAppHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def check_auth(self):
        data = load_data()
        if not data.get("security_enabled", False):
            return True
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False
        token = auth_header.split('Bearer ')[1].strip()
        username = data.get("security_username", DEFAULT_USER)
        password_hash = data.get("security_password_hash", DEFAULT_PASS_HASH)
        expected_token = generate_auth_token(username, password_hash)
        return token == expected_token

    def do_HEAD(self):
        if self.path in ['/assets/logo.png', '/favicon.ico']:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            if os.path.exists(logo_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.send_header('Content-Length', str(os.path.getsize(logo_path)))
                self.end_headers()
                return
            else:
                self.send_response(404)
                self.end_headers()
                return
        elif self.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            return
        super().do_HEAD()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode('utf-8'))
        elif self.path == '/manifest.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            manifest = {
                "name": "Vitalise - Alto Rendimiento",
                "short_name": "Vitalise",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#090d16",
                "theme_color": "#185FA5",
                "icons": [
                    {
                        "src": "/assets/logo.png",
                        "sizes": "192x192",
                        "type": "image/png"
                    },
                    {
                        "src": "/assets/logo.png",
                        "sizes": "512x512",
                        "type": "image/png"
                    }
                ]
            }
            self.wfile.write(json.dumps(manifest, ensure_ascii=False).encode('utf-8'))
            return
        elif self.path in ['/assets/logo.png', '/favicon.ico']:
            logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')
            if os.path.exists(logo_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
                self.end_headers()
                with open(logo_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == '/api/auth/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = load_data()
            self.wfile.write(json.dumps({
                "enabled": data.get("security_enabled", False),
                "username": data.get("security_username", DEFAULT_USER)
            }).encode('utf-8'))
        elif self.path == '/api/data':
            if not self.check_auth():
                self.send_response(401)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            data = load_data()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length) if content_length > 0 else b''
        
        # Public auth endpoints:
        if self.path == '/api/auth/verify':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                username = payload.get("username", "")
                password = payload.get("password", "")
                data = load_data()
                stored_user = data.get("security_username", DEFAULT_USER)
                stored_hash = data.get("security_password_hash", DEFAULT_PASS_HASH)
                
                if username == stored_user and verify_password(stored_hash, password):
                    token = generate_auth_token(stored_user, stored_hash)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "token": token}).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Usuario o contraseña incorrectos"}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        elif self.path == '/api/auth/config':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                action = payload.get("action") # "enable", "disable", "change"
                data = load_data()
                is_currently_enabled = data.get("security_enabled", False)
                
                if is_currently_enabled:
                    old_password = payload.get("old_password", "")
                    stored_hash = data.get("security_password_hash", DEFAULT_PASS_HASH)
                    if not verify_password(stored_hash, old_password):
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "La contraseña actual es incorrecta"}).encode('utf-8'))
                        return
                
                if action == "enable":
                    new_user = payload.get("new_username", "admin")
                    new_password = payload.get("new_password", "")
                    if len(new_password) < 8:
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({"error": "La contraseña debe tener al menos 8 caracteres"}).encode('utf-8'))
                        return
                    hashed_new = hash_password(new_password)
                    data["security_enabled"] = True
                    data["security_username"] = new_user
                    data["security_password_hash"] = hashed_new
                    save_data(data)
                    token = generate_auth_token(new_user, hashed_new)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "token": token}).encode('utf-8'))
                    return
                
                elif action == "disable":
                    data["security_enabled"] = False
                    save_data(data)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True}).encode('utf-8'))
                    return
                
                elif action == "change":
                    new_user = payload.get("new_username")
                    new_password = payload.get("new_password")
                    
                    if not new_user:
                        new_user = data.get("security_username", DEFAULT_USER)
                    
                    if new_password:
                        if len(new_password) < 8:
                            self.send_response(400)
                            self.send_header('Content-Type', 'application/json')
                            self.end_headers()
                            self.wfile.write(json.dumps({"error": "La nueva contraseña debe tener al menos 8 caracteres"}).encode('utf-8'))
                            return
                        hashed_new = hash_password(new_password)
                    else:
                        hashed_new = data.get("security_password_hash", DEFAULT_PASS_HASH)
                        
                    data["security_username"] = new_user
                    data["security_password_hash"] = hashed_new
                    save_data(data)
                    token = generate_auth_token(new_user, hashed_new)
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": True, "token": token}).encode('utf-8'))
                    return
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
            return

        # Secure endpoints:
        if not self.check_auth():
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Unauthorized"}).encode('utf-8'))
            return

        if self.path == '/api/data':
            try:
                data = json.loads(post_data.decode('utf-8'))
                current_stored_data = load_data()
                data["security_password_hash"] = current_stored_data.get("security_password_hash", DEFAULT_PASS_HASH)
                data["security_username"] = current_stored_data.get("security_username", DEFAULT_USER)
                data["security_enabled"] = current_stored_data.get("security_enabled", True)
                save_data(data)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
            except Exception as e:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
        elif self.path == '/api/meals/generate':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                pref = payload.get("dietPreference", "Omnívoro")
                goal = payload.get("objective", "Mantener peso saludable")
                cal = payload.get("calorieGoal", 2100)
                
                prompt = f"""Genera un plan alimenticio de un día con 4 comidas (desayuno, almuerzo, merienda, cena) adaptado para un ciclista de Enduro / deportista.
                Preferencia de dieta: {pref}
                Objetivo de calorías diario: {cal} kcal
                Objetivo físico: {goal}

                Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura exacta:
                {{
                  "desayuno": {{ "name": "Nombre detallado", "calories": 350, "protein": 15, "carbs": 40, "fat": 10, "ingredients": ["ingrediente 1", "ingrediente 2"], "recipeInstructions": "Paso 1... Paso 2..." }},
                  "almuerzo": {{ "name": "Nombre detallado", "calories": 600, "protein": 40, "carbs": 60, "fat": 15, "ingredients": [...], "recipeInstructions": "..." }},
                  "merienda": {{ "name": "Nombre detallado", "calories": 250, "protein": 15, "carbs": 25, "fat": 8, "ingredients": [...], "recipeInstructions": "..." }},
                  "cena": {{ "name": "Nombre detallado", "calories": 500, "protein": 35, "carbs": 30, "fat": 12, "ingredients": [...], "recipeInstructions": "..." }}
                }}
                No incluyas explicaciones, etiquetas markdown, ni texto adicional."""
                
                res_obj = call_gemini_api(prompt)
                if not res_obj:
                    raise ValueError("Failed to generate with Gemini")
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res_obj).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
                
        elif self.path == '/api/finances/analyze':
            try:
                payload = json.loads(post_data.decode('utf-8'))
                txs = payload.get("transactions", [])
                
                prompt = f"""Analiza las siguientes transacciones financieras de mi cuenta y provee un reporte estratégico e inteligente:
                {json.dumps(txs, indent=2)}

                Debes responder ÚNICAMENTE con un objeto JSON válido con la siguiente estructura exacta:
                {{
                  "summary": "Resumen ejecutivo del análisis financiero de las transacciones, destacando la relación ingreso/gasto y oportunidades.",
                  "savingTips": [
                    "Consejo de ahorro específico 1",
                    "Consejo de ahorro específico 2",
                    "Consejo de ahorro específico 3"
                  ],
                  "financialHealthScore": 85
                }}
                Asegúrate de calcular el score de salud del 0 al 100 de forma realista basándote en ingresos vs gastos.
                No incluyas explicaciones, etiquetas markdown, ni texto adicional."""
                
                res_obj = call_gemini_api(prompt)
                if not res_obj:
                    raise ValueError("Failed to analyze with Gemini")
                    
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(res_obj).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

def run_server():
    server_address = ('0.0.0.0', PORT)
    httpd = HTTPServer(server_address, WorkoutAppHandler)
    print(f"Python single script server running on port {PORT}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
