import smtplib
from email.mime.text import MIMEText

def send_email_alert(message):
    config = load_config()
    smtp = config.get('smtp', {})
    try:
        msg = MIMEText(message)
        msg['Subject'] = 'تنبيه سهم'
        msg['From'] = smtp['email']
        msg['To'] = smtp['to']
        with smtplib.SMTP(smtp['host'], smtp['port']) as server:
            server.starttls()
            server.login(smtp['email'], smtp['password'])
            server.send_message(msg)
    except Exception as e:
        print(f"خطأ في إرسال البريد: {e}")
