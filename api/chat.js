export default async function handler(req, res) {
    // Sirf POST request allow karenge
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { query } = req.body;
    const API_KEY = process.env.GEMINI_KEY;

    if (!API_KEY) {
        return res.status(500).json({ error: "API Key missing in Vercel settings!" });
    }

    try {
        const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${API_KEY}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                contents: [{ parts: [{ text: query }] }]
            })
        });

        const data = await response.json();
        return res.status(200).json(data);
    } catch (error) {
        return res.status(500).json({ error: "Mayank AI Uplink Failed: " + error.message });
    }
}
