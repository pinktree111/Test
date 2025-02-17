from flask import Flask, render_template_string, Response
import requests
import json

app = Flask(__name__)

# URL del JSON da cui scaricare i dati
JSON_URL = "https://vavoo.to/channels"

# Template HTML aggiornato
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
    .note {
      text-align: center;
      font-size: 12px;
      color: #777;
      display: none;
      margin-top: 10px;
      margin-bottom: 20px;
      line-height: 1.4;
      max-width: 600px;
      margin-left: auto;
      margin-right: auto;
    }
    .toggle-note {
      display: block;
      width: 140px;
      margin: 15px auto 30px;
      padding: 8px;
      text-align: center;
      background-color: #dc3545;
      color: white;
      text-decoration: none;
      border-radius: 5px;
      font-weight: bold;
      font-size: 16px;
    }
    .toggle-note:hover {
      background-color: #c82333;
    }
    .download-button {
      display: block;
      width: 100px;
      margin: 0 auto 20px;
      padding: 8px;
      text-align: center;
      background-color: #28a745;
      color: white;
      text-decoration: none;
      border-radius: 5px;
      font-weight: bold;
      font-size: 16px;
    }
    .download-button:hover {
      background-color: #218838;
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

    function toggleNote() {
      var note = document.getElementById('note');
      if (note.style.display === 'none' || note.style.display === '') {
        note.style.display = 'block';
      } else {
        note.style.display = 'none';
      }
    }
  </script>
</head>
<body>
  <h1>Canali Italiani</h1>
  <a class="download-button" href="/download">💾m3u</a>
  <a class="toggle-note" onclick="toggleNote()">🚨SE NON PARTE</a>
  <div class="note" id="note">
    In caso cliccando non si apre direttamente il canale, provare a installare VLC e cliccare sulla sua icona. 
    Oppure clicca su "COPIA" e incolla il link nel tuo player preferito.
  </div>
  <input type="text" id="search" onkeyup="searchChannels()" placeholder="Cerca canale...">
  <ul>
    {% for name, link in channels %}
    <li>
      <a href="{{ link }}" target="_blank" class="channel-name">{{ name }}</a>
      <div class="icons">
        <span class="icon-label">Apri:</span> 
        <a href="{{ link }}" target="_blank" title="Guarda qui">Qui ▶️</a> |
        <a href="vlc://{{ link | replace('https://', '') }}" title="Apri con VLC">VLC 🎥</a> |
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

@app.route("/download")
def download_m3u():
    channels = get_italy_channels()
    m3u_content = "#EXTM3U\n"
    for name, link in channels:
        m3u_content += f"#EXTINF:-1,{name}\n{link}\n"
    return Response(m3u_content, mimetype="application/x-mpegURL",
                    headers={"Content-Disposition": "attachment;filename=canali.m3u"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
