import os
import json
from datetime import datetime
import csv

ALERTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'alerts')

os.makedirs(ALERTS_DIR, exist_ok=True)

__all__ = ['save_alerts_json', 'save_alerts_csv']

def save_alerts_json(alerts):
    if not alerts:
        return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(ALERTS_DIR, f'alerts_{ts}.json')
    with open(path, 'w') as f:
        json.dump(alerts, f, indent=2)
    return path

def save_alerts_csv(alerts):
    if not alerts:
        return None
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    path = os.path.join(ALERTS_DIR, f'alerts_{ts}.csv')
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=alerts[0].keys())
        writer.writeheader()
        writer.writerows(alerts)
    return path 