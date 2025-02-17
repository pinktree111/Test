from flask import Flask, render_template_string
import requests
import json

app = Flask(__name__)

# URL del JSON da cui scaricare i dati
JSON_URL = "https://vavoo.to/channels"

# Template HTML aggiornato con icona di copia link
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Canali Italiani</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            padding: 20px;
            background-color: #f4f4f9;
        }
        h1 {
            text-align: center;
            color: #333;
        }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            margin-bottom: 20px;
            font-size: 18px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .grid {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .grid-item {
            position: relative;
            background: #fff;
            width: calc(50% - 10px);
            padding: 15px;
            box-sizing: border-box;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .grid-item a {
            text-decoration: none;
            color: #007BFF;
            font-size: 18px;
        }
        .grid-item a:hover {
            text-decoration: underline;
        }
        .copy-icon {
            position: absolute;
            bottom: 10px;
            left: 10px;
            font-size: 20px;
            color: #666;
            cursor: pointer;
        }
        .copy-icon:hover {
            color: #333;
        }
        @media (min-width: 600px) {
            .grid-item {
                width: calc(33.33% - 10px);
            }
        }
    </style>
    <script>
        function searchChannels() {
            var input = document.getElementById('search').value.toLowerCase();
            var items = document.querySelectorAll('.grid-item');
            items.forEach(function(item) {
                var text = item.innerText.toLowerCase();
                if (text.includes(input)) {
                    item.style.display = 'block';
                } else {
                    item.style.display = 'none';
                }
            });
        }

        function copyToClipboard(link) {
            navigator.clipboard.writeText(link).then(function() {
                alert("Link copiato: " + link);
            }).catch(function(err) {
                alert("Errore nel copiare il link: " + err);
            });
        }
    </script>
</head>
<body>
    <h1>Canali Italiani</h1>
    <input type="text" id="search" onkeyup="searchChannels()" placeholder="Cerca canale...">
    <div class="grid">
        {% for name, link in channels %}
        <div class="grid-item">
            <a href="{{ link }}" target="_blank">{{ name }}</a>
            <span class="copy-icon" onclick="copyToClipboard('{{ link }}')">📋</span>
        </div>
        {% endfor %}
    </div>
</body>
</html>
"""

def get_italy_channels():
    try:
        # Scarica il contenuto del file JSON
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel download del file JSON: {e}")
        return []

    # Filtra i canali con country "Italy"
    channels = []
    for item in data:
        if item.get("country") == "Italy":
            name = item.get("name", "Sconosciuto")
            id_value = item.get("id")
            if id_value:
                link = f"https://vavoo.to/play/{id_value}/index.m3u8"
                channels.append((name, link))

    return channels

@app.route("/")
def home():
    channels = get_italy_channels()
    return render_template_string(HTML_TEMPLATE, channels=channels)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8191)
