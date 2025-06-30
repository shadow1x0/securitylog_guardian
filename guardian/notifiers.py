import requests
import smtplib
import logging
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, List
from collections import defaultdict

# Throttling: track last notification time per IP+type
last_notifications = defaultdict(float)
THROTTLE_SECONDS = 300  # 5 minutes

def send_telegram_alert(token: str, chat_id: str, message: str) -> bool:
    """Send alert via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Telegram alert failed: {e}")
        return False

def send_slack_alert(webhook_url: str, message: str, channel: Optional[str] = None) -> bool:
    """Send alert via Slack webhook."""
    payload = {"text": message}
    if channel:
        payload["channel"] = channel
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logging.error(f"Slack alert failed: {e}")
        return False

def send_email_alert(smtp_server: str, smtp_port: int, username: str, 
                    password: str, to_email: str, subject: str, message: str) -> bool:
    """Send alert via SMTP email."""
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    try:
        with smtplib.SMTP(smtp_server, smtp_port, timeout=10) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, to_email, msg.as_string())
        return True
    except Exception as e:
        logging.error(f"Email alert failed: {e}")
        return False

def log_alert(message: str) -> None:
    """Log alert to system logs."""
    logging.warning(f"[SecurityLogGuardian Alert] {message}")

def should_throttle(ip: str, alert_type: str) -> bool:
    """Check if notification should be throttled for this IP+type."""
    key = f"{ip}:{alert_type}"
    now = time.time()
    if now - last_notifications[key] < THROTTLE_SECONDS:
        return True
    last_notifications[key] = now
    return False

def send_notification(alert: Dict, config: Dict) -> bool:
    """Send notification via all configured channels with throttling."""
    if should_throttle(alert['ip'], alert['type']):
        logging.info(f"Throttling notification for {alert['ip']}:{alert['type']}")
        return False
    
    message = format_alert_message(alert)
    sent = False
    
    # Telegram
    telegram_config = config.get('notification', {})
    if telegram_config.get('telegram_token') and telegram_config.get('telegram_chat_id'):
        if telegram_config['telegram_token'] != 'YOUR_TOKEN':
            sent = send_telegram_alert(
                telegram_config['telegram_token'],
                telegram_config['telegram_chat_id'],
                message
            ) or sent
    
    # Slack
    slack_config = config.get('notification', {})
    if slack_config.get('slack_webhook_url'):
        sent = send_slack_alert(
            slack_config['slack_webhook_url'],
            message,
            slack_config.get('slack_channel')
        ) or sent
    
    # Email
    email_config = config.get('notification', {})
    if all(k in email_config for k in ['smtp_server', 'smtp_port', 'email_username', 'email_password', 'email_to']):
        sent = send_email_alert(
            email_config['smtp_server'],
            email_config['smtp_port'],
            email_config['email_username'],
            email_config['email_password'],
            email_config['email_to'],
            f"SecurityLog Guardian Alert - {alert['type']}",
            message
        ) or sent
    
    # Fallback to logging
    if not sent:
        log_alert(message)
    
    return sent

def format_alert_message(alert: Dict) -> str:
    """Format alert as HTML message for notifications."""
    return (f"🚨 <b>SecurityLog Guardian Alert</b>\n\n"
            f"<b>IP:</b> {alert['ip']}\n"
            f"<b>Type:</b> {alert['type'].capitalize()}\n"
            f"<b>Score:</b> {alert['score']}/100\n"
            f"<b>Time:</b> {alert['time']}\n"
            f"<b>Log:</b> {alert['log']}\n"
            f"<b>Method:</b> {alert.get('method', 'N/A')}\n"
            f"<b>Path:</b> {alert.get('path', 'N/A')}\n"
            f"<b>Status:</b> {alert.get('status', 'N/A')}\n"
            f"<b>Pattern:</b> {alert.get('pattern', 'N/A')}\n\n"
            f"<code>{alert['line']}</code>") 