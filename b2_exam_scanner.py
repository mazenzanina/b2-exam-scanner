<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>TELC B2 Simulator</title>
  <meta name="description" content="Modern TELC B2 German exam simulator with reading, listening, writing, and speaking practice." />
  <style>
    :root{
      --bg:#0b1020;
      --panel:#10182d;
      --panel-2:#151f3a;
      --line:rgba(255,255,255,.08);
      --text:#eef2ff;
      --muted:#a7b0d6;
      --accent:#7c8cff;
      --accent-2:#35d0ba;
      --danger:#ff6b6b;
      --success:#37d67a;
      --warning:#ffd166;
      --shadow:0 20px 60px rgba(0,0,0,.35);
      --radius:20px;
      --radius-sm:14px;
      --max:1180px;
    }
    *{box-sizing:border-box}
    html,body{margin:0;padding:0;background:
      radial-gradient(circle at top left, rgba(124,140,255,.15), transparent 28%),
      radial-gradient(circle at top right, rgba(53,208,186,.12), transparent 22%),
      linear-gradient(180deg, #080d1a, #0b1020 35%, #090d18 100%);
      color:var(--text);
      font-family:Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    a{color:inherit;text-decoration:none}
    .wrap{max-width:var(--max);margin:0 auto;padding:24px}
    .topbar{
      display:flex;align-items:center;justify-content:space-between;gap:16px;
      padding:16px 20px;border:1px solid var(--line);border-radius:24px;
      background:rgba(16,24,45,.75);backdrop-filter:blur(14px);box-shadow:var(--shadow);
      position:sticky;top:16px;z-index:10;
    }
    .brand{display:flex;align-items:center;gap:14px;font-weight:800}
    .logo{
      width:44px;height:44px;border-radius:14px;
      background:linear-gradient(135deg,var(--accent),var(--accent-2));
      display:grid;place-items:center;color:#08101f;font-weight:900;
      box-shadow:0 12px 28px rgba(124,140,255,.28);
    }
    .brand small{display:block;color:var(--muted);font-weight:600}
    .toolbar{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:flex-end}
    .pill{
      border:1px solid var(--line);background:rgba(255,255,255,.03);
      color:var(--text);padding:10px 14px;border-radius:999px;
      cursor:pointer;transition:.2s ease;font-weight:700;
    }
    .pill:hover,.pill.active{transform:translateY(-1px);background:rgba(124,140,255,.14);border-color:rgba(124,140,255,.28)}
    .hero{
      display:grid;grid-template-columns:1.3fr .9fr;gap:18px;margin-top:20px;
    }
    .card{
      background:rgba(16,24,45,.82);backdrop-filter:blur(12px);
      border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);
    }
    .hero-main{padding:28px}
    .hero-main h1{margin:0 0 10px;font-size:clamp(30px,4vw,54px);line-height:1.05}
    .hero-main p{margin:0;color:var(--muted);font-size:16px;line-height:1.6;max-width:62ch}
    .hero-actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}
    .btn{
      border:0;border-radius:16px;padding:13px 18px;font-weight:800;cursor:pointer;
      transition:.2s ease;color:#08101f;background:linear-gradient(135deg,var(--accent),#9aa5ff);
    }
    .btn.secondary{background:transparent;color:var(--text);border:1px solid var(--line)}
    .btn:hover{transform:translateY(-1px)}
    .hero-side{padding:22px;display:grid;gap:12px}
    .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
    .stat{
      padding:16px;border-radius:18px;background:rgba(255,255,255,.03);border:1px solid var(--line)
    }
    .stat b{display:block;font-size:22px;margin-bottom:4px}
    .stat span{color:var(--muted);font-size:12px}
    .notice{
      padding:16px;border-radius:18px;background:rgba(53,208,186,.08);border:1px solid rgba(53,208,186,.18);
      color:#dffcf6;line-height:1.55;
    }
    .grid{
      margin-top:18px;
      display:grid;grid-template-columns:280px 1fr;gap:18px;
    }
    .sidebar{padding:18px}
    .sidebar h3{margin:0 0 12px}
    .navlist{display:grid;gap:10px}
    .navitem{
      padding:14px 15px;border-radius:16px;border:1px solid var(--line);background:rgba(255,255,255,.03);
      cursor:pointer;transition:.2s ease;display:flex;align-items:center;justify-content:space-between;gap:10px;
    }
    .navitem.active{background:rgba(124,140,255,.14);border-color:rgba(124,140,255,.3)}
    .navitem:hover{transform:translateY(-1px)}
    .navitem small{color:var(--muted)}
    .content{padding:18px}
    .sectionhead{
      display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:14px;
    }
    .sectionhead h2{margin:0;font-size:26px}
    .sectionhead p{margin:0;color:var(--muted)}
    .packs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
    .pack{
      padding:18px;border-radius:18px;border:1px solid var(--line);background:rgba(255,255,255,.03);
      display:flex;flex-direction:column;gap:12px
    }
    .pack-top{display:flex;justify-content:space-between;gap:10px;align-items:flex-start}
    .badge{
      display:inline-flex;align-items:center;gap:6px;padding:7px 10px;border-radius:999px;
      background:rgba(124,140,255,.12);border:1px solid rgba(124,140,255,.24);color:#dce3ff;font-size:12px;font-weight:800;
    }
    .pack h3{margin:0}
    .pack p{margin:0;color:var(--muted);line-height:1.55}
    .tagrow{display:flex;flex-wrap:wrap;gap:8px}
    .tag{
      padding:8px 10px;border-radius:999px;background:rgba(255,255,255,.03);
      border:1px solid var(--line);color:var(--muted);font-size:12px;
    }
    .pack .btn{width:fit-content}
    .footer{
      color:var(--muted);font-size:13px;line-height:1.6;margin:18px 0 6px
    }

    /* modal */
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
      position:sticky;top:0;background:rgba(16,24,45,.98);backdrop-filter:blur(10px);
      border-bottom:1px solid var(--line);padding:18px 20px;display:flex;justify-content:space-between;gap:12px;align-items:center;
    }
    .modal-head h3{margin:0;font-size:20px}
    .modal-body{padding:20px}
    .meta{color:var(--muted);font-size:14px}
    .panel{
      border:1px solid var(--line);border-radius:18px;background:rgba(255,255,255,.03);
      padding:16px;margin-top:14px;
    }
    .question{padding:14px 0;border-bottom:1px solid var(--line)}
    .question:last-child{border-bottom:0}
    .question h4{margin:0 0 10px}
    .options{display:grid;gap:10px}
    .option{
      padding:12px 14px;border-radius:14px;border:1px solid var(--line);background:rgba(255,255,255,.02);
      cursor:pointer;transition:.2s ease
    }
    .option:hover{transform:translateY(-1px);border-color:rgba(124,140,255,.3)}
    .option.correct{border-color:rgba(55,214,122,.45);background:rgba(55,214,122,.12)}
    .option.wrong{border-color:rgba(255,107,107,.45);background:rgba(255,107,107,.12)}
    textarea,input,select{
      width:100%;padding:14px 14px;border-radius:14px;border:1px solid var(--line);
      background:rgba(255,255,255,.03);color:var(--text);outline:none
    }
    textarea{min-height:220px;resize:vertical;line-height:1.6}
    .row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
    .feedback{
      margin-top:12px;padding:12px 14px;border-radius:14px;border:1px solid var(--line);
      color:var(--muted);background:rgba(255,255,255,.03)
    }
    .feedback.good{border-color:rgba(55,214,122,.35);background:rgba(55,214,122,.08);color:#dcffe8}
    .feedback.bad{border-color:rgba(255,107,107,.35);background:rgba(255,107,107,.08);color:#ffe4e4}
    .mini-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:14px}
    .ghost{
      border:1px solid var(--line);background:transparent;color:var(--text);
      padding:12px 15px;border-radius:14px;cursor:pointer;font-weight:800
    }
    .timer{
      font-variant-numeric:tabular-nums;
      padding:8px 12px;border-radius:999px;border:1px solid rgba(53,208,186,.24);
      background:rgba(53,208,186,.08);color:#dbfff8;font-weight:800
    }

    .sr-only{position:absolute;left:-9999px}
    @media (max-width: 980px){
      .hero,.grid,.packs,.row{grid-template-columns:1fr}
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
          TELC B2 Simulator
          <small>Modern practice platform</small>
        </div>
      </div>
      <div class="toolbar">
        <span class="timer" id="timerChip">Timer: 30:00</span>
        <button class="pill active" data-level="b2">B2</button>
        <button class="pill" data-level="b1">B1</button>
      </div>
    </header>

    <section class="hero">
      <div class="card hero-main">
        <h1>Modern German exam practice, built like a real product.</h1>
        <p>
          This template mirrors the TELC flow with clean navigation, exercise cards, timers, answer checking,
          writing practice, and speaking prompts. Replace the sample tasks with your own licensed content or your own practice material.
        </p>
        <div class="hero-actions">
          <button class="btn" id="startReadingBtn">Start Reading</button>
          <button class="btn secondary" id="startWritingBtn">Open Writing Task</button>
        </div>
      </div>
      <aside class="card hero-side">
        <div class="stats">
          <div class="stat"><b id="sectionCount">5</b><span>Sections</span></div>
          <div class="stat"><b id="packCount">10</b><span>Practice packs</span></div>
          <div class="stat"><b id="saveState">0%</b><span>Progress</span></div>
        </div>
        <div class="notice">
          Designed for GitHub Pages or any static host. One file is enough to run it.
          Add your own audio, PDFs, and question sets later.
        </div>
      </aside>
    </section>

    <main class="grid">
      <aside class="card sidebar">
        <h3>Exam sections</h3>
        <div class="navlist" id="navlist"></div>
        <div class="footer">
          Tip: keep your real content in a separate JSON file so the UI stays reusable.
        </div>
      </aside>

      <section class="card content">
        <div class="sectionhead">
          <div>
            <h2 id="sectionTitle">Reading</h2>
            <p id="sectionDesc">Select a section to see the practice packs.</p>
          </div>
          <div class="badge" id="sectionBadge">TELC-style</div>
        </div>
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
    const examData = {
      b2: {
        reading: {
          title: "Lesen",
          desc: "Reading practice with multiple choice, matching, and short-answer tasks.",
          packs: [
            {
              id: "read-1",
              title: "Headline matching",
              type: "match",
              duration: "15 min",
              tags: ["Reading", "Matching", "Exam logic"],
              prompt: "Match each short text with the best headline.",
              items: [
                { text: "A local community shares tools, books, and even services so nothing useful gets wasted.", options: ["Shopping habits", "Sharing and sustainability", "Online delivery", "Sport injuries"], answer: 1 },
                { text: "A psychologist explains why shopping can feel rewarding only for a short time.", options: ["Buying feels like a reward", "Learning languages", "Travel planning", "Public transport"], answer: 0 },
                { text: "A repair initiative helps people fix appliances instead of throwing them away.", options: ["Repair instead of replace", "New fashion trends", "Summer camp", "University exams"], answer: 0 }
              ]
            },
            {
              id: "read-2",
              title: "Short article test",
              type: "mcq",
              duration: "20 min",
              tags: ["Reading", "MCQ", "Speed"],
              prompt: "Read the article and answer the questions.",
              items: [
                {
                  q: "What is the main goal of the project?",
                  options: ["To sell more products", "To reduce waste", "To build cars", "To increase rent"],
                  answer: 1
                },
                {
                  q: "What is emphasized besides the environmental benefit?",
                  options: ["Fashion", "Social interaction", "Traffic", "Sports betting"],
                  answer: 1
                }
              ]
            }
          ]
        },
        grammar: {
          title: "Sprachbausteine",
          desc: "Grammar and language elements in a cleaner, exam-friendly interface.",
          packs: [
            {
              id: "gram-1",
              title: "Context grammar",
              type: "mcq",
              duration: "20 min",
              tags: ["Grammar", "Vocabulary", "B2"],
              prompt: "Choose the best completion in context.",
              items: [
                {
                  q: "Although the task was difficult, he finished it ____.",
                  options: ["carefully", "successfully", "yesterday", "outside"],
                  answer: 1
                },
                {
                  q: "She didn't attend the meeting because she had already made other ____.",
                  options: ["results", "choices", "plans", "reasons"],
                  answer: 2
                }
              ]
            },
            {
              id: "gram-2",
              title: "Sentence building",
              type: "fill",
              duration: "15 min",
              tags: ["Sentence order", "Rules", "Practice"],
              prompt: "Insert the missing word or phrase.",
              items: [
                { q: "If you need help, please ____ the support team.", answer: "contact" },
                { q: "The report was sent ____ yesterday afternoon.", answer: "in" }
              ]
            }
          ]
        },
        listening: {
          title: "Hören",
          desc: "Listening practice with audio placeholders and transcript-based questions.",
          packs: [
            {
              id: "listen-1",
              title: "Listening Part 1",
              type: "listening",
              duration: "20 min",
              tags: ["Listening", "Audio", "True/False"],
              prompt: "Upload your audio or use the transcript mode below.",
              transcript: [
                "The speaker says the new policy will start next month.",
                "The meeting moved from Monday to Wednesday.",
                "Tickets can now be booked online."
              ],
              items: [
                { q: "The policy starts immediately.", options: ["True", "False"], answer: 1 },
                { q: "The meeting was postponed.", options: ["True", "False"], answer: 0 },
                { q: "Tickets are available online.", options: ["True", "False"], answer: 0 }
              ]
            },
            {
              id: "listen-2",
              title: "Listening Part 2",
              type: "listening",
              duration: "25 min",
              tags: ["Listening", "Notes", "Details"],
              prompt: "Practice short-note comprehension.",
              transcript: [
                "A man calls to reschedule an appointment.",
                "A woman asks about opening hours.",
                "A message mentions a delayed train."
              ],
              items: [
                { q: "The appointment is canceled forever.", options: ["True", "False"], answer: 1 },
                { q: "The message is about transport.", options: ["True", "False"], answer: 0 }
              ]
            }
          ]
        },
        writing: {
          title: "Schreiben",
          desc: "Writing prompts with word count, timer, and draft saving.",
          packs: [
            {
              id: "write-1",
              title: "Complaint letter",
              type: "writing",
              duration: "30 min",
              tags: ["Writing", "Email", "150+ words"],
              prompt:
                "You joined a group activity that was poorly organized. Write a complaint email to the organizer.",
              checklist: [
                "Introduce the situation",
                "Describe the problems clearly",
                "State what you expect as a solution",
                "Use a formal closing"
              ],
              minWords: 150
            },
            {
              id: "write-2",
              title: "Opinion email",
              type: "writing",
              duration: "30 min",
              tags: ["Writing", "Opinion", "Structure"],
              prompt:
                "Write an email to a friend giving your opinion about studying German abroad.",
              checklist: [
                "Give an introduction",
                "Explain advantages and disadvantages",
                "Share your recommendation"
              ],
              minWords: 120
            }
          ]
        },
        speaking: {
          title: "Sprechen",
          desc: "Speaking practice cards with prompts, follow-up questions, and self-recording support.",
          packs: [
            {
              id: "speak-1",
              title: "Presentation starter",
              type: "speaking",
              duration: "15 min",
              tags: ["Speaking", "Presentation", "Follow-up"],
              prompt: "Choose a topic and present for 2 minutes.",
              topics: ["A book", "A trip", "A film", "A sport event", "A favorite place"],
              followups: [
                "Why did you choose this topic?",
                "What do you like most about it?",
                "Would you recommend it to others?"
              ]
            },
            {
              id: "speak-2",
              title: "Discussion practice",
              type: "speaking",
              duration: "15 min",
              tags: ["Speaking", "Dialogue", "Interaction"],
              prompt: "Practice agreeing, disagreeing, and making suggestions.",
              topics: ["Public transport", "Healthy habits", "Learning languages", "Weekend plans"],
              followups: [
                "I agree because...",
                "I see your point, but...",
                "Maybe we could..."
              ]
            }
          ]
        }
      },
      b1: {
        reading: { title: "Lesen", desc: "B1 reading practice.", packs: [] },
        grammar: { title: "Sprachbausteine", desc: "B1 grammar practice.", packs: [] },
        listening: { title: "Hören", desc: "B1 listening practice.", packs: [] },
        writing: { title: "Schreiben", desc: "B1 writing practice.", packs: [] },
        speaking: { title: "Sprechen", desc: "B1 speaking practice.", packs: [] }
      }
    };

    const sectionOrder = ["reading", "grammar", "listening", "writing", "speaking"];

    const state = {
      level: "b2",
      section: "reading",
      progress: Number(localStorage.getItem("telc_progress") || 0),
      timer: 30 * 60,
      timerRunning: false,
      timerId: null,
      selected: {}
    };

    const el = (id) => document.getElementById(id);
    const navlist = el("navlist");
    const packs = el("packs");
    const modal = el("modal");
    const modalTitle = el("modalTitle");
    const modalMeta = el("modalMeta");
    const modalBody = el("modalBody");

    function saveProgress(value){
      state.progress = Math.max(0, Math.min(100, value));
      localStorage.setItem("telc_progress", String(state.progress));
      el("saveState").textContent = state.progress + "%";
    }

    function formatTime(sec){
      const m = String(Math.floor(sec / 60)).padStart(2, "0");
      const s = String(sec % 60).padStart(2, "0");
      return `${m}:${s}`;
    }

    function startTimer(minutes){
      state.timer = minutes * 60;
      if (state.timerId) clearInterval(state.timerId);
      state.timerRunning = true;
      updateTimer();
      state.timerId = setInterval(() => {
        if (!state.timerRunning) return;
        state.timer--;
        updateTimer();
        if (state.timer <= 0){
          state.timerRunning = false;
          clearInterval(state.timerId);
        }
      }, 1000);
    }

    function updateTimer(){
      el("timerChip").textContent = "Timer: " + formatTime(Math.max(0, state.timer));
    }

    function renderNav(){
      navlist.innerHTML = "";
      sectionOrder.forEach(key => {
        const sec = examData[state.level][key];
        const item = document.createElement("div");
        item.className = "navitem" + (state.section === key ? " active" : "");
        item.innerHTML = `<div><b>${sec.title}</b><br><small>${sec.desc}</small></div><span>›</span>`;
        item.onclick = () => {
          state.section = key;
          renderAll();
        };
        navlist.appendChild(item);
      });
    }

    function renderPacks(){
      const sec = examData[state.level][state.section];
      el("sectionTitle").textContent = sec.title;
      el("sectionDesc").textContent = sec.desc;

      const allPacks = sec.packs || [];
      el("packCount").textContent = Object.values(examData[state.level]).reduce((acc, s) => acc + (s.packs ? s.packs.length : 0), 0);

      packs.innerHTML = "";
      if (!allPacks.length){
        packs.innerHTML = `<div class="panel" style="grid-column:1/-1">
          No packs added yet for this mode. Add your own content to the examData object.
        </div>`;
        return;
      }

      allPacks.forEach(pack => {
        const card = document.createElement("article");
        card.className = "pack";
        card.innerHTML = `
          <div class="pack-top">
            <div>
              <span class="badge">${pack.type.toUpperCase()}</span>
              <h3 style="margin-top:12px">${pack.title}</h3>
            </div>
            <div class="meta">${pack.duration}</div>
          </div>
          <p>${pack.prompt}</p>
          <div class="tagrow">${(pack.tags || []).map(t => `<span class="tag">${t}</span>`).join("")}</div>
          <button class="btn">Open practice</button>
        `;
        card.querySelector("button").onclick = () => openPack(pack);
        packs.appendChild(card);
      });
    }

    function renderAll(){
      renderNav();
      renderPacks();
      el("sectionBadge").textContent = state.level.toUpperCase() + " mode";
      el("sectionCount").textContent = sectionOrder.length;
      saveProgress(state.progress);
    }

    function openPack(pack){
      modal.classList.add("open");
      modalTitle.textContent = pack.title;
      modalMeta.textContent = `${pack.duration} • ${pack.type.toUpperCase()}`;
      if (pack.type === "mcq") renderMCQ(pack);
      else if (pack.type === "match") renderMatch(pack);
      else if (pack.type === "fill") renderFill(pack);
      else if (pack.type === "listening") renderListening(pack);
      else if (pack.type === "writing") renderWriting(pack);
      else if (pack.type === "speaking") renderSpeaking(pack);
    }

    function closeModal(){ modal.classList.remove("open"); }

    function renderMCQ(pack){
      let checked = false;
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.prompt}</div>
          <div id="mcqRoot"></div>
          <div class="mini-actions">
            <button class="btn" id="checkMCQ">Check answers</button>
            <button class="ghost" id="resetMCQ">Reset</button>
          </div>
          <div class="feedback" id="mcqFeedback">Answer all questions, then check your score.</div>
        </div>
      `;

      const root = document.getElementById("mcqRoot");
      pack.items.forEach((item, idx) => {
        const block = document.createElement("div");
        block.className = "question";
        block.innerHTML = `
          <h4>${idx + 1}. ${item.q}</h4>
          <div class="options">
            ${item.options.map((opt, i) => `
              <label class="option">
                <input type="radio" name="q${idx}" value="${i}" class="sr-only">
                ${opt}
              </label>
            `).join("")}
          </div>
        `;
        root.appendChild(block);
      });

      document.getElementById("checkMCQ").onclick = () => {
        if (checked) return;
        let score = 0;
        pack.items.forEach((item, idx) => {
          const chosen = document.querySelector(`input[name="q${idx}"]:checked`);
          const labels = [...document.querySelectorAll(`input[name="q${idx}"]`)].map(i => i.parentElement);
          labels.forEach(l => l.classList.remove("correct", "wrong"));
          if (chosen && Number(chosen.value) === item.answer) {
            score++;
            chosen.parentElement.classList.add("correct");
          } else {
            if (chosen) chosen.parentElement.classList.add("wrong");
            const correctLabel = labels[item.answer];
            if (correctLabel) correctLabel.classList.add("correct");
          }
        });
        checked = true;
        const fb = document.getElementById("mcqFeedback");
        fb.className = "feedback good";
        fb.textContent = `Score: ${score}/${pack.items.length}.`;
        saveProgress(Math.min(100, state.progress + 8));
      };

      document.getElementById("resetMCQ").onclick = () => renderMCQ(pack);
    }

    function renderMatch(pack){
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.prompt}</div>
          ${pack.items.map((item, idx) => `
            <div class="question">
              <h4>${idx + 1}. ${item.text}</h4>
              <select data-idx="${idx}">
                <option value="">Choose a headline</option>
                ${item.options.map((opt, i) => `<option value="${i}">${opt}</option>`).join("")}
              </select>
            </div>
          `).join("")}
          <div class="mini-actions">
            <button class="btn" id="checkMatch">Check answers</button>
          </div>
          <div class="feedback" id="matchFeedback">Select a headline for each text.</div>
        </div>
      `;

      document.getElementById("checkMatch").onclick = () => {
        let score = 0;
        const selects = [...modalBody.querySelectorAll("select")];
        selects.forEach((sel, idx) => {
          const correct = pack.items[idx].answer;
          const chosen = Number(sel.value);
          sel.style.borderColor = chosen === correct ? "rgba(55,214,122,.6)" : "rgba(255,107,107,.6)";
          if (chosen === correct) score++;
        });
        const fb = document.getElementById("matchFeedback");
        fb.className = score === pack.items.length ? "feedback good" : "feedback bad";
        fb.textContent = `Score: ${score}/${pack.items.length}.`;
        saveProgress(Math.min(100, state.progress + 10));
      };
    }

    function renderFill(pack){
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.prompt}</div>
          ${pack.items.map((item, idx) => `
            <div class="question">
              <h4>${idx + 1}. ${item.q}</h4>
              <input type="text" data-answer="${item.answer}" placeholder="Type your answer">
            </div>
          `).join("")}
          <div class="mini-actions">
            <button class="btn" id="checkFill">Check answers</button>
          </div>
          <div class="feedback" id="fillFeedback">Type the missing words, then check.</div>
        </div>
      `;
      document.getElementById("checkFill").onclick = () => {
        let score = 0;
        const inputs = [...modalBody.querySelectorAll("input[type=text]")];
        inputs.forEach(inp => {
          const a = inp.dataset.answer.trim().toLowerCase();
          const v = inp.value.trim().toLowerCase();
          inp.style.borderColor = v === a ? "rgba(55,214,122,.6)" : "rgba(255,107,107,.6)";
          if (v === a) score++;
        });
        const fb = document.getElementById("fillFeedback");
        fb.className = score === pack.items.length ? "feedback good" : "feedback bad";
        fb.textContent = `Score: ${score}/${pack.items.length}.`;
        saveProgress(Math.min(100, state.progress + 8));
      };
    }

    function renderListening(pack){
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.prompt}</div>
          <div class="panel" style="margin-top:12px">
            <b>Transcript mode</b>
            <div style="margin-top:10px;color:var(--muted);line-height:1.7">
              ${pack.transcript.map(t => `• ${t}`).join("<br>")}
            </div>
          </div>
          ${pack.items.map((item, idx) => `
            <div class="question">
              <h4>${idx + 1}. ${item.q}</h4>
              <div class="options">
                ${item.options.map((opt, i) => `
                  <label class="option">
                    <input type="radio" name="l${idx}" value="${i}" class="sr-only">
                    ${opt}
                  </label>
                `).join("")}
              </div>
            </div>
          `).join("")}
          <div class="mini-actions">
            <button class="btn" id="checkListen">Check answers</button>
          </div>
          <div class="feedback" id="listenFeedback">Use the transcript or add audio later.</div>
        </div>
      `;

      document.getElementById("checkListen").onclick = () => {
        let score = 0;
        pack.items.forEach((item, idx) => {
          const chosen = document.querySelector(`input[name="l${idx}"]:checked`);
          const labels = [...document.querySelectorAll(`input[name="l${idx}"]`)].map(i => i.parentElement);
          labels.forEach(l => l.classList.remove("correct", "wrong"));
          if (chosen && Number(chosen.value) === item.answer) {
            score++;
            chosen.parentElement.classList.add("correct");
          } else {
            if (chosen) chosen.parentElement.classList.add("wrong");
            const correctLabel = labels[item.answer];
            if (correctLabel) correctLabel.classList.add("correct");
          }
        });
        const fb = document.getElementById("listenFeedback");
        fb.className = "feedback good";
        fb.textContent = `Score: ${score}/${pack.items.length}.`;
        saveProgress(Math.min(100, state.progress + 10));
      };
    }

    function renderWriting(pack){
      const draftKey = `draft_${state.level}_${pack.id}`;
      const saved = localStorage.getItem(draftKey) || "";
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.duration} • minimum ${pack.minWords} words</div>
          <h4 style="margin:12px 0 10px">${pack.prompt}</h4>
          <div class="panel">
            <b>Checklist</b>
            <ul style="color:var(--muted);line-height:1.8;margin:10px 0 0 18px">
              ${(pack.checklist || []).map(i => `<li>${i}</li>`).join("")}
            </ul>
          </div>
          <div style="margin-top:12px">
            <textarea id="writingBox" placeholder="Write your response here...">${saved}</textarea>
          </div>
          <div class="row" style="margin-top:12px">
            <div class="panel">Words: <b id="wordCount">0</b></div>
            <div class="panel">Target: <b>${pack.minWords}</b></div>
          </div>
          <div class="mini-actions">
            <button class="btn" id="saveDraft">Save draft</button>
            <button class="ghost" id="clearDraft">Clear</button>
          </div>
          <div class="feedback" id="writingFeedback">Use formal structure, clear paragraphs, and a closing.</div>
        </div>
      `;

      const box = document.getElementById("writingBox");
      const wc = document.getElementById("wordCount");
      const updateCount = () => {
        const count = (box.value.trim().match(/\S+/g) || []).length;
        wc.textContent = count;
      };
      box.addEventListener("input", updateCount);
      updateCount();

      document.getElementById("saveDraft").onclick = () => {
        localStorage.setItem(draftKey, box.value);
        const fb = document.getElementById("writingFeedback");
        fb.className = "feedback good";
        fb.textContent = "Draft saved locally in your browser.";
        saveProgress(Math.min(100, state.progress + 12));
      };
      document.getElementById("clearDraft").onclick = () => {
        box.value = "";
        localStorage.removeItem(draftKey);
        updateCount();
      };
    }

    function renderSpeaking(pack){
      modalBody.innerHTML = `
        <div class="panel">
          <div class="meta">${pack.prompt}</div>
          <div class="row" style="margin-top:12px">
            <div class="panel">
              <b>Topics</b>
              <div class="tagrow" style="margin-top:10px">
                ${pack.topics.map(t => `<span class="tag">${t}</span>`).join("")}
              </div>
            </div>
            <div class="panel">
              <b>Useful phrases</b>
              <div style="color:var(--muted);line-height:1.8;margin-top:10px">
                I think...<br>
                In my opinion...<br>
                On the one hand... / On the other hand...
              </div>
            </div>
          </div>
          <div class="panel" style="margin-top:12px">
            <b>Follow-up questions</b>
            <ul style="color:var(--muted);line-height:1.8;margin:10px 0 0 18px">
              ${pack.followups.map(q => `<li>${q}</li>`).join("")}
            </ul>
          </div>
          <div class="mini-actions">
            <button class="btn" id="startSpeakTimer">Start 2-minute timer</button>
            <button class="ghost" id="doneSpeak">Mark as done</button>
          </div>
          <div class="feedback" id="speakFeedback">Practice out loud, then record yourself on your phone if needed.</div>
        </div>
      `;

      document.getElementById("startSpeakTimer").onclick = () => {
        startTimer(2);
        const fb = document.getElementById("speakFeedback");
        fb.className = "feedback good";
        fb.textContent = "Speaking timer started for 2 minutes.";
      };
      document.getElementById("doneSpeak").onclick = () => {
        const fb = document.getElementById("speakFeedback");
        fb.className = "feedback good";
        fb.textContent = "Marked as completed.";
        saveProgress(Math.min(100, state.progress + 10));
      };
    }

    document.getElementById("closeModalBtn").onclick = closeModal;
    modal.addEventListener("click", (e) => { if (e.target === modal) closeModal(); });

    document.getElementById("startReadingBtn").onclick = () => {
      state.section = "reading";
      renderAll();
      const firstPack = examData[state.level].reading.packs[0];
      openPack(firstPack);
    };

    document.getElementById("startWritingBtn").onclick = () => {
      state.section = "writing";
      renderAll();
      const firstPack = examData[state.level].writing.packs[0];
      openPack(firstPack);
    };

    document.querySelectorAll(".pill[data-level]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll(".pill[data-level]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        state.level = btn.dataset.level;
        state.section = "reading";
        renderAll();
      });
    });

    renderAll();
    updateTimer();
    saveProgress(state.progress);
  </script>
</body>
</html>