from flask import Flask, render_template_string
import requests

app = Flask(__name__)

JSON_URL = "https://vavoo.to/channels"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="it">
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Canali Italiani</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f4f9;
      padding: 20px;
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
    ul {
      list-style: none;
      padding: 0;
    }
    li {
      background: #fff;
      margin: 10px 0;
      padding: 15px;
      border-radius: 8px;
      box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .channel-name {
      font-size: 18px;
      color: #007BFF;
      text-decoration: none;
    }
    .channel-name:hover {
      text-decoration: underline;
    }
    .icons {
      margin-top: 5px;
    }
    .icons a, .icons span {
      margin-right: 10px;
      font-size: 20px;
      text-decoration: none;
      cursor: pointer;
      color: #555;
    }
    .icons a:hover, .icons span:hover {
      opacity: 0.8;
    }
    .copy-msg {
      display: none;
      font-size: 12px;
      color: #333;
    }
    .icon-label {
      font-size: 14px;
      color: #333;
      margin-right: 5px;
      font-weight: bold;
    }
  </style>
  <script>
    function searchChannels() {
      var input = document.getElementById('search').value.toLowerCase();
      var items = document.querySelectorAll('ul li');
      items.forEach(function(item) {
        var text = item.innerText.toLowerCase();
        item.style.display = text.includes(input) ? 'block' : 'none';
      });
    }

    function copyToClipboard(link, msgElement) {
      if(navigator.clipboard) {
        navigator.clipboard.writeText(link).then(function() {
          showCopyMessage(msgElement);
        }).catch(function(err) {
          console.error('Errore nel copiare: ', err);
        });
      } else {
        var tempInput = document.createElement('input');
        tempInput.value = link;
        document.body.appendChild(tempInput);
        tempInput.select();
        document.execCommand('copy');
        document.body.removeChild(tempInput);
        showCopyMessage(msgElement);
      }
    }

    function showCopyMessage(msgElement) {
      msgElement.style.display = 'inline';
      setTimeout(function() {
        msgElement.style.display = 'none';
      }, 2000);
    }
  </script>
</head>
<body>
  <h1>Canali Italiani</h1>
  <input type="text" id="search" onkeyup="searchChannels()" placeholder="Cerca canale...">
  <ul>
    {% for name, link in channels %}
    <li>
      <!-- Nome del canale cliccabile (apre il link originale) -->
      <a href="{{ link }}" target="_blank" class="channel-name">{{ name }}</a>
      <div class="icons">
        <!-- Label esplicativa -->
        <span class="icon-label">Apri:</span> 
        <!-- ▶️ Apre direttamente il link nel browser -->
        <a href="{{ link }}" target="_blank" title="Guarda qui">Qui ▶️</a> |
        <!-- 🎥 Apre con VLC usando il deeplink vlc:// -->
        <a href="vlc://{{ link | replace('https://', '') }}" title="Apri con VLC">VLC 🎥</a> |
        <!-- 🖨️ Copia il link negli appunti -->
        <span onclick="copyToClipboard('{{ link }}', this.nextElementSibling)" title="Copia link">COPIA 🖨️</span>
        <span class="copy-msg">Copiato!</span>
      </div>
    </li>
    {% endfor %}
  </ul>
</body>
</html>
"""

def get_italy_channels():
    try:
        response = requests.get(JSON_URL)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Errore nel download del JSON: {e}")
        return []

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
    app.run(host="0.0.0.0", port=9999)
