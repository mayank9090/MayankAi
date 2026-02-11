module.exports = async (req, res) => {
    // CORS Headers taaki browser block na kare
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

    if (req.method === 'OPTIONS') return res.status(200).end();
    if (req.method !== 'POST') return res.status(405).send('Only POST allowed');

    const { query } = req.body;
    const API_KEY = process.env.GROQ_API_KEY; 

    if (!API_KEY) {
        return res.status(500).json({ error: "Environment Variable GROQ_API_KEY is missing!" });
    }

    try {
        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "model": "llama3-8b-8192", 
                "messages": [
                    { "role": "system", "content": "You are Mayank's AI assistant. Keep responses short and in Hindi." },
                    { "role": "user", "content": query }
                ],
                "temperature": 0.7
            })
        });

        const data = await response.json();
        
        if (data.choices && data.choices[0]) {
            // Hum 'text' key bhej rahe hain kyunki tera index.html 'data.text' dhoond raha hai
            res.status(200).json({ text: data.choices[0].message.content });
        } else {
            console.error("Groq Error Data:", data);
            res.status(500).json({ error: "Groq API Error", details: data });
        }
    } catch (error) {
        res.status(500).json({ error: "Server Crash", message: error.message });
    }
};
