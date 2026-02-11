import os
import base64
from flask import Flask, render_template_string, request, jsonify, session
from groq import Groq

app = Flask(__name__)
# Memory ke liye secret key zaruri hai
app.secret_key = "mayank_ai_elite_key_99"

# Groq Client - Vercel Env se key uthayega
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Password logic
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

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Plus Jakarta Sans', sans-serif; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }

        body { background: var(--bg); color: var(--text); height: 100dvh; display: flex; justify-content: center; overflow: hidden; }

        #login-overlay {
            position: fixed; inset: 0; background: #050505; z-index: 999;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .login-card {
            background: #111214; padding: 40px 25px; border-radius: 24px;
            width: 90%; max-width: 350px; text-align: center; border: 1px solid var(--border);
            backdrop-filter: blur(10px); /* Glassmorphism touch */
        }
        .login-input {
            width: 100%; padding: 14px; background: #000; border: 1px solid #333;
            color: white; border-radius: 12px; text-align: center; margin-bottom: 20px; outline: none;
        }
        .access-btn {
            background: transparent; border: 2px solid var(--accent); color: var(--accent);
            padding: 14px; width: 100%; border-radius: 35px; font-weight: bold; cursor: pointer;
        }
        .footer-tag { font-size: 10px; opacity: 0.4; margin-top: 40px; text-align: center; letter-spacing: 1px; }

        .app-shell {
            display: none;
            width: 100%; max-width: 800px; height: 100dvh;
            background: var(--card); backdrop-filter: blur(20px);
            flex-direction: column; position: relative;
        }

        @media (min-width: 768px) {
            .app-shell { height: 90dvh; margin-top: 5dvh; border: 1px solid var(--border); border-radius: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        }

        header {
            padding: 18px 24px; border-bottom: 1px solid var(--border);
            display: flex; justify-content: space-between; align-items: center;
        }

        .logo { font-weight: 700; font-size: 1.3rem; letter-spacing: -0.5px; background: linear-gradient(90deg, #00d2ff, #3a7bd5); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }

        .controls { display: flex; gap: 10px; }
        .btn-icon { background: var(--ai-bubble); border: 1px solid var(--border); color: var(--text); padding: 8px 12px; border-radius: 12px; cursor: pointer; font-size: 0.8rem; font-weight: 600; }

        #chat-area { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 20px; scroll-behavior: smooth; padding-bottom: 120px; }

        /* --- QUICK ACTION CARDS UPDATE --- */
        .quick-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 10px; }
        .q-card { background: var(--ai-bubble); border: 1px solid var(--border); padding: 18px; border-radius: 20px; cursor: pointer; transition: 0.2s; text-align: left; }
        .q-card:active { transform: scale(0.95); background: rgba(0, 210, 255, 0.1); }
        .q-card span { font-size: 1.5rem; display: block; margin-bottom: 8px; }
        .q-card p { font-size: 0.9rem; font-weight: 700; color: var(--text); }

        .msg-row { display: flex; width: 100%; animation: slideUp 0.3s ease; }
        .user-row { justify-content: flex-end; }
        .ai-row { justify-content: flex-start; }

        .bubble { max-width: 85%; padding: 14px 18px; border-radius: 20px; font-size: 0.95rem; line-height: 1.6; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        .user-bubble { background: var(--user-bubble); color: var(--user-text); border-bottom-right-radius: 4px; font-weight: 500; }
        .ai-bubble { background: var(--ai-bubble); border: 1px solid var(--border); border-bottom-left-radius: 4px; }

        /* --- NEXT LEVEL INPUT REFINEMENT --- */
        .input-wrapper {
            position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
            width: 100%; max-width: 800px; padding: 20px;
            background: var(--bg);
            display: flex; gap: 12px; align-items: flex-end; /* Align to bottom for multiline */
            border-top: 1px solid var(--border);
            z-index: 100; transition: bottom 0.1s ease-out;
        }

        /* Using Textarea for auto-resize input */
        textarea#userInput {
            flex: 1; background: var(--ai-bubble); border: 1px solid var(--border);
            border-radius: 16px; padding: 14px 20px; color: var(--text); outline: none; 
            font-size: 16px; resize: none; max-height: 150px; min-height: 54px;
            overflow-y: auto; line-height: 1.5;
        }

        .icon-btn-upload { background: var(--ai-bubble); border: 1px solid var(--border); color: var(--text); width: 50px; height: 50px; border-radius: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; }
        .send-btn {
            background: var(--accent); color: white; border: none;
            width: 50px; height: 50px; border-radius: 16px;
            display: flex; justify-content: center; align-items: center;
            cursor: pointer; font-size: 1.2rem; box-shadow: 0 8px 15px rgba(0, 210, 255, 0.3); flex-shrink: 0;
        }
        
        #preview-img { display: none; width: 50px; height: 50px; border-radius: 12px; object-fit: cover; border: 2px solid var(--accent); margin-right: 5px; }

        @keyframes slideUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        pre { background: #000; color: #00d2ff; padding: 15px; border-radius: 12px; margin: 10px 0; overflow-x: auto; font-size: 0.85rem; }
    </style>
</head>
<body>

    <div id="login-overlay">
        <div style="margin-bottom: 30px; font-weight: 800; font-size: 1.5rem; letter-spacing: 2px;">
            MAYANK <span style="color:var(--accent)">AI ASSISTANCE</span>
        </div>
        <div class="login-card">
            <h3 style="margin-bottom: 20px;">🛡️ SECURE LOGIN</h3>
            <input type="password" id="passKey" class="login-input" placeholder="ENTER ACCESS KEY">
            <button class="access-btn" onclick="validateKey()">ACCESS TERMINAL</button>
        </div>
        <div class="footer-tag">© 2026 | DESIGNED BY <span style="color:var(--accent)">हिNDIE VLOGGER</span></div>
    </div>

    <div class="app-shell" id="mainApp">
        <header>
            <div class="logo">MAYANK AI</div>
            <div class="controls">
                <button class="btn-icon" id="voiceToggle" onclick="toggleVoice()">🔊 ON</button>
                <button class="btn-icon" onclick="toggleTheme()" id="themeBtn">🌙 DARK</button>
            </div>
        </header>

        <div id="chat-area">
            <div class="msg-row ai-row">
                <div class="ai-bubble bubble">Swagat hai Mayank! Aaj main aapki kya madad kar sakta hoon?</div>
            </div>

            <div class="quick-grid" id="quickActions">
                <div class="q-card" onclick="quickMsg('Prompt generate: Is photo ka mast prompt banao ')">
                    <span>🖼️</span> <p>Prompt generate</p>
                </div>
                <div class="q-card" onclick="quickMsg('YouTube Expert: Meri video ke liye viral script aur content idea do ')">
                    <span>🎬</span> <p>YouTube Expert</p>
                </div>
                <div class="q-card" onclick="quickMsg('Coding Guru: Is code logic ko simplify karo aur optimized code likho ')">
                    <span>💻</span> <p>Coding Guru</p>
                </div>
                <div class="q-card" onclick="quickMsg('Help me learn: Ise simple bhasha mein samjhao ')">
                    <span>🎓</span> <p>Help me learn</p>
                </div>
            </div>
        </div>

        <div class="input-wrapper">
            <label class="icon-btn-upload" for="file-upload">📷</label>
            <input type="file" id="file-upload" hidden accept="image/*" onchange="previewImage(this)">
            <img id="preview-img">
            <textarea id="userInput" placeholder="Ask me anything..." autocomplete="off" rows="1" oninput="autoResize(this)"></textarea>
            <button class="send-btn" onclick="send()">🚀</button>
        </div>
    </div>

    <script>
        const chatArea = document.getElementById('chat-area');
        const input = document.getElementById('userInput');
        const themeBtn = document.getElementById('themeBtn');
        let currentPass = "";
        let base64Image = null;
        let voiceEnabled = true;

        function validateKey() {
            const keyInput = document.getElementById('passKey').value;
            if(keyInput === "") { alert("Bhai Key toh daalo!"); return; }
            currentPass = keyInput;
            document.getElementById('login-overlay').style.display = 'none';
            document.getElementById('mainApp').style.display = 'flex';
        }

        // --- AUTO RESIZE INPUT ---
        function autoResize(el) {
            el.style.height = '54px';
            el.style.height = (el.scrollHeight) + 'px';
        }

        // --- VOICE ENGINE ---
        function toggleVoice() {
            voiceEnabled = !voiceEnabled;
            document.getElementById('voiceToggle').innerText = voiceEnabled ? "🔊 ON" : "🔇 OFF";
            if(!voiceEnabled) window.speechSynthesis.cancel();
        }

        function speak(text) {
            if(!voiceEnabled) return;
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(text.replace(/[#*`]/g, ''));
            utterance.rate = 1.1;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
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
            autoResize(input);
            input.focus();
        }

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
            if(!msg && !base64Image) return;

            document.getElementById('quickActions').style.display = 'none';
            chatArea.innerHTML += `<div class="msg-row user-row"><div class="user-bubble bubble">${msg || "Sent a photo"}</div></div>`;
            
            const imgToSend = base64Image;
            input.value = '';
            input.style.height = '54px';
            base64Image = null;
            document.getElementById('preview-img').style.display = 'none';
            
            chatArea.scrollTop = chatArea.scrollHeight;

            const tempId = "ai-" + Date.now();
            chatArea.innerHTML += `<div class="msg-row ai-row"><div class="ai-bubble bubble" id="${tempId}"><span class="dot-flashing">Thinking...</span></div></div>`;
            chatArea.scrollTop = chatArea.scrollHeight;

            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg, password: currentPass, image: imgToSend}) 
                });
                
                if (res.status === 401) { location.reload(); return; }

                const data = await res.json();
                document.getElementById(tempId).innerHTML = marked.parse(data.reply);
                speak(data.reply); // Voice response
            } catch (err) {
                document.getElementById(tempId).innerText = "Error: Connection issue.";
            }
            chatArea.scrollTop = chatArea.scrollHeight;
        }

        // --- KEYBOARD LIFT FIX ---
        if (window.visualViewport) {
            window.visualViewport.addEventListener('resize', () => {
                const wrapper = document.querySelector('.input-wrapper');
                const offset = window.innerHeight - window.visualViewport.height;
                wrapper.style.bottom = offset > 0 ? `${offset}px` : '0';
            });
        }

        input.addEventListener("keydown", (e) => { 
            if(e.key === "Enter" && !e.shiftKey) { 
                e.preventDefault();
                send(); 
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    session['history'] = [] # Reset memory on fresh load
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    if data.get("password") != ACCESS_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    user_msg = data.get("message")
    image_data = data.get("image")

    # --- MEMORY LOGIC & ADVANCED PERSONA ---
    if 'history' not in session:
        session['history'] = []

    persona = (
        "You are Mayank AI Elite, a professional assistant. "
        "Expertise: 1. YouTube Content & Viral Growth (suggest hooks, scripts) "
        "2. Professional Coding Guru (optimized logic, clean code) "
        "3. Portfolio Manager. "
        "Style: Smart, expert-level Hinglish. Remember context from previous chat history."
    )

    try:
        if image_data:
            base64_img = image_data.split(",")[1]
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f"{persona} Analyze this image and provide expert guidance. User: {user_msg}"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }]
            )
        else:
            # Memory messages build up
            messages = [{"role": "system", "content": persona}]
            # Last 6 chats for memory context
            for h in session['history'][-6:]:
                messages.append(h)
            messages.append({"role": "user", "content": user_msg})

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages
            )

        reply = response.choices[0].message.content
        
        # Save to memory
        session['history'].append({"role": "user", "content": user_msg})
        session['history'].append({"role": "assistant", "content": reply})
        session.modified = True

        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": f"System error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)
