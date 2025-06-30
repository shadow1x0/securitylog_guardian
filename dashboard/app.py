from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import glob
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

def load_alerts() -> List[Dict[str, Any]]:
    """Load all alerts from JSON files in alerts directory."""
    alerts_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'alerts')
    if not os.path.exists(alerts_dir):
        return []
    
    alert_files = sorted(glob.glob(os.path.join(alerts_dir, 'alerts_*.json')), reverse=True)
    alerts = []
    for file in alert_files:
        try:
            with open(file, 'r') as f:
                alerts.extend(json.load(f))
        except Exception as e:
            print(f"Error loading {file}: {e}")
    return alerts

def filter_alerts(alerts: List[Dict], ip_filter: Optional[str] = None, 
                  type_filter: Optional[str] = None, date_filter: Optional[str] = None) -> List[Dict]:
    """Filter alerts by various criteria."""
    filtered = alerts
    
    if ip_filter:
        filtered = [a for a in filtered if a.get('ip') == ip_filter]
    
    if type_filter:
        filtered = [a for a in filtered if a.get('type') == type_filter]
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            filtered = [a for a in filtered if datetime.strptime(a.get('time', ''), '%Y-%m-%d %H:%M').date() == filter_date]
        except:
            pass
    
    return filtered

def sort_alerts(alerts: List[Dict], sort_by: str = 'time', sort_order: str = 'desc') -> List[Dict]:
    """Sort alerts by specified field."""
    reverse = sort_order == 'desc'
    
    if sort_by == 'time':
        alerts.sort(key=lambda x: x.get('time', ''), reverse=reverse)
    elif sort_by == 'score':
        alerts.sort(key=lambda x: x.get('score', 0), reverse=reverse)
    elif sort_by == 'ip':
        alerts.sort(key=lambda x: x.get('ip', ''), reverse=reverse)
    elif sort_by == 'type':
        alerts.sort(key=lambda x: x.get('type', ''), reverse=reverse)
    
    return alerts

def paginate_alerts(alerts: List[Dict], page: int = 1, per_page: int = 50) -> Dict[str, Any]:
    """Paginate alerts for display."""
    total = len(alerts)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_alerts = alerts[start:end]
    
    return {
        'alerts': paginated_alerts,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': end < total
    }

app = Flask(__name__)

@app.route('/')
def index():
    """Main dashboard page with filtering, sorting, and pagination."""
    # Get query parameters
    ip_filter = request.args.get('ip', '')
    type_filter = request.args.get('type', '')
    date_filter = request.args.get('date', '')
    sort_by = request.args.get('sort', 'time')
    sort_order = request.args.get('order', 'desc')
    page = int(request.args.get('page', 1))
    
    # Load and process alerts
    alerts = load_alerts()
    alerts = filter_alerts(alerts, ip_filter, type_filter, date_filter)
    alerts = sort_alerts(alerts, sort_by, sort_order)
    pagination = paginate_alerts(alerts, page)
    
    # Get unique values for filter dropdowns
    unique_ips = sorted(list(set(a.get('ip', '') for a in alerts if a.get('ip'))))
    unique_types = sorted(list(set(a.get('type', '') for a in alerts if a.get('type'))))
    
    return render_template('index.html', 
                         pagination=pagination,
                         ip_filter=ip_filter,
                         type_filter=type_filter,
                         date_filter=date_filter,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         unique_ips=unique_ips,
                         unique_types=unique_types)

@app.route('/export')
def export():
    """Export filtered alerts as CSV."""
    ip_filter = request.args.get('ip', '')
    type_filter = request.args.get('type', '')
    date_filter = request.args.get('date', '')
    
    alerts = load_alerts()
    alerts = filter_alerts(alerts, ip_filter, type_filter, date_filter)
    
    if not alerts:
        return "No alerts to export", 404
    
    # Create temporary CSV file
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'alerts', f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=alerts[0].keys())
        writer.writeheader()
        writer.writerows(alerts)
    
    return send_file(csv_path, as_attachment=True, download_name='security_alerts.csv')

@app.route('/api/alerts')
def api_alerts():
    """API endpoint for alerts (JSON)."""
    alerts = load_alerts()
    return jsonify(alerts)

@app.route('/api/stats')
def api_stats():
    """API endpoint for alert statistics."""
    alerts = load_alerts()
    
    # Calculate stats
    total_alerts = len(alerts)
    unique_ips = len(set(a.get('ip', '') for a in alerts))
    alert_types = {}
    for alert in alerts:
        alert_type = alert.get('type', 'unknown')
        alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
    
    # Recent alerts (last 24 hours)
    yesterday = datetime.now() - timedelta(days=1)
    recent_alerts = [a for a in alerts if datetime.strptime(a.get('time', ''), '%Y-%m-%d %H:%M') > yesterday]
    
    return jsonify({
        'total_alerts': total_alerts,
        'unique_ips': unique_ips,
        'alert_types': alert_types,
        'recent_alerts': len(recent_alerts)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 