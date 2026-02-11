module.exports = async (req, res) => {
    if (req.method !== 'POST') return res.status(405).send('Only POST allowed');

    const { query } = req.body;
    const API_KEY = process.env.GROQ_API_KEY; 

    try {
        const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "model": "llama-3.3-70b-versatile",
                "messages": [{ "role": "user", "content": query }]
            })
        });

        const data = await response.json();
        
        // Groq se humein 'choices[0].message.content' milta hai
        // Hum ise simple karke bhejenge taaki HTML confuse na ho
        if (data.choices && data.choices[0]) {
            res.status(200).json({ text: data.choices[0].message.content });
        } else {
            res.status(500).json({ error: "Invalid Response from Groq" });
        }
    } catch (error) {
        res.status(500).json({ error: "Fetch Failed", message: error.message });
    }
};
