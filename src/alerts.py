def check_alerts(analysis: dict) -> list:
    alerts = []

    if analysis.get("final_rating", 0) >= 4.5:
        alerts.append("📈 تنبيه: السهم حصل على تقييم شراء قوي.")
    if analysis.get("roe", 100) < 5:
        alerts.append("⚠️ تنبيه: عائد حقوق الملكية منخفض (ROE < 5%).")
    if analysis.get("de_ratio", 0) > 2:
        alerts.append("🚨 تنبيه: نسبة الدين لحقوق الملكية مرتفعة (خطر مالي).")
    
    return alerts
