module.exports = async (req, res) => {
    if (req.method !== 'POST') return res.status(405).send('Method Not Allowed');

    const { query } = req.body;
    const API_KEY = process.env.GROQ_API_KEY; 

    try {
        const response = await fetch(`https://api.groq.com/openai/v1/chat/completions`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    { "role": "system", "content": "Aap Mayank ke AI assistant hain. Hamesha helpful aur respectful rahen." },
                    { "role": "user", "content": query }
                ]
            })
        });

        const data = await response.json();
        res.status(200).json(data);
    } catch (error) {
        res.status(500).json({ error: "Groq Failed", details: error.message });
    }
};
