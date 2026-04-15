import streamlit as st
import sqlite3
import hashlib
import time

# ================= CONFIG =================
st.set_page_config(page_title="TELC B2 SaaS", layout="wide")

# ================= DATABASE =================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS progress (
    username TEXT,
    progress INTEGER
)
""")

conn.commit()

# ================= UTILS =================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    try:
        c.execute("INSERT INTO users VALUES (?,?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except:
        return False

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

def save_progress(username, progress):
    c.execute("DELETE FROM progress WHERE username=?", (username,))
    c.execute("INSERT INTO progress VALUES (?,?)", (username, progress))
    conn.commit()

def get_progress(username):
    c.execute("SELECT progress FROM progress WHERE username=?", (username,))
    res = c.fetchone()
    return res[0] if res else 0

# ================= STATE =================
if "user" not in st.session_state:
    st.session_state.user = None

if "page" not in st.session_state:
    st.session_state.page = "login"

if "selected" not in st.session_state:
    st.session_state.selected = None

if "progress" not in st.session_state:
    st.session_state.progress = 0

# ================= AUTH =================
def login_page():
    st.title("🔐 TELC B2 Simulator")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u, p):
                st.session_state.user = u
                st.session_state.page = "app"
                st.session_state.progress = get_progress(u)
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Wrong credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create Account"):
            if create_user(u, p):
                st.success("Account created")
            else:
                st.error("User exists")

# ================= DATA =================
sections = {
    "Lesen": ["Umwelt", "Impfung", "Kinderhandy"],
    "Hören": ["Lufthansa", "Erdbeben"],
    "Schreiben": ["Beschwerdebrief"],
    "Sprechen": ["Lieblingsland"]
}

# ================= MAIN APP =================
def app():
    st.sidebar.title(f"👤 {st.session_state.user}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "login"
        st.rerun()

    st.sidebar.progress(st.session_state.progress / 100)

    page = st.sidebar.radio("Navigate", ["Catalog", "Exercise"])

    if page == "Catalog":
        st.title("📚 Exercises")

        for sec, items in sections.items():
            st.subheader(sec)
            for item in items:
                if st.button(f"Start {item}"):
                    st.session_state.selected = item
                    st.session_state.page = "exercise"
                    st.rerun()

    if st.session_state.page == "exercise":
        exercise_page()

# ================= EXERCISE =================
def exercise_page():
    st.title(f"📝 {st.session_state.selected}")

    if st.button("⬅ Back"):
        st.session_state.page = "app"
        st.rerun()

    # Example MCQ
    answer = st.radio("Choose:", ["A", "B", "C"])

    if st.button("Submit"):
        if answer == "A":
            st.success("Correct")
            st.session_state.progress += 10
        else:
            st.error("Wrong")

        save_progress(st.session_state.user, st.session_state.progress)

    # Writing
    text = st.text_area("Write here")

    if st.button("Save Writing"):
        st.success("Saved")
        st.session_state.progress += 5
        save_progress(st.session_state.user, st.session_state.progress)

# ================= ROUTER =================
if st.session_state.page == "login":
    login_page()
else:
    app()