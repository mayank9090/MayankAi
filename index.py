import os
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Groq Client Setup (Vercel Environment Variables se key uthayega)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Frontend HTML/CSS/JS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Personal AI Assistant</title>
    <style>
        :root { --bg: #0f172a; --chat-bg: #1e293b; --accent: #3b82f6; --text: #f8fafc; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; display: flex; justify-content: center; height: 100vh; }
        .container { width: 100%; max-width: 600px; display: flex; flex-direction: column; background: var(--chat-bg); border-left: 1px solid #334155; border-right: 1px solid #334155; }
        .header { padding: 20px; text-align: center; border-bottom: 1px solid #334155; font-weight: bold; font-size: 1.2rem; background: #1e293b; }
        #chat-window { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 12px; scroll-behavior: smooth; }
        .msg { padding: 12px 16px; border-radius: 12px; max-width: 80%; word-wrap: break-word; font-size: 0.95rem; line-height: 1.5; }
        .user { align-self: flex-end; background: var(--accent); color: white; border-bottom-right-radius: 2px; }
        .ai { align-self: flex-start; background: #334155; color: var(--text); border-bottom-left-radius: 2px; }
        .input-box { padding: 20px; display: flex; gap: 10px; border-top: 1px solid #334155; }
        input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #475569; background: #0f172a; color: white; outline: none; }
        button { padding: 0 20px; border-radius: 8px; border: none; background: var(--accent); color: white; cursor: pointer; font-weight: 600; }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🤖 AI Personal Assistant</div>
        <div id="chat-window">
            <div class="msg ai">Hello! Main Groq API se powered aapka assistant hoon. Main aapki kya help kar sakta hoon?</div>
        </div>
        <div class="input-box">
            <input type="text" id="userInput" placeholder="Yahan kuch likhein..." autocomplete="off">
            <button id="sendBtn" onclick="send()">Send</button>
        </div>
    </div>

    <script>
        const chatWin = document.getElementById('chat-window');
        const input = document.getElementById('userInput');
        const btn = document.getElementById('sendBtn');

        async function send() {
            const text = input.value.trim();
            if(!text) return;

            // Add User Message
            chatWin.innerHTML += `<div class="msg user">${text}</div>`;
            input.value = '';
            btn.disabled = true;
            chatWin.scrollTop = chatWin.scrollHeight;

            // Add Loading Placeholder
            const tid = "t" + Date.now();
            chatWin.innerHTML += `<div class="msg ai" id="${tid}">...</div>`;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                document.getElementById(tid).innerText = data.reply;
            } catch (err) {
                document.getElementById(tid).innerText = "Error: Connection lost.";
            }
            btn.disabled = false;
            chatWin.scrollTop = chatWin.scrollHeight;
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
                {"role": "system", "content": "You are a smart personal assistant. Use Hinglish."},
                {"role": "user", "content": user_msg}
            ]
        )
        return jsonify({"reply": completion.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": str(e)})

# Vercel doesn't need app.run()
