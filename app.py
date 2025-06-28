from flask import Flask, request, render_template, jsonify
from datetime import datetime
from user_agents import parse
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/log', methods=['POST'])
def log_visitor():
    data = request.json
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    ua_string = request.headers.get('User-Agent')
    user_agent = parse(ua_string)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    try:
        geo = requests.get(f"https://ipwho.is/{ip}").json()
        city = geo.get("city", "N/A")
        country = geo.get("country", "N/A")
        isp = geo.get("connection", {}).get("org", "N/A")
    except:
        city = country = isp = "N/A"

    log_entry = (
        f"[{timestamp}] IP: {ip}\n"
        f"  → Location: {city}, {country}\n"
        f"  → ISP: {isp}\n"
        f"  → Device: {user_agent.device.family}, OS: {user_agent.os.family}, Browser: {user_agent.browser.family}\n"
        f"  → Screen: {data.get('screen')} | Lang: {data.get('lang')} | Timezone: {data.get('timezone')}\n"
        f"  → User-Agent: {ua_string}\n\n"
    )

    with open("visitor_log.txt", "a") as f:
        f.write(log_entry)

    return jsonify({"status": "logged"})
@app.route('/dashboard')
def dashboard():
    try:
        with open("visitor_log.txt", "r") as f:
            logs = f.read().replace("\n", "<br>")
    except:
        logs = "No logs found."
    
    return f"""
    <html>
      <head>
        <title>Visitor Logs</title>
        <style>
          body {{
            background: #111;
            color: #0f0;
            font-family: monospace;
            padding: 20px;
          }}
        </style>
      </head>
      <body>
        <h2>Visitor Logs 📄</h2>
        <div>{logs}</div>
      </body>
    </html>
    """

