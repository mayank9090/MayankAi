import os
import base64
from flask import Flask, render_template_string, request, jsonify
from groq import Groq

app = Flask(__name__)

# Config
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
ACCESS_KEY = os.environ.get("ACCESS_KEY", "MAYANKAI")

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

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; }

        body { background: var(--bg); color: var(--text); height: 100dvh; display: flex; justify-content: center; overflow: hidden; }

        #login-overlay {
            position: fixed; inset: 0; background: #050505; z-index: 1000;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .login-card {
            background: #111214; padding: 40px 25px; border-radius: 24px;
            width: 90%; max-width: 350px; text-align: center; border: 1px solid var(--border);
        }
        .login-input {
            width: 100%; padding: 14px; background: #000; border: 1px solid #333;
            color: white; border-radius: 12px; text-align: center; margin-bottom: 20px; outline: none;
        }
        .access-btn {
            background: transparent; border: 2px solid var(--accent); color: var(--accent);
            padding: 14px; width: 100%; border-radius: 35px; font-weight: bold; cursor: pointer;
        }

        .app-shell {
            display: none; width: 100%; max-width: 800px; height: 100dvh;
            background: var(--card); flex-direction: column; position: relative;
        }

        header {
            padding: 15px 20px; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center; flex-shrink: 0;
        }

        .logo { font-weight: 700; font-size: 1.2rem; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        #chat-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 100px; }

        /* --- QUICK ACTION CARDS --- */
        .quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 10px; }
        .q-card { background: var(--ai-bubble); border: 1px solid var(--border); padding: 15px; border-radius: 16px; cursor: pointer; transition: 0.2s; }
        .q-card:active { transform: scale(0.95); background: rgba(0, 210, 255, 0.1); }
        .q-card span { display: block; font-size: 1.3rem; margin-bottom: 5px; }
        .q-card p { font-size: 0.85rem; font-weight: 700; color: var(--text); }

        .bubble { max-width: 85%; padding: 12px 16px; border-radius: 18px; font-size: 0.95rem; line-height: 1.5; }
        .user-bubble { background: var(--user-bubble); color: var(--user-text); align-self: flex-end; border-bottom-right-radius: 4px; }
        .ai-bubble { background: var(--ai-bubble); border: 1px solid var(--border); align-self: flex-start; border-bottom-left-radius: 4px; }

        /* --- INPUT BOX FIX --- */
        .input-wrapper {
            position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
            width: 100%; max-width: 800px; padding: 12px; background: var(--bg);
            display: flex; gap: 8px; align-items: center; border-top: 1px solid var(--border);
            z-index: 100; transition: bottom 0.1s ease-out;
        }

        input#userInput {
            flex: 1; background: var(--ai-bubble); border: 1px solid var(--border);
            border-radius: 12px; padding: 12px 15px; color: var(--text); outline: none; font-size: 16px;
        }
        
        .icon-btn { background: var(--ai-bubble); border: 1px solid var(--border); color: var(--text); width: 45px; height: 45px; border-radius: 12px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; }
        .send-btn { background: var(--accent); color: white; border: none; width: 45px; height: 45px; border-radius: 12px; cursor: pointer; font-size: 1.2rem; }
        
        #preview-img { display: none; width: 45px; height: 45px; border-radius: 8px; object-fit: cover; border: 1px solid var(--accent); }

        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div class="login-card">
            <h3 style="margin-bottom: 20px; color:white;">MAYANK AI LOGIN</h3>
            <input type="password" id="passKey" class="login-input" placeholder="ENTER ACCESS KEY">
            <button class="access-btn" onclick="validateKey()">ACCESS TERMINAL</button>
        </div>
    </div>

    <div class="app-shell" id="mainApp">
        <header>
            <div class="logo">MAYANK AI</div>
            <button class="icon-btn" style="width:auto; padding:0 10px; font-size:0.8rem;" onclick="toggleTheme()" id="themeBtn">🌙 DARK</button>
        </header>

        <div id="chat-area">
            <div class="ai-bubble bubble">Swagat hai Mayank! Kya help karun?</div>
            
            <div class="quick-grid" id="quickActions">
                <div class="q-card" onclick="quickMsg('Prompt generate: Is photo ka detailed prompt banao ')">
                    <span>🖼️</span> <p>Prompt Generate</p>
                </div>
                <div class="q-card" onclick="quickMsg('Explore Cricket: Cricket news updates ')">
                    <span>🏏</span> <p>Explore Cricket</p>
                </div>
                <div class="q-card" onclick="quickMsg('Write anything: Ek chhota essay likho ')">
                    <span>📝</span> <p>Write anything</p>
                </div>
                <div class="q-card" onclick="quickMsg('Help me learn: Ise easy bhasha mein samjhao ')">
                    <span>🎓</span> <p>Help me learn</p>
                </div>
            </div>
        </div>

        <div class="input-wrapper">
            <label class="icon-btn" for="file-upload">📷</label>
            <input type="file" id="file-upload" hidden accept="image/*" onchange="previewImage(this)">
            <img id="preview-img">
            <input type="text" id="userInput" placeholder="Message or upload image..." autocomplete="off">
            <button class="send-btn" onclick="send()">🚀</button>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chat-area');
        const input = document.getElementById('userInput');
        let currentPass = "";
        let base64Image = null;

        function validateKey() {
            const k = document.getElementById('passKey').value;
            if(!k) return;
            currentPass = k;
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('mainApp').style.display = 'flex';
        }

        function previewImage(input) {
            const file = input.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    base64Image = e.target.result;
                    document.getElementById('preview-img').src = base64Image;
                    document.getElementById('preview-img').style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }

        function quickMsg(txt) {
            input.value = txt;
            input.focus();
        }

        function toggleTheme() {
            if (document.body.hasAttribute('data-theme')) {
                document.body.removeAttribute('data-theme');
                document.getElementById('themeBtn').innerText = "🌙 DARK";
            } else {
                document.body.setAttribute('data-theme', 'light');
                document.getElementById('themeBtn').innerText = "☀️ LIGHT";
            }
        }

        async function send() {
            const msg = input.value.trim();
            if(!msg && !base64Image) return;

            document.getElementById('quickActions').style.display = 'none';
            chatArea.innerHTML += `<div class="user-bubble bubble">${msg || "Sent a photo"}</div>`;
            
            const imgData = base64Image;
            input.value = '';
            base64Image = null;
            document.getElementById('preview-img').style.display = 'none';
            
            const tempId = "ai-" + Date.now();
            chatArea.innerHTML += `<div class="ai-bubble bubble" id="${tempId}">Thinking...</div>`;
            chatArea.scrollTop = chatArea.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, password: currentPass, image: imgData})
                });
                const data = await res.json();
                if(res.status === 401) { location.reload(); return; }
                document.getElementById(tempId).innerHTML = marked.parse(data.reply);
            } catch (err) {
                document.getElementById(tempId).innerText = "Error: System Offline.";
            }
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                const wrapper = document.querySelector('.input-wrapper');
                const offset = window.innerHeight - window.visualViewport.height;
                wrapper.style.bottom = offset > 0 ? `${offset}px` : '0';
            });
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
    data = request.json
    if data.get("password") != ACCESS_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_msg = data.get("message")
    image_data = data.get("image")

    try:
        if image_data:
            # Vision Logic
            base64_img = image_data.split(",")[1]
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"Analyze this image and generate a highly detailed prompt for an image generator (like Midjourney). Also respond in smart Hinglish about the analysis. User message: {user_msg}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }]
            )
        else:
            # Standard Text Logic
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are Mayank AI, a premium assistant. Use smart Hinglish."},
                    {"role": "user", "content": user_msg}
                ]
            )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"reply": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
