import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from github import Github
import json
import hashlib
from datetime import datetime

# --- BEÁLLÍTÁSOK ÉS TITKOK BETÖLTÉSE ---
api_keys = [k.strip() for k in st.secrets["GEMINI_API_KEYS"].split(",") if k.strip()]
g = Github(st.secrets["GITHUB_PAT"])
repo = g.get_user().get_repo(st.secrets["GITHUB_REPO_NAME"])

# --- GITHUB ADATBÁZIS FÜGGVÉNYEK ---
def get_github_file(filepath):
    try:
        content = repo.get_contents(filepath)
        return json.loads(content.decoded_content.decode('utf-8')), content.sha
    except Exception:
        return None, None

def save_to_github(filepath, data, commit_message, sha=None):
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    if sha:
        repo.update_file(filepath, commit_message, json_data, sha)
    else:
        repo.create_file(filepath, commit_message, json_data)

def auto_save_chat():
    if st.session_state.logged_in and st.session_state.messages:
        filename = f"history/{st.session_state.username}_{st.session_state.current_chat_id}.json"
        _, sha = get_github_file(filename)
        save_to_github(filename, st.session_state.messages, "Automatikus csevegés mentés", sha)

# --- AUTENTIKÁCIÓS FÜGGVÉNYEK ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def auth_user():
    st.sidebar.title("Belépés / Regisztráció")
    menu = st.sidebar.radio("Válassz opciót:", ["Belépés", "Regisztráció"])
    username = st.sidebar.text_input("Felhasználónév")
    password = st.sidebar.text_input("Jelszó", type="password")
    
    if st.sidebar.button("Mehet"):
        if not username or not password:
            st.sidebar.error("Minden mezőt ki kell tölteni!")
            return False

        users_data, sha = get_github_file("users.json")
        if users_data is None:
            users_data = {}
            
        hashed_pw = hash_password(password)

        if menu == "Regisztráció":
            if username in users_data:
                st.sidebar.error("Ez a felhasználónév már foglalt!")
            else:
                users_data[username] = {"password": hashed_pw}
                save_to_github("users.json", users_data, f"Új regisztráció: {username}", sha)
                st.sidebar.success("Sikeres regisztráció! Most már beléphetsz.")
                
        elif menu == "Belépés":
            if username in users_data and users_data[username]["password"] == hashed_pw:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.current_chat_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                st.rerun()
            else:
                st.sidebar.error("Hibás felhasználónév vagy jelszó!")

