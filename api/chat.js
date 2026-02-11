export default async function handler(req, res) {
    if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });
    const { query } = req.body;
    const API_KEY = process.env.GEMINI_KEY; 
    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contents: [{ parts: [{ text: query }] }] })
        });
        const data = await response.json();
        res.status(200).json(data);
    } catch (e) { res.status(500).json({ error: "Server Error" }); }
}
