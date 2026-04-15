import streamlit as st
import time
import re
from datetime import datetime

st.set_page_config(
    page_title="TELC B2 Simulator",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Data extracted from the public page structure
# ----------------------------
EXAM_STRUCTURE = {
    "Lesen": {
        "label": "Reading",
        "minutes": 60,
        "parts": [
            {
                "name": "Lesen Teil 1",
                "kind": "reading",
                "minutes": 20,
                "titles": [
                    "Umwelt", "Impfung", "Kinderhandy", "Drogen", "Tanzkurs", "Limonade",
                    "Grundschule", "Insekten", "Österreich", "Jugend forscht", "Sport ist Gesund",
                    "Inseln", "In den Alpen", "In den Alpen 2", "Kartoffel", "Bilder", "Licht",
                    "Spielen", "Programmieren", "Trampoline", "Benzin", "Kaffee", "Bonbons",
                    "Geld", "Auf dem Weg", "Schlafzug 1", "Schlafzug 2", "Keine Zeit",
                    "Licht (NEUE)", "Russische Frau", "Farben", "Löwen اسود"
                ],
            },
            {
                "name": "Lesen Teil 2",
                "kind": "reading",
                "minutes": 20,
                "titles": [
                    "Puppenmacher", "Österreich", "Parkuhren", "Traumfrau", "Kaufentscheidungen",
                    "Millionäre", "Gehirn", "Verpackungen", "Kreditkarten", "Krista die Kühe",
                    "Ernährung", "Kaffee", "Kaffee 2", "Großraumbüros", "Familie", "Babys",
                    "Karneval von Unna", "Mehrsprachige", "Gesundes Essen", "Dienstmädchen",
                    "Reitergruppe", "Brigitte Vollmer", "Nachtzug", "Die ganze Welt",
                    "Kellner", "Weniger Euro"
                ],
            },
            {
                "name": "Lesen Teil 3",
                "kind": "reading",
                "minutes": 20,
                "titles": [
                    "Fernsehprogramm", "Sport ist Gesund", "Kellner", "Schwägerin",
                    "Schwägerin(das)", "Dokumentarfilm", "Wein und Insekten", "Grundschule",
                    "Kein Zeit", "Kein Zeit 2", "Sport", "Gärten", "Apotheker", "Urlaub",
                    "Anwalt", "Anwalt 2", "Der Hund", "Musik", "Haushalt", "Musikinstrumente",
                    "Schiffsreise", "Ausflug", "Schwägerin Gesund", "Au-pair-Mädchen",
                    "Tierdokumentationen", "Schlafzug", "Bonbons", "Schränke",
                    "schnelle Wasserfahrzeuge - اعلانات الألوان"
                ],
            },
        ],
    },
    "Sprachbausteine": {
        "label": "Grammar",
        "minutes": 40,
        "parts": [
            {
                "name": "Sprachbausteine Teil 1",
                "kind": "grammar",
                "minutes": 20,
                "titles": [
                    "Herr Martini", "Judith oder Lina", "Igor", "Maria", "Ida", "Andrea",
                    "Andrea 2", "Autorinnen und Autoren", "Geissler oder Dippold", "Herr Dr. Dobromil",
                    "Frau Szabo", "Frau Szabo 2", "Corinna", "Justus oder Juhannas",
                    "Justus oder Juhannas 2", "Ferdinand, Phillip, Christopher", "Liebe Paola",
                    "Liebe Julian", "Liebe Lara", "Lieber David", "Liebe Maria, Lieber Timur",
                    "Liebe Vanessa", "Frau Goronsksa", "Liebe Karin", "Liebe Jutta",
                    "Liebe Meike", "Liebe Leon", "Liebe Clara", "Lieber Thomas",
                    "Dr. Moosberger", "Lina & Florian", "Liebe Agnieszka", "Jens",
                    "Frau Melchior"
                ],
            },
            {
                "name": "Sprachbausteine Teil 2",
                "kind": "grammar",
                "minutes": 20,
                "titles": [
                    "Theater für Kinder und Jugendliche", "Im Restaurant",
                    "Das Fahrrad: ernsthafte Konkurrenz fürs Auto?", "Haustieren",
                    "Liebesgrüße aus der Kühltruhe", "Braunbären", "Ausbildung",
                    "Skipiste", "Jugend diskutiert", "Manipulierte Bilder", "Haustieren",
                    "Schwarzarbeit", "Handschrift", "Schulweg", "Höflichkeit",
                    "Obst und Gemüse", "TV-Bilder", "Freund des Menschen", "BIO",
                    "Erfolg", "Deutschland", "Joggen", "Maßgeschneidert", "Der Hund",
                    "Online—Sprachkurse", "Fische", "Man(n) kocht selbst", "Schönschrift",
                    "Kaffee und Kuchen", "Städte vor dem Infarkt"
                ],
            },
        ],
    },
    "Hören": {
        "label": "Listening",
        "minutes": 45,
        "parts": [
            {
                "name": "Hören Teil 1",
                "kind": "listening",
                "minutes": 15,
                "titles": [
                    "Lufthansa", "Erdbeben", "Bierkonsum", "Schiff", "Vögel", "Europäischen",
                    "Wetter", "Nicht sicher", "Die Stadt Friedrichsberg", "Frau Jürgens",
                    "Die Wahlbeteiligung", "In den Alpen", "In den Alpen 2", "Insel Bali",
                    "Die Fluggeselschaft", "Der Bau", "50-Euro", "Das Schladminger"
                ],
            },
            {
                "name": "Hören Teil 2",
                "kind": "listening",
                "minutes": 15,
                "titles": ["Teil 2 – add your licensed audio and questions here"],
            },
            {
                "name": "Hören Teil 3",
                "kind": "listening",
                "minutes": 15,
                "titles": ["Teil 3 – add your licensed audio and questions here"],
            },
        ],
    },
    "Schreiben": {
        "label": "Writing",
        "minutes": 30,
        "parts": [
            {
                "name": "Beschwerdebrief",
                "kind": "writing",
                "minutes": 30,
                "min_words": 150,
                "titles": [
                    "Faharradtour", "Staubsaugroboter", "Wohnen und Zeit", "Autovermitung",
                    "Freizeitverein", "Engagement", "Kursbeschreibung", "Hotel", "Schmelzkäse",
                    "Renovierungskurs", "Naturmuseum", "Appartement", "Backstage Musical",
                    "Meine Kiste", "Apps", "Kultur", "Reisburo", "Schlaflos", "Kino sonnental",
                    "Fotobuch", "Kosmetik-Shop", "Informatik-Shop", "TIKKI TAKKA", "Partyservice"
                ],
            }
        ],
    },
    "Sprechen": {
        "label": "Speaking",
        "minutes": 15,
        "parts": [
            {
                "name": "Teil 1",
                "kind": "speaking",
                "minutes": 5,
                "titles": ["Presentation topics from the linked PDF"],
            },
            {
                "name": "Teil 2 + 3",
                "kind": "speaking",
                "minutes": 10,
                "titles": ["Interactive speaking topics"],
            },
            {
                "name": "Struktur 2 + 3",
                "kind": "speaking",
                "minutes": 10,
                "titles": ["Question / answer structure cards"],
            },
        ],
    },
}

SECTION_ORDER = ["Lesen", "Sprachbausteine", "Hören", "Schreiben", "Sprechen"]

# ----------------------------
# Helpers
# ----------------------------
def build_catalog():
    catalog = []
    for section_key in SECTION_ORDER:
        section = EXAM_STRUCTURE[section_key]
        for p_index, part in enumerate(section["parts"], start=1):
            for t_index, title in enumerate(part["titles"], start=1):
                catalog.append({
                    "id": f"{section_key.lower()}-{p_index}-{t_index}",
                    "section": section_key,
                    "section_label": section["label"],
                    "part": part["name"],
                    "kind": part["kind"],
                    "title": title,
                    "minutes": part.get("minutes", 0),
                    "min_words": part.get("min_words"),
                })
    return catalog

CATALOG = build_catalog()

def init_state():
    defaults = {
        "section": "Lesen",
        "search": "",
        "selected_id": None,
        "progress": 0,
        "started_at": time.time(),
        "exam_minutes": 90,
        "writing_texts": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def css():
    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; }
        div[data-testid="stMetric"] {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.08);
            padding: 12px 14px;
            border-radius: 16px;
        }
        .card {
            background: rgba(17,26,49,0.82);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 20px;
            padding: 16px 18px;
            margin-bottom: 12px;
        }
        .soft {
            color: #a9b3d4;
        }
        .badge {
            display:inline-block;
            padding:6px 10px;
            border-radius:999px;
            background: rgba(124,140,255,0.12);
            border: 1px solid rgba(124,140,255,0.24);
            font-size: 12px;
            font-weight: 700;
        }
        .title {
            font-size: 2rem;
            font-weight: 800;
            line-height: 1.05;
            margin-bottom: 0.35rem;
        }
        .subtle {
            color: #a9b3d4;
            line-height: 1.6;
        }
        .divider {
            margin: 1rem 0;
            border-top: 1px solid rgba(255,255,255,0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

def pretty_timer(seconds):
    seconds = max(0, int(seconds))
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def elapsed_seconds():
    return int(time.time() - st.session_state.started_at)

def exam_remaining():
    total = st.session_state.exam_minutes * 60
    return total - elapsed_seconds()

def section_items(section):
    return [x for x in CATALOG if x["section"] == section]

def filtered_items(section, query):
    items = section_items(section)
    if not query:
        return items
    q = query.lower().strip()
    return [
        x for x in items
        if q in x["title"].lower()
        or q in x["part"].lower()
        or q in x["kind"].lower()
    ]

def item_by_id(item_id):
    for x in CATALOG:
        if x["id"] == item_id:
            return x
    return None

def choose_first_writing():
    for x in CATALOG:
        if x["kind"] == "writing":
            return x
    return None

def progress_update(delta):
    st.session_state.progress = max(0, min(100, st.session_state.progress + delta))

def render_header():
    remaining = exam_remaining()
    col1, col2, col3, col4 = st.columns([3.2, 1, 1, 1])
    with col1:
        st.markdown(
            """
            <div class="title">TELC Exam Simulator</div>
            <div class="subtle">
            Modern Streamlit practice platform built from the visible public catalog of the linked page.
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.metric("Time left", pretty_timer(remaining))
    with col3:
        st.metric("Progress", f"{st.session_state.progress}%")
    with col4:
        st.metric("Catalog", f"{len(CATALOG)} items")

def render_sidebar():
    st.sidebar.markdown("## Simulator controls")
    st.sidebar.caption("The source page is labeled B1, while this app is branded as a B2-style simulator shell.")

    st.session_state.section = st.sidebar.selectbox(
        "Section",
        SECTION_ORDER,
        index=SECTION_ORDER.index(st.session_state.section),
    )
    st.session_state.search = st.sidebar.text_input(
        "Search titles",
        value=st.session_state.search,
        placeholder="Type a title or part name...",
    )

    st.session_state.exam_minutes = st.sidebar.slider(
        "Exam duration",
        min_value=30,
        max_value=180,
        value=st.session_state.exam_minutes,
        step=5,
    )

    if st.sidebar.button("Restart timer"):
        st.session_state.started_at = time.time()

    if st.sidebar.button("Reset progress"):
        st.session_state.progress = 0

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Exam overview")
    for sec in SECTION_ORDER:
        total = len(section_items(sec))
        st.sidebar.write(f"• {sec}: {total} items")

def render_overview():
    sec = EXAM_STRUCTURE[st.session_state.section]
    items = filtered_items(st.session_state.section, st.session_state.search)

    st.markdown(
        f"""
        <div class="card">
            <div class="badge">{st.session_state.section} • {sec['label']}</div>
            <h2 style="margin:10px 0 6px 0;">{st.session_state.section}</h2>
            <div class="subtle">
                Open any exercise title to practice it in a clean exam-like shell.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not items:
        st.info("No items matched your search.")
        return

    for part in sec["parts"]:
        part_items = [x for x in items if x["part"] == part["name"]]
        if not part_items:
            continue

        with st.expander(f"{part['name']}  •  {len(part_items)} items", expanded=True):
            cols = st.columns(2)
            for idx, item in enumerate(part_items):
                with cols[idx % 2]:
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="badge">{item['kind'].title()}</div>
                            <h4 style="margin:10px 0 6px 0;">{item['title']}</h4>
                            <div class="subtle">
                                {item['section_label']} • {item['part']}
                                {" • " + str(item['minutes']) + " min" if item['minutes'] else ""}
                                {" • min " + str(item['min_words']) + " words" if item.get('min_words') else ""}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    if st.button("Open exercise", key=f"open_{item['id']}"):
                        st.session_state.selected_id = item["id"]
                        st.rerun()

def placeholder_mcq(title, seed_key):
    # Deterministic, exam-like practice shell without reproducing the proprietary text.
    choices = [
        "A", "B", "C", "D"
    ]
    q1 = f"What is the best next step for the exercise titled '{title}'?"
    q2 = "Which strategy is most useful here?"
    q3 = "What should you focus on first?"
    q4 = "How do you manage the time?"
    q5 = "Which answer usually fits a formal exam task?"

    questions = [
        (q1, ["Read the title carefully", "Skip all tasks", "Answer randomly", "Only check spelling"], 0),
        (q2, ["Find keywords", "Ignore the text", "Wait for luck", "Use a calculator"], 0),
        (q3, ["Task instructions", "Decorations", "Music", "Ads"], 0),
        (q4, ["Move fast but stay accurate", "Spend all time on one item", "Leave early", "Guess every answer"], 0),
        (q5, ["Clear and formal", "Messy and short", "Off-topic", "Unfinished"], 0),
    ]

    score = 0
    for i, (question, options, answer) in enumerate(questions):
        st.markdown(f"**{i+1}. {question}**")
        selected = st.radio(
            label="",
            options=options,
            key=f"{seed_key}_q{i}",
            horizontal=False,
            index=None,
            label_visibility="collapsed",
        )
        if selected is not None and st.button(f"Check {i+1}", key=f"{seed_key}_check_{i}"):
            if options.index(selected) == answer:
                st.success("Correct.")
                score += 1
                progress_update(2)
            else:
                st.error("Try again.")
    if st.button("Submit practice set", key=f"{seed_key}_submit"):
        st.success("Practice set submitted.")
        progress_update(8)
        st.write(f"Score: {score}/{len(questions)}")

def render_generic_exercise(item):
    st.markdown(
        f"""
        <div class="card">
            <div class="badge">{item['kind'].title()}</div>
            <h2 style="margin:10px 0 6px 0;">{item['title']}</h2>
            <div class="subtle">
                {item['section']} • {item['part']}{" • " + str(item['minutes']) + " min" if item['minutes'] else ""}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "This is an exam shell built from the visible public catalog. "
        "Drop in licensed content or your own rewritten questions here."
    )

    left, right = st.columns([1.2, 0.8])
    with left:
        placeholder_mcq(item["title"], item["id"])
    with right:
        st.markdown("### What this slot represents")
        st.write("Use this area for the original task, a licensed replacement, or your own practice content.")
        st.markdown("### Quick notes")
        note = st.text_area("Notes", key=f"notes_{item['id']}", height=180)
        if st.button("Save notes", key=f"save_notes_{item['id']}"):
            st.success("Saved in this session.")
            progress_update(1)

def render_writing_exercise(item):
    st.markdown(
        f"""
        <div class="card">
            <div class="badge">Writing</div>
            <h2 style="margin:10px 0 6px 0;">{item['title']}</h2>
            <div class="subtle">30 minutes • at least 150 words</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "The public page shows a complaint-letter writing task with a 30-minute limit and a 150-word minimum. "
        "This app uses that structure, while the prompt below is a safe paraphrase."
    )

    st.markdown("### Task brief")
    st.write(
        "Write a formal complaint letter after taking part in a cycling tour that did not meet your expectations. "
        "Include greeting, subject line, detailed problems, what went well, and a clear closing."
    )

    default_text = st.session_state.writing_texts.get(item["id"], "")
    text = st.text_area(
        "Your text",
        value=default_text,
        height=320,
        placeholder="Start your complaint letter here...",
        key=f"writing_box_{item['id']}",
    )

    words = len(re.findall(r"\S+", text.strip())) if text.strip() else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Words", words)
    c2.metric("Target", "150+")
    c3.metric("Mode", "Formal letter")

    if st.button("Save draft", key=f"save_draft_{item['id']}"):
        st.session_state.writing_texts[item["id"]] = text
        st.success("Draft saved in this session.")
        progress_update(5)

    if st.button("Clear draft", key=f"clear_draft_{item['id']}"):
        st.session_state.writing_texts[item["id"]] = ""
        st.rerun()

    st.markdown("### Checklist")
    checklist = [
        "Add sender, address, date, subject line, greeting, and closing.",
        "Describe the problem clearly and politely.",
        "State what you want to change or improve.",
        "Keep the tone formal and organized.",
    ]
    for i, point in enumerate(checklist, start=1):
        st.checkbox(point, key=f"{item['id']}_check_{i}")

def render_speaking_exercise(item):
    st.markdown(
        f"""
        <div class="card">
            <div class="badge">Speaking</div>
            <h2 style="margin:10px 0 6px 0;">{item['title']}</h2>
            <div class="subtle">Timed speaking practice</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "The public page links to a 5-page speaking PDF. This app provides a reusable speaking simulator shell "
        "with topics, timer, and note-taking."
    )

    topics = [
        "A book you like",
        "A travel experience",
        "A film or series",
        "A sport event",
        "A favorite city",
        "A useful app",
    ]
    st.markdown("### Practice topics")
    st.write("Choose one and speak for 2 minutes.")
    chosen_topic = st.selectbox("Topic", topics, key=f"topic_{item['id']}")

    notes = st.text_area("Speaking notes", height=220, key=f"speaker_notes_{item['id']}")
    cols = st.columns(3)
    if "speak_start" not in st.session_state:
        st.session_state.speak_start = None
    with cols[0]:
        if st.button("Start 2-minute timer", key=f"start_speak_{item['id']}"):
            st.session_state.speak_start = time.time()
    with cols[1]:
        if st.button("Mark completed", key=f"done_speak_{item['id']}"):
            st.success("Marked completed.")
            progress_update(4)
    with cols[2]:
        if st.button("Save notes", key=f"save_speak_{item['id']}"):
            st.success("Saved in this session.")
            progress_update(1)

    if st.session_state.speak_start is not None:
        elapsed = int(time.time() - st.session_state.speak_start)
        remaining = max(0, 120 - elapsed)
        st.progress(min(1.0, elapsed / 120))
        st.write(f"Time left: {pretty_timer(remaining)}")
        if remaining == 0:
            st.success("Time is up.")

    st.markdown("### Useful phrases")
    st.write("I think that ...")
    st.write("In my opinion, ...")
    st.write("On the one hand ... on the other hand ...")
    st.write(f"Current topic: {chosen_topic}")

def render_listening_exercise(item):
    st.markdown(
        f"""
        <div class="card">
            <div class="badge">Listening</div>
            <h2 style="margin:10px 0 6px 0;">{item['title']}</h2>
            <div class="subtle">
                Listening practice shell. Add your own audio or licensed material here.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "The public page shows listening sections with audio-backed true/false tasks. "
        "This simulator keeps the timing and answer flow, but does not reproduce the original audio."
    )

    uploaded = st.file_uploader("Upload audio for practice", type=["mp3", "wav", "m4a"], key=f"audio_{item['id']}")
    if uploaded is not None:
        st.audio(uploaded)

    st.markdown("### Transcript / notes")
    transcript = st.text_area(
        "Write your transcript or key phrases here",
        height=180,
        key=f"transcript_{item['id']}",
        placeholder="Paste your own transcript or listening notes...",
    )

    questions = [
        ("The speaker agrees with the proposal.", ["True", "False"], 0),
        ("The meeting was postponed.", ["True", "False"], 1),
        ("The message is about transport.", ["True", "False"], 0),
        ("The problem was solved immediately.", ["True", "False"], 1),
    ]
    score = 0
    for i, (q, options, answer) in enumerate(questions, start=1):
        st.markdown(f"**{i}. {q}**")
        chosen = st.radio(
            label="",
            options=options,
            key=f"{item['id']}_listen_q{i}",
            horizontal=True,
            index=None,
            label_visibility="collapsed",
        )
        if chosen is not None and st.button(f"Check {i}", key=f"{item['id']}_listen_check_{i}"):
            if options.index(chosen) == answer:
                st.success("Correct.")
                score += 1
                progress_update(2)
            else:
                st.error("Not quite.")

    if st.button("Submit listening set", key=f"{item['id']}_listen_submit"):
        st.success("Listening set submitted.")
        progress_update(6)
        st.write(f"Score: {score}/{len(questions)}")

def render_selected():
    item = item_by_id(st.session_state.selected_id)
    if not item:
        return

    back1, back2, back3 = st.columns([0.18, 0.18, 0.64])
    with back1:
        if st.button("← Back"):
            st.session_state.selected_id = None
            st.rerun()

    with back2:
        if st.button("Reset exam"):
            st.session_state.selected_id = None
            st.session_state.progress = 0
            st.session_state.started_at = time.time()
            st.rerun()

    st.markdown("---")

    if item["kind"] == "writing":
        render_writing_exercise(item)
    elif item["kind"] == "speaking":
        render_speaking_exercise(item)
    elif item["kind"] == "listening":
        render_listening_exercise(item)
    else:
        render_generic_exercise(item)

# ----------------------------
# App
# ----------------------------
init_state()
css()

render_header()
render_sidebar()

tab1, tab2, tab3 = st.tabs(["Catalog", "Selected exercise", "Exam mode"])

with tab1:
    render_overview()

with tab2:
    if st.session_state.selected_id is None:
        st.info("Open any exercise from the Catalog tab.")
        first_writing = choose_first_writing()
        if first_writing and st.button("Open writing task"):
            st.session_state.selected_id = first_writing["id"]
            st.rerun()
    else:
        render_selected()

with tab3:
    st.markdown(
        """
        <div class="card">
            <div class="badge">Exam mode</div>
            <h2 style="margin:10px 0 6px 0;">Full simulator overview</h2>
            <div class="subtle">
                Use this tab to present the exam structure like a product landing page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    for i, sec in enumerate(SECTION_ORDER):
        cols[i].metric(sec, f"{len(section_items(sec))} items")

    st.markdown("### Quick start")
    st.write("1. Choose a section in the sidebar.")
    st.write("2. Open a title.")
    st.write("3. Use the writing and speaking shells for timed practice.")
    st.write("4. Replace the placeholders with your own licensed material when needed.")

    st.markdown("### Progress")
    st.progress(st.session_state.progress / 100 if st.session_state.progress else 0)

    st.markdown("### Notes")
    st.write(
        "The public page is organized as a B1 catalog, but the simulator is branded for B2-style practice. "
        "The structure here is built from the visible section map and titles."
    )