# --- GEMINI AI MULTIMODÁLIS FÜGGVÉNY ---
def get_gemini_response(gemini_parts):
    # Előzmények felépítése (csak a szöveges tartalmat visszük át a korábbi körökből)
    history = []
    for msg in st.session_state.messages[:-1]:
        history.append({
            "role": "user" if msg["role"] == "user" else "model", 
            "parts": [msg["content"]]
        })
        
    for _ in range(len(api_keys)):
        current_key = api_keys[st.session_state.key_index]
        genai.configure(api_key=current_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(gemini_parts)
            return response.text
        except ResourceExhausted:
            st.session_state.key_index = (st.session_state.key_index + 1) % len(api_keys)
            st.warning("Kvóta kimerült, váltás a következő kulcsra...")
        except Exception as e:
            return f"Hiba történt a generálás során: {e}"
            
    return "Sajnos az összes megadott API kulcsod kvótája elfogyott mára."

# --- FŐ ALKALMAZÁS LOGIKA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "key_index" not in st.session_state:
    st.session_state.key_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.logged_in:
    auth_user()
    st.info("Kérlek lépj be vagy regisztrálj a chateléshez.")
else:
    # --- OLDALSÁV (HISTORY KEZELÉS) ---
    st.sidebar.title(f"Üdv, {st.session_state.username}!")
    
    if st.sidebar.button("➕ Új csevegés indítása"):
        st.session_state.messages = []
        st.session_state.current_chat_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        st.rerun()
        
    st.sidebar.write("---")
    st.sidebar.subheader("Mentett beszélgetéseid")
    
    # Repó fájljainak listázása a múlthoz
    user_chats = []
    try:
        contents = repo.get_contents("history")
        for f in contents:
            if f.name.startswith(st.session_state.username) and f.name.endswith(".json"):
                display_name = f.name.replace(f"{st.session_state.username}_", "").replace(".json", "").replace("_", " ")
                user_chats.append({"display": display_name, "filename": f.name, "sha": f.sha, "obj": f})
    except Exception:
        pass

    if user_chats:
        chat_options = {c["display"]: c for c in user_chats}
        selected_display = st.sidebar.selectbox("Válassz ki egy csevegést:", list(chat_options.keys()))
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.sidebar.button("📂 Betöltés", use_container_width=True):
                chosen = chat_options[selected_display]
                chat_data, _ = get_github_file(f"history/{chosen['filename']}")
                if chat_data:
                    st.session_state.messages = chat_data
                    st.session_state.current_chat_id = chosen['filename'].replace(f"{st.session_state.username}_", "").replace(".json", "")
                    st.rerun()
        with col2:
            if st.sidebar.button("🗑️ Törlés", use_container_width=True):
                chosen = chat_options[selected_display]
                repo.delete_file(chosen['obj'].path, f"Csevegés törlése: {chosen['filename']}", chosen['sha'])
                
                # Ha pont a megnyitottat törölte ki, ürítsük az ablakot
                if chosen['filename'] == f"{st.session_state.username}_{st.session_state.current_chat_id}.json":
                    st.session_state.messages = []
                    st.session_state.current_chat_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                st.sidebar.success("Törölve!")
                st.rerun()
    else:
        st.sidebar.info("Még nincs mentett beszélgetésed.")

    st.sidebar.write("---")
    if st.sidebar.button("Kijelentkezés"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    # --- CHAT FELÜLET ---
    st.title("Felhős AI Asszisztens")

    # Üzenetek kirajzolása
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Fájl feltöltő modul
    uploaded_file = st.file_uploader("Fájl csatolása (Kép, PDF, TXT, PY, CSV)", type=["png", "jpg", "jpeg", "pdf", "txt", "py", "csv"])

    if prompt := st.chat_input("Írj egy üzenetet..."):
        display_prompt = prompt
        gemini_parts = [prompt]
        
        # Ha van feltöltött fájl, feldolgozzuk
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            display_prompt = f"📎 *[{uploaded_file.name}]* feltöltve.\n\n{prompt}"
            
            # Ha sima kód vagy szöveg, beolvassuk stringként (így stabilabb és nem hízik a Git adatbázis)
            if uploaded_file.name.endswith(('.txt', '.py', '.csv', '.json', '.html', '.css')):
                try:
                    text_content = file_bytes.decode('utf-8')
                    gemini_parts = [prompt + f"\n\n--- CSATOLT FÁJL TARTALMA ({uploaded_file.name}) ---\n{text_content}"]
                except Exception:
                    gemini_parts = [prompt + "\n\n(A szöveges fájl kódolása nem olvasható.)"]
            else:
                # Kép vagy PDF esetén nyers bájtokként küldjük az API-nak
                gemini_parts = [
                    prompt,
                    {"mime_type": uploaded_file.type, "data": file_bytes}
                ]
        
        # Felhasználói üzenet hozzáadása és kirajzolása
        st.session_state.messages.append({"role": "user", "content": display_prompt})
        with st.chat_message("user"):
            st.markdown(display_prompt)

        # AI válasz generálása
        with st.chat_message("assistant"):
            with st.spinner("Gondolkodom..."):
                response_text = get_gemini_response(gemini_parts)
            st.markdown(response_text)
            
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # AUTOMATIKUS MENTÉS A GITHUBRA
        auto_save_chat()