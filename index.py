import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Groq Client - Vercel Settings mein GROQ_API_KEY add karna mat bhulna
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="theme-color" content="#050505">
    <title>Mayank AI | Pro</title>
    
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --accent: #00d2ff;
            --bg: #050505;
            --card: rgba(23, 23, 23, 0.8);
            --text: #ffffff;
            --border: rgba(255, 255, 255, 0.1);
            --ai-bubble: rgba(255, 255, 255, 0.05);
            --user-bubble: #ffffff;
            --user-text: #000000;
        }

        [data-theme="light"] {
            --bg: #f9fafb;
            --card: rgba(255, 255, 255, 0.9);
            --text: #111827;
            --border: rgba(0, 0, 0, 0.08);
            --ai-bubble: #f3f4f6;
            --user-bubble: #00d2ff;
            --user-text: #ffffff;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }

        body { background: var(--bg); color: var(--text); height: 100vh; display: flex; justify-content: center; overflow: hidden; }

        .app-shell {
            width: 100%; max-width: 800px; height: 100vh;
            background: var(--card); backdrop-filter: blur(20px);
            display: flex; flex-direction: column; position: relative;
        }

        @media (min-width: 768px) {
            .app-shell { height: 90vh; margin-top: 5vh; border: 1px solid var(--border); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        }

        header {
            padding: 18px 24px; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }

        .logo { font-weight: 700; font-size: 1.3rem; letter-spacing: -0.5px; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        .controls { display: flex; gap: 10px; }
        .btn-icon { background: var(--ai-bubble); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 12px; cursor: pointer; font-size: 0.8rem; font-weight: 600; }

        #chat-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; padding-bottom: 100px; }

        .msg-row { display: flex; width: 100%; animation: slideUp 0.3s ease; }
        .user-row { justify-content: flex-end; }
        .ai-row { justify-content: flex-start; }

        .bubble { max-width: 85%; padding: 14px 18px; border-radius: 20px; font-size: 0.95rem; line-height: 1.6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .user-bubble { background: var(--user-bubble); color: var(--user-text); border-bottom-right-radius: 4px; font-weight: 500; }
        .ai-bubble { background: var(--ai-bubble); border: 1px solid var(--border); border-bottom-left-radius: 4px; }

        /* Thinking Animation */
        .dot-flashing { font-size: 0.8rem; opacity: 0.5; font-style: italic; }

        .input-wrapper {
            position: absolute; bottom: 0; width: 100%; padding: 20px;
            background: linear-gradient(transparent, var(--bg) 50%);
            display: flex; gap: 12px; align-items: center;
        }

        input {
            flex: 1; background: var(--ai-bubble); border: 1px solid var(--border);
            border-radius: 16px; padding: 14px 20px; color: var(--text); outline: none; font-size: 16px;
        }
        input:focus { border-color: var(--accent); }

        .send-btn {
            background: var(--accent); color: white; border: none;
            width: 50px; height: 50px; border-radius: 16px;
            display: flex; justify-content: center; align-items: center;
            cursor: pointer; font-size: 1.2rem; box-shadow: 0 8px 15px rgba(0, 210, 255, 0.3);
        }

        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        /* Code Block Styling */
        pre { background: #000; color: #00d2ff; padding: 15px; border-radius: 12px; margin: 10px 0; overflow-x: auto; font-size: 0.85rem; }
    </style>
</head>
<body>

    <div class="app-shell">
        <header>
            <div class="logo">MAYANK AI</div>
            <div class="controls">
                <button class="btn-icon" onclick="toggleTheme()" id="themeBtn">🌙 DARK</button>
            </div>
        </header>

        <div id="chat-area">
            <div class="msg-row ai-row">
                <div class="ai-bubble bubble">Swagat hai Mayank! Aaj main aapki kya madad kar sakta hoon?</div>
            </div>
        </div>

        <div class="input-wrapper">
            <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
            <button class="send-btn" onclick="send()">🚀</button>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chat-area');
        const input = document.getElementById('userInput');
        const themeBtn = document.getElementById('themeBtn');

        function toggleTheme() {
            if (document.body.hasAttribute('data-theme')) {
                document.body.removeAttribute('data-theme');
                themeBtn.innerText = "🌙 DARK";
            } else {
                document.body.setAttribute('data-theme', 'light');
                themeBtn.innerText = "☀️ LIGHT";
            }
        }

        async function send() {
            const msg = input.value.trim();
            if(!msg) return;

            chatArea.innerHTML += `<div class="msg-row user-row"><div class="user-bubble bubble">${msg}</div></div>`;
            input.value = '';
            chatArea.scrollTop = chatArea.scrollHeight;

            const tempId = "ai-" + Date.now();
            chatArea.innerHTML += `<div class="msg-row ai-row"><div class="ai-bubble bubble" id="${tempId}"><span class="dot-flashing">Mayank AI is thinking...</span></div></div>`;
            chatArea.scrollTop = chatArea.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                document.getElementById(tempId).innerHTML = marked.parse(data.reply);
            } catch (err) {
                document.getElementById(tempId).innerText = "Error: Check API Key or Internet.";
            }
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        input.addEventListener("keypress", (e) => { if(e.key === "Enter") send(); });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are Mayank AI, a premium and professional personal assistant. You respond in natural Hinglish. Be smart, concise, and helpful."},
                {"role": "user", "content": user_msg}
            ]
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Maaf kijiye, error aaya: {str(e)}"})
