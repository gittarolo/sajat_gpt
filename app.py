import streamlit as st
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from github import Github
import json
import hashlib
from datetime import datetime

# --- BEÁLLÍTÁSOK ÉS TITKOK BETÖLTÉSE ---
# Vesszővel elválasztott kulcsok beolvasása és tisztítása
api_keys = [k.strip() for k in st.secrets["GEMINI_API_KEYS"].split(",") if k.strip()]

# Csatlakozás a privát GitHub repóhoz
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
            users_data = {}  # Ha még nincs adatbázis, létrehozzuk a memóriában

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
                st.rerun()
            else:
                st.sidebar.error("Hibás felhasználónév vagy jelszó!")


# --- GEMINI AI ROTÁCIÓS FÜGGVÉNY ---
def get_gemini_response(prompt):
    # A Streamlit üzenetek átalakítása a Gemini formátumára
    history = [
        {"role": "user" if msg["role"] == "user" else "model", "parts": [msg["content"]]}
        for msg in st.session_state.messages[:-1]  # Az utolsót (a mostanit) nem tesszük bele a history-ba
    ]

    for _ in range(len(api_keys)):
        current_key = api_keys[st.session_state.key_index]
        genai.configure(api_key=current_key)
        model = genai.GenerativeModel("gemini-1.5-flash")  # Legjobb ingyenes sebesség/minőség arány

        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt)
            return response.text
        except ResourceExhausted:
            # Ha kimerült a kvóta, ugrunk a következő kulcsra
            st.session_state.key_index = (st.session_state.key_index + 1) % len(api_keys)
            st.warning(f"Kvóta kimerült a jelenlegi kulcson, automatikus váltás a következőre...")
        except Exception as e:
            return f"Hiba történt a generálás során: {e}"

    return "Sajnos az összes megadott API kulcsod kvótája elfogyott mára."


# --- FŐ ALKALMAZÁS LOGIKA ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "key_index" not in st.session_state:
    st.session_state.key_index = 0

if not st.session_state.logged_in:
    auth_user()
    st.info("Kérlek lépj be vagy regisztrálj a chateléshez.")
else:
    # Kijelentkezés és Mentés gombok a sidebarban
    st.sidebar.title(f"Üdv, {st.session_state.username}!")

    if st.sidebar.button("Kijelentkezés"):
        st.session_state.logged_in = False
        st.session_state.messages = []
        st.rerun()

    if st.sidebar.button("Beszélgetés mentése a GitHubra"):
        if "messages" in st.session_state and len(st.session_state.messages) > 0:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"history/{st.session_state.username}_{timestamp}.json"
            save_to_github(filename, st.session_state.messages, f"Chat mentése: {timestamp}")
            st.sidebar.success("Beszélgetés sikeresen elmentve!")
        else:
            st.sidebar.warning("Nincs mit menteni.")

    # --- CHAT FELÜLET ---
    st.title("Felhős AI Asszisztens")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Írj valamit..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Gondolkodom..."):
                response_text = get_gemini_response(prompt)
            st.markdown(response_text)

        st.session_state.messages.append({"role": "assistant", "content": response_text})