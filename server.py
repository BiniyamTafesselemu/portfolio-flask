from flask import Flask, render_template, request, redirect
from dotenv import load_dotenv
import csv
import requests
import os

load_dotenv()

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


@app.route('/')
def my_home():
    return render_template('index.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database2:
        csv_writer = csv.writer(database2, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([
            data.get("name", ""),
            data.get("email", ""),
            data.get("telegram", ""),
            data.get("phone", ""),
            data.get("message", "")
        ])

def send_to_telegram(data):
    name = data.get("name", "N/A")
    email = data.get("email", "N/A")
    telegram = data.get("telegram", "N/A")
    phone = data.get("phone", "N/A") or "Not provided"
    message = data.get("message", "N/A")

    text = (
        f"📩 <b>New Contact Form Submission</b>\n\n"
        f"<b>Name:</b> {name}\n"
        f"<b>Email:</b> {email}\n"
        f"<b>Telegram:</b> {telegram}\n"
        f"<b>Phone:</b> {phone}\n"
        f"<b>Message:</b>\n{message}"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception:
        pass


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            send_to_telegram(data)
            return redirect('/thankyou.html')
        except Exception:
            return 'did not save to database'
    else:
        return 'something went wrong. Try again!!'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    # Werkzeug's debug reloader installs signal handlers; many hosts (e.g. Streamlit Cloud) reject that.
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
