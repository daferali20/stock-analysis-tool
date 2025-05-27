def check_alerts(analysis: dict) -> list:
    alerts = []

    if analysis.get("final_rating", 0) >= 4.5:
        alerts.append("📈 تنبيه: السهم حصل على تقييم شراء قوي.")
    if analysis.get("roe", 100) < 5:
        alerts.append("⚠️ تنبيه: عائد حقوق الملكية منخفض (ROE < 5%).")
    if analysis.get("de_ratio", 0) > 2:
        alerts.append("🚨 تنبيه: نسبة الدين لحقوق الملكية مرتفعة (خطر مالي).")
    st.audio("https://actions.google.com/sounds/v1/alarms/digital_watch_alarm_long.ogg")
from src.email_alert import send_email_alert

# مثال استخدام
send_email_alert("تنبيه سهم مهم", "السهم AAPL حصل على تقييم شراء قوي.")

    return alerts
