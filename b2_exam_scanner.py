from flask import Flask, render_template_string, jsonify
from collections import defaultdict

app = Flask(__name__)

# Publicly visible catalog structure from the page.
# The full question texts are not reproduced here.
EXAM = {
    "Lesen": {
        "label": "Reading",
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
        "parts": [
            {
                "name": "Hören Teil 1",
                "kind": "listening",
                "minutes": 15,
                "titles": ["Lufthansa", "Erdbeben", "Bierkonsum", "Schiff", "Vögel", "Europäischen",
                           "Wetter", "Nicht sicher", "Die Stadt Friedrichsberg", "Frau Jürgens",
                           "Die Wahlbeteiligung", "In den Alpen", "In den Alpen 2", "Insel Bali",
                           "Die Fluggeselschaft", "Der Bau", "50-Euro", "Das Schladminger"]
            },
            {
                "name": "Hören Teil 2",
                "kind": "listening",
                "minutes": 15,
                "titles": ["Teil 2 – add your licensed audio + questions here"]
            },
            {
                "name": "Hören Teil 3",
                "kind": "listening",
                "minutes": 15,
                "titles": ["Teil 3 – add your licensed audio + questions here"]
            },
        ],
    },
    "Schreiben": {
        "label": "Writing",
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
        "parts": [
            {
                "name": "Teil 1",
                "kind": "speaking",
                "minutes": 5,
                "titles": ["Presentation topics from the 5-page PDF"]
            },
            {
                "name": "Teil 2 + 3",
                "kind": "speaking",
                "minutes": 10,
                "titles": ["Interactive speaking topics"]
            },
            {
                "name": "Struktur 2 + 3",
                "kind": "speaking",
                "minutes": 10,
                "titles": ["Question/answer structure cards"]
            },
        ],
    },
}

def flatten_catalog():
    catalog = []
    for section_key, section in EXAM.items():
        for part_index, part in enumerate(section["parts"], start=1):
            for title_index, title in enumerate(part["titles"], start=1):
                catalog.append({
                    "id": f"{section_key.lower()}-{part_index}-{title_index}",
                    "section": section_key,
                    "section_label": section["label"],
                    "part": part["name"],
                    "kind": part["kind"],
                    "title": title,
                    "minutes": part.get("minutes", 0),
                    "min_words": part.get("min_words", None),
                })
    return catalog

CATALOG = flatten_catalog()

HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TELC Simulator</title>
  <style>
    :root{
      --bg:#0b1020;
      --panel:#111a31;
      --panel2:#151f3a;
      --line:rgba(255,255,255,.08);
      --text:#eef2ff;
      --muted:#a9b3d4;
      --accent:#7c8cff;
      --accent2:#35d0ba;
      --shadow:0 20px 60px rgba(0,0,0,.35);
      --radius:20px;
    }
    *{box-sizing:border-box}
    body{
      margin:0;
      font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
      color:var(--text);
      background:
        radial-gradient(circle at top left, rgba(124,140,255,.15), transparent 25%),
        radial-gradient(circle at top right, rgba(53,208,186,.12), transparent 20%),
        linear-gradient(180deg, #080d1a, #0b1020 35%, #090d18 100%);
    }
    .wrap{max-width:1320px;margin:0 auto;padding:22px}
    .topbar{
      position:sticky;top:16px;z-index:10;
      display:flex;justify-content:space-between;gap:16px;align-items:center;flex-wrap:wrap;
      padding:16px 20px;background:rgba(17,26,49,.8);backdrop-filter:blur(14px);
      border:1px solid var(--line);border-radius:24px;box-shadow:var(--shadow);
    }
    .brand{display:flex;align-items:center;gap:14px;font-weight:800}
    .logo{
      width:46px;height:46px;border-radius:15px;display:grid;place-items:center;
      background:linear-gradient(135deg,var(--accent),var(--accent2));
      color:#08101f;font-weight:900;
    }
    .brand small{display:block;color:var(--muted);font-weight:600}
    .toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
    .pill{
      border:1px solid var(--line);background:rgba(255,255,255,.03);color:var(--text);
      padding:10px 14px;border-radius:999px;cursor:pointer;font-weight:700;
    }
    .pill.active,.pill:hover{background:rgba(124,140,255,.14);border-color:rgba(124,140,255,.28)}
    .hero{
      display:grid;grid-template-columns:1.25fr .95fr;gap:18px;margin-top:18px;
    }
    .card{
      background:rgba(17,26,49,.82);backdrop-filter:blur(12px);
      border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);
    }
    .hero-main{padding:28px}
    .hero-main h1{margin:0 0 10px;font-size:clamp(30px,4vw,54px);line-height:1.05}
    .hero-main p{margin:0;color:var(--muted);max-width:68ch;line-height:1.6}
    .hero-actions{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}
    .btn{
      border:0;border-radius:16px;padding:13px 18px;font-weight:800;cursor:pointer;
      color:#08101f;background:linear-gradient(135deg,var(--accent),#9aa5ff);
    }
    .btn.secondary{background:transparent;color:var(--text);border:1px solid var(--line)}
    .hero-side{padding:20px;display:grid;gap:12px}
    .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .stat{
      padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid var(--line)
    }
    .stat b{display:block;font-size:22px;margin-bottom:4px}
    .stat span{color:var(--muted);font-size:12px}
    .notice{
      padding:16px;border-radius:18px;background:rgba(53,208,186,.08);border:1px solid rgba(53,208,186,.18);
      color:#dbfff8;line-height:1.55
    }
    .grid{display:grid;grid-template-columns:300px 1fr;gap:18px;margin-top:18px}
    .sidebar,.content{padding:18px}
    .sidebar h3,.content h3{margin:0 0 12px}
    .navlist{display:grid;gap:10px}
    .navitem{
      padding:14px 15px;border-radius:16px;border:1px solid var(--line);background:rgba(255,255,255,.03);
      cursor:pointer;display:flex;justify-content:space-between;gap:10px;align-items:flex-start;
    }
    .navitem.active{background:rgba(124,140,255,.14);border-color:rgba(124,140,255,.3)}
    .navitem small{color:var(--muted)}
    .sectionhead{display:flex;justify-content:space-between;gap:12px;align-items:flex-end;margin-bottom:14px}
    .sectionhead h2{margin:0}
    .sectionhead p{margin:0;color:var(--muted)}
    .meta{
      display:flex;gap:10px;flex-wrap:wrap;align-items:center
    }
    .badge{
      display:inline-flex;align-items:center;padding:7px 10px;border-radius:999px;
      background:rgba(124,140,255,.12);border:1px solid rgba(124,140,255,.24);font-size:12px;font-weight:800
    }
    .search{
      width:100%;padding:14px 14px;border-radius:14px;border:1px solid var(--line);
      background:rgba(255,255,255,.03);color:var(--text);outline:none;margin:0 0 14px
    }
    .packs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .pack{
      padding:18px;border-radius:18px;border:1px solid var(--line);background:rgba(255,255,255,.03)
    }
    .pack-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .pack h3{margin:10px 0 8px}
    .pack p{margin:0;color:var(--muted);line-height:1.55}
    .tagrow{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}
    .tag{
      padding:8px 10px;border-radius:999px;background:rgba(255,255,255,.03);
      border:1px solid var(--line);color:var(--muted);font-size:12px
    }
    .pack button{
      margin-top:14px;border:0;border-radius:14px;padding:11px 14px;font-weight:800;cursor:pointer;
      background:linear-gradient(135deg,var(--accent),#9aa5ff);color:#08101f
    }
    .footer{color:var(--muted);font-size:13px;line-height:1.6;margin-top:14px}
    .modal{
      position:fixed;inset:0;background:rgba(4,7,15,.72);backdrop-filter:blur(10px);
      display:none;align-items:center;justify-content:center;padding:18px;z-index:30;
    }
    .modal.open{display:flex}
    .modal-card{
      width:min(980px,100%);max-height:min(92vh,920px);overflow:auto;
      background:linear-gradient(180deg, rgba(16,24,45,.98), rgba(12,18,35,.98));
      border:1px solid var(--line);border-radius:26px;box-shadow:var(--shadow);
    }
    .modal-head{
      position:sticky;top:0;background:rgba(16,24,45,.98);border-bottom:1px solid var(--line);
      padding:18px 20px;display:flex;justify-content:space-between;gap:12px;align-items:center
    }
    .modal-body{padding:20px}
    .panel{
      border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.03);padding:16px
    }
    .question{padding:14px 0;border-bottom:1px solid var(--line)}
    .question:last-child{border-bottom:0}
    textarea{
      width:100%;min-height:220px;resize:vertical;border-radius:16px;border:1px solid var(--line);
      background:rgba(255,255,255,.03);color:var(--text);padding:14px;outline:none;line-height:1.6
    }
    .options{display:grid;gap:10px}
    .option{
      padding:12px 14px;border-radius:14px;border:1px solid var(--line);background:rgba(255,255,255,.02);
      cursor:pointer
    }
    .option.correct{border-color:rgba(55,214,122,.45);background:rgba(55,214,122,.12)}
    .option.wrong{border-color:rgba(255,107,107,.45);background:rgba(255,107,107,.12)}
    .feedback{
      margin-top:12px;padding:12px 14px;border-radius:14px;border:1px solid var(--line);
      background:rgba(255,255,255,.03);color:var(--muted)
    }
    .feedback.good{border-color:rgba(55,214,122,.35);background:rgba(55,214,122,.08);color:#dcffe8}
    .feedback.bad{border-color:rgba(255,107,107,.35);background:rgba(255,107,107,.08);color:#ffe4e4}
    .mini-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
    .ghost{
      border:1px solid var(--line);background:transparent;color:var(--text);
      padding:12px 15px;border-radius:14px;cursor:pointer;font-weight:800
    }
    .timer{
      font-variant-numeric:tabular-nums;padding:8px 12px;border-radius:999px;
      border:1px solid rgba(53,208,186,.24);background:rgba(53,208,186,.08);color:#dbfff8;font-weight:800
    }
    .sr-only{position:absolute;left:-9999px}
    @media (max-width: 980px){
      .hero,.grid,.packs{grid-template-columns:1fr}
      .topbar{position:relative;top:0}
    }
  </style>
</head>
<body>
  <div class="wrap">
    <header class="topbar card">
      <div class="brand">
        <div class="logo">B2</div>
        <div>
          TELC Simulator
          <small>Modern practice dashboard</small>
        </div>
      </div>
      <div class="toolbar">
        <span class="timer" id="timerChip">Timer: 30:00</span>
        <button class="pill active" data-level="Lesen">Lesen</button>
        <button class="pill" data-level="Sprachbausteine">Sprachbausteine</button>
        <button class="pill" data-level="Hören">Hören</button>
        <button class="pill" data-level="Schreiben">Schreiben</button>
        <button class="pill" data-level="Sprechen">Sprechen</button>
      </div>
    </header>

    <section class="hero">
      <div class="card hero-main">
        <h1>One clean simulator for the full exam structure.</h1>
        <p>
          This version keeps the visible catalog from the linked page, organizes it into a modern UI,
          and leaves clear placeholders where you can insert your own licensed exercise text, audio, and PDFs.
        </p>
        <div class="hero-actions">
          <button class="btn" id="openFirstBtn">Open first exercise</button>
          <button class="btn secondary" id="openWritingBtn">Open writing task</button>
        </div>
      </div>
      <aside class="card hero-side">
        <div class="stats">
          <div class="stat"><b id="sectionCount">5</b><span>Sections</span></div>
          <div class="stat"><b id="packCount">0</b><span>Exercises</span></div>
          <div class="stat"><b id="progressChip">0%</b><span>Progress</span></div>
        </div>
        <div class="notice">
          The source page is structured as B1. The page exposes the exam map and titles, while the full exercise content is not reproduced here.
        </div>
      </aside>
    </section>

    <main class="grid">
      <aside class="card sidebar">
        <h3>Exam sections</h3>
        <div class="navlist" id="navlist"></div>
        <div class="footer">
          Use the search box to filter titles. Replace placeholders with your own material if you have the rights to use the original prompts.
        </div>
      </aside>

      <section class="card content">
        <div class="sectionhead">
          <div>
            <h2 id="sectionTitle">Lesen</h2>
            <p id="sectionDesc">Choose a part and open any title.</p>
          </div>
          <div class="meta">
            <span class="badge" id="sectionBadge">Reading</span>
          </div>
        </div>

        <input class="search" id="searchInput" placeholder="Search titles..." />
        <div class="packs" id="packs"></div>
      </section>
    </main>
  </div>

  <div class="modal" id="modal">
    <div class="modal-card">
      <div class="modal-head">
        <div>
          <h3 id="modalTitle">Exercise</h3>
          <div class="meta" id="modalMeta"></div>
        </div>
        <button class="ghost" id="closeModalBtn">Close</button>
      </div>
      <div class="modal-body" id="modalBody"></div>
    </div>
  </div>

  <script>
    const catalog = {{ catalog|tojson }};
    const structure = {{ structure|tojson }};

    const state = {
      section: "Lesen",
      search: "",
      timer: 30 * 60,
      timerRunning: true,
      progress: Number(localStorage.getItem("telc_progress") || 0),
    };

    const el = (id) => document.getElementById(id);
    const navlist = el("navlist");
    const packs = el("packs");
    const modal = el("modal");

    function formatTime(sec){
      const m = String(Math.floor(sec / 60)).padStart(2, "0");
      const s = String(sec % 60).padStart(2, "0");
      return `${m}:${s}`;
    }

    function updateTimer(){
      el("timerChip").textContent = "Timer: " + formatTime(Math.max(0, state.timer));
    }

    setInterval(() => {
      if (!state.timerRunning) return;
      state.timer--;
      updateTimer();
      if (state.timer <= 0) state.timerRunning = false;
    }, 1000);

    function saveProgress(value){
      state.progress = Math.max(0, Math.min(100, value));
      localStorage.setItem("telc_progress", String(state.progress));
      el("progressChip").textContent = state.progress + "%";
    }

    function currentSectionItems(){
      return catalog.filter(x => x.section === state.section)
        .filter(x => x.title.toLowerCase().includes(state.search.toLowerCase()));
    }

    function renderNav(){
      navlist.innerHTML = "";
      Object.keys(structure).forEach(section => {
        const sec = structure[section];
        const total = catalog.filter(x => x.section === section).length;
        const item = document.createElement("div");
        item.className = "navitem" + (section === state.section ? " active" : "");
        item.innerHTML = `<div><b>${section}</b><br><small>${sec.label} • ${total} exercises</small></div><span>›</span>`;
        item.onclick = () => {
          state.section = section;
          el("searchInput").value = "";
          state.search = "";
          renderAll();
        };
        navlist.appendChild(item);
      });
    }

    function renderPacks(){
      const sec = structure[state.section];
      el("sectionTitle").textContent = state.section;
      el("sectionDesc").textContent = sec.label + " practice, organized by part.";
      el("sectionBadge").textContent = sec.label;
      el("packCount").textContent = catalog.length;

      const items = currentSectionItems();
      packs.innerHTML = "";

      if (!items.length){
        packs.innerHTML = `<div class="panel" style="grid-column:1/-1">No exercises match your search.</div>`;
        return;
      }

      items.forEach(item => {
        const card = document.createElement("article");
        card.className = "pack";
        card.innerHTML = `
          <div class="pack-top">
            <div>
              <span class="badge">${item.part}</span>
              <h3>${item.title}</h3>
            </div>
            <div class="meta">${item.minutes ? item.minutes + " min" : ""}</div>
          </div>
          <p>Type: ${item.kind}. This card uses the visible title from the source page and a clean simulator shell.</p>
          <div class="tagrow">
            <span class="tag">${item.section_label}</span>
            <span class="tag">${item.kind}</span>
            ${item.min_words ? `<span class="tag">Min ${item.min_words} words</span>` : ""}
          </div>
          <button>Open exercise</button>
        `;
        card.querySelector("button").onclick = () => openExercise(item);
        packs.appendChild(card);
      });
    }

    function renderAll(){
      renderNav();
      renderPacks();
      saveProgress(state.progress);
    }

    function openExercise(item){
      modal.classList.add("open");
      el("modalTitle").textContent = item.title;
      el("modalMeta").textContent = `${item.part} • ${item.section_label} • ${item.kind}`;
      if (item.kind === "writing"){
        renderWriting(item);
      } else if (item.kind === "speaking"){
        renderSpeaking(item);
      } else {
        renderGeneric(item);
      }
    }

    function renderGeneric(item){
      modalBody.innerHTML = `
        <div class="panel">
          <p><b>Placeholder exercise shell.</b></p>
          <p style="color:var(--muted);line-height:1.6">
            Insert your own licensed reading/listening/grammar content here.
            This template keeps the structure ready without copying the original text.
          </p>

          <div class="question">
            <h4>1. Sample answer area</h4>
            <div class="options">
              <label class="option"><input class="sr-only" type="radio" name="q1"> Option A</label>
              <label class="option"><input class="sr-only" type="radio" name="q1"> Option B</label>
              <label class="option"><input class="sr-only" type="radio" name="q1"> Option C</label>
            </div>
          </div>

          <div class="question">
            <h4>2. Sample answer area</h4>
            <div class="options">
              <label class="option"><input class="sr-only" type="radio" name="q2"> Option A</label>
              <label class="option"><input class="sr-only" type="radio" name="q2"> Option B</label>
              <label class="option"><input class="sr-only" type="radio" name="q2"> Option C</label>
            </div>
          </div>

          <div class="mini-actions">
            <button class="ghost" id="markDone">Mark as done</button>
          </div>
          <div class="feedback" id="genericFeedback">Use this slot for the original exercise content or your own practice set.</div>
        </div>
      `;
      document.getElementById("markDone").onclick = () => {
        const fb = document.getElementById("genericFeedback");
        fb.className = "feedback good";
        fb.textContent = "Completed.";
        saveProgress(state.progress + 5);
      };
    }

    function renderWriting(item){
      const key = "draft_" + item.id;
      const saved = localStorage.getItem(key) || "";
      modalBody.innerHTML = `
        <div class="panel">
          <p><b>Writing task shell.</b> The linked page shows a complaint letter task with 30 minutes and at least 150 words.  [oai_citation:1‡telcexam.tech](https://telcexam.tech/quizz/schreiben2_b2.html)</p>
          <p style="color:var(--muted);line-height:1.6">
            Add the original prompt text only if you have the rights to do so. This layout is ready for your own content.
          </p>
          <textarea id="writingBox" placeholder="Write your response here...">${saved}</textarea>
          <div class="mini-actions">
            <button class="ghost" id="saveDraft">Save draft</button>
            <button class="ghost" id="clearDraft">Clear</button>
          </div>
          <div class="feedback" id="writingFeedback">Draft saved locally in the browser.</div>
        </div>
      `;
      const box = document.getElementById("writingBox");
      document.getElementById("saveDraft").onclick = () => {
        localStorage.setItem(key, box.value);
        const fb = document.getElementById("writingFeedback");
        fb.className = "feedback good";
        fb.textContent = "Draft saved locally.";
        saveProgress(state.progress + 8);
      };
      document.getElementById("clearDraft").onclick = () => {
        box.value = "";
        localStorage.removeItem(key);
      };
    }

    function renderSpeaking(item){
      modalBody.innerHTML = `
        <div class="panel">
          <p><b>Speaking task shell.</b> The linked PDF is 5 pages long and contains presentation prompts and follow-up questions.  [oai_citation:2‡telcexam.tech](https://telcexam.tech/quizz/sprechen1.pdf)</p>
          <p style="color:var(--muted);line-height:1.6">
            Use this structure for your own prompts, timing, and follow-up cards.
          </p>
          <div class="question">
            <h4>Topic cards</h4>
            <div class="tagrow">
              <span class="tag">Book</span>
              <span class="tag">Film</span>
              <span class="tag">Travel</span>
              <span class="tag">Music event</span>
              <span class="tag">Sport event</span>
            </div>
          </div>
          <div class="question">
            <h4>Practice box</h4>
            <textarea placeholder="Write notes for your speaking answer..."></textarea>
          </div>
          <div class="mini-actions">
            <button class="ghost" id="markSpeak">Mark as practiced</button>
          </div>
          <div class="feedback" id="speakFeedback">Practice out loud, then repeat with a timer.</div>
        </div>
      `;
      document.getElementById("markSpeak").onclick = () => {
        const fb = document.getElementById("speakFeedback");
        fb.className = "feedback good";
        fb.textContent = "Marked as practiced.";
        saveProgress(state.progress + 8);
      };
    }

    el("searchInput").addEventListener("input", (e) => {
      state.search = e.target.value;
      renderPacks();
    });

    el("closeModalBtn").onclick = () => modal.classList.remove("open");
    modal.addEventListener("click", (e) => { if (e.target === modal) modal.classList.remove("open"); });

    document.querySelectorAll(".pill[data-level]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".pill[data-level]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.section = btn.dataset.level;
        state.search = "";
        el("searchInput").value = "";
        renderAll();
      });
    });

    document.getElementById("openFirstBtn").onclick = () => {
      const first = catalog[0];
      openExercise(first);
    };

    document.getElementById("openWritingBtn").onclick = () => {
      const firstWriting = catalog.find(x => x.section === "Schreiben");
      if (firstWriting) openExercise(firstWriting);
    };

    renderAll();
    updateTimer();
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(
        HTML,
        catalog=CATALOG,
        structure=EXAM,
    )

@app.route("/api/catalog")
def api_catalog():
    return jsonify(CATALOG)

@app.route("/api/structure")
def api_structure():
    return jsonify(EXAM)

if __name__ == "__main__":
    app.run(debug=True)