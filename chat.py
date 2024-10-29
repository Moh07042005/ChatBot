from flask import Flask, request, jsonify
from openai import OpenAI

app = Flask(__name__)

# Festgelegter API-Schlüssel und Meta-Prompt
api_key = "YOUR_API_KEY_HERE"
META_PROMPT = "Du bist eine Person welche basierend auf den dir gegebenen Informationen vorschläge bezüglich Büchern macht. Wenn du nicht genug informationen hast kannst du den Nutzer nach mehr fragen."

client = OpenAI(api_key=api_key)

# Initialisiere die Chat-Historie
chat_history = []

# Die Haupt-HTML-Seite
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chatbot Interface</title>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
        input, textarea { width: 100%; max-width: 600px; padding: 10px; margin: 10px 0; }
        button { padding: 10px 20px; font-size: 16px; }
        .chat-container { margin-top: 30px; text-align: left; max-width: 600px; margin: auto; }
        .user-msg { color: #333; }
        .bot-msg { color: #007BFF; }
    </style>
</head>
<body>
    <h1>Chatbot Interface</h1>
    <div class="chat-container" id="chat-container">
        <h3>Chat</h3>
    </div>
    <input type="text" id="user-input" placeholder="Schreibe eine Nachricht...">
    <button onclick="sendMessage()">Senden</button>

    <script>
        async function sendMessage() {
            const userInput = document.getElementById('user-input').value;
            if (!userInput) return;

            // Anzeige der Benutzernachricht
            document.getElementById('chat-container').innerHTML += `<p class="user-msg"><strong>Du:</strong> ${userInput}</p>`;
            document.getElementById('user-input').value = '';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_message: userInput })
            });

            const data = await response.json();
            
            // Update chat with entire history
            document.getElementById('chat-container').innerHTML = '';
            data.chat_history.forEach(message => {
                const role = message.role === "user" ? "Du" : "Bot";
                const className = message.role === "user" ? "user-msg" : "bot-msg";
                document.getElementById('chat-container').innerHTML += `<p class="${className}"><strong>${role}:</strong> ${message.content}</p>`;
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return html_template

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data['user_message']
    
    # Füge die Benutzernachricht zur Chat-Historie hinzu
    chat_history.append({"role": "user", "content": user_message})
    
    try:
        # Anfrage an die OpenAI-API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": META_PROMPT}] + chat_history
        )
        bot_response = response.choices[0].message.content
        
        # Füge die Bot-Antwort zur Chat-Historie hinzu
        chat_history.append({"role": "assistant", "content": bot_response})
    except Exception as e:
        bot_response = "Error: " + str(e)
    
    return jsonify({"bot_response": bot_response, "chat_history": chat_history})

if __name__ == '__main__':
    app.run(debug=True)
