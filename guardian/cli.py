import argparse
import os
import sys
import yaml
from .core import LogAnalyzer
from .notifiers import send_notification
from .storage import save_alerts_json, save_alerts_csv

def format_alert(alert):
    return (f"[SecurityLogGuardian Alert 🚨]\n"
            f"Suspicious activity detected!\n"
            f"IP: {alert['ip']}\n"
            f"Type: {alert['type'].capitalize()}\n"
            f"Score: {alert['score']}/100\n"
            f"Time: {alert['time']}\n"
            f"Log: {alert['log']}\n")

def main():
    parser = argparse.ArgumentParser(description='SecurityLog Guardian CLI')
    parser.add_argument('--config', required=True, help='Path to config YAML')
    parser.add_argument('--output', help='Output file for alerts (optional)')
    parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    args = parser.parse_args()

    analyzer = LogAnalyzer(args.config)
    alerts = analyzer.analyze()

    if not alerts:
        print('No suspicious activity detected.')
        sys.exit(0)

    # Output alerts
    if args.format == 'json':
        path = save_alerts_json(alerts)
    else:
        path = save_alerts_csv(alerts)
    if args.output and path:
        os.rename(path, args.output)
        path = args.output
    if path:
        print(f"Alerts saved to {path}")

    # Send notifications using new unified function
    for alert in alerts:
        send_notification(alert, analyzer.config)

if __name__ == '__main__':
    main() 