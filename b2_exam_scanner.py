from flask import Flask, render_template_string, jsonify

app = Flask(__name__)

# ================= DATA =================
exam_data = {
    "reading": [
        {
            "question": "What is the main idea of the text?",
            "options": ["Shopping", "Sustainability", "Travel", "Sports"],
            "answer": 1
        }
    ],
    "grammar": [
        {
            "question": "She ____ to school every day.",
            "options": ["go", "goes", "going", "gone"],
            "answer": 1
        }
    ]
}

# ================= HTML (EMBEDDED) =================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>TELC B2 Simulator</title>

<style>
body {
    background: #0b1020;
    color: white;
    font-family: Arial;
    padding: 20px;
}
h1 {
    color: #7c8cff;
}
.card {
    background: #151f3a;
    padding: 20px;
    margin: 10px 0;
    border-radius: 10px;
}
button {
    margin: 5px;
    padding: 10px;
    border: none;
    background: #7c8cff;
    color: white;
    cursor: pointer;
    border-radius: 5px;
}
button:hover {
    background: #5a6cff;
}
</style>

</head>

<body>

<h1>TELC B2 Simulator</h1>
<div id="app"></div>

<script>
async function loadExam() {
    const res = await fetch('/api/exam');
    const data = await res.json();

    const app = document.getElementById('app');

    Object.keys(data).forEach(section => {
        const sectionDiv = document.createElement('div');
        sectionDiv.innerHTML = `<h2>${section.toUpperCase()}</h2>`;

        data[section].forEach(q => {
            const card = document.createElement('div');
            card.className = 'card';

            let optionsHTML = '';
            q.options.forEach((opt, i) => {
                optionsHTML += `
                    <button onclick="checkAnswer(${q.answer}, ${i})">
                        ${opt}
                    </button>
                `;
            });

            card.innerHTML = `
                <p>${q.question}</p>
                ${optionsHTML}
            `;

            sectionDiv.appendChild(card);
        });

        app.appendChild(sectionDiv);
    });
}

function checkAnswer(correct, selected) {
    if (correct === selected) {
        alert("Correct!");
    } else {
        alert("Wrong!");
    }
}

loadExam();
</script>

</body>
</html>
"""

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/exam")
def get_exam():
    return jsonify(exam_data)

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)