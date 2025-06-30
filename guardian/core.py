import re
import os
import yaml
from collections import defaultdict, deque
from datetime import datetime, timedelta
from .detectors import load_patterns, load_scores, detect_threats
from typing import List, Dict, Any

class LogAnalyzer:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.ip_scores = defaultdict(int)
        self.alerts = []
        self.whitelist = set(self.config.get('whitelist', []))
        self.alert_threshold = self.config.get('alert_threshold', 70)
        self.log_paths = self.config.get('log_paths', [])
        self.rate_limit = self.config.get('rate_limit', {'count': 20, 'seconds': 60})
        self.ip_times = defaultdict(deque)  # For rate-limiting
        self.log_format = self.config.get('log_format', 'auto')
        self.custom_patterns = self.config.get('custom_patterns', {})
        # Load patterns and scores
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
        patterns_path = os.path.join(assets_dir, 'regex_patterns.json')
        scores_path = os.path.join(assets_dir, 'threat_score_rules.yaml')
        self.patterns = load_patterns(patterns_path, self.custom_patterns)
        self.scores = load_scores(scores_path)

    def parse_log_line(self, line: str):
        # Support auto, nginx/apache, and custom regex from config
        if self.log_format == 'auto' or self.log_format == 'nginx':
            ip_match = re.match(r'^(\d+\.\d+\.\d+\.\d+)', line)
            ip = ip_match.group(1) if ip_match else None
            method_match = re.search(r'"(GET|POST|PUT|DELETE|HEAD)', line)
            method = method_match.group(1) if method_match else None
            path_match = re.search(r' (/[\w\-\./?=&%]*) ', line)
            path = path_match.group(1) if path_match else None
            status_match = re.search(r' (\d{3}) ', line)
            status = status_match.group(1) if status_match else None
        elif self.log_format == 'iis':
            # Example: 2023-01-01 12:00:00 192.168.1.2 GET /index.html 200 ...
            parts = line.split()
            ip = parts[2] if len(parts) > 2 else None
            method = parts[3] if len(parts) > 3 else None
            path = parts[4] if len(parts) > 4 else None
            status = parts[5] if len(parts) > 5 else None
        elif self.log_format == 'custom' and 'log_regex' in self.config:
            m = re.match(self.config['log_regex'], line)
            ip = m.group('ip') if m and 'ip' in m.groupdict() else None
            method = m.group('method') if m and 'method' in m.groupdict() else None
            path = m.group('path') if m and 'path' in m.groupdict() else None
            status = m.group('status') if m and 'status' in m.groupdict() else None
        else:
            ip = method = path = status = None
        return ip, method, path, status

    def analyze(self) -> List[Dict[str, Any]]:
        now = datetime.now
        for log_path in self.log_paths:
            if not os.path.exists(log_path):
                continue
            with open(log_path, 'r', errors='ignore') as f:
                for line in f:
                    ip, method, path, status = self.parse_log_line(line)
                    if not ip or ip in self.whitelist:
                        continue
                    # Rate-limiting detection
                    t = now()
                    times = self.ip_times[ip]
                    times.append(t)
                    while times and (t - times[0]).total_seconds() > self.rate_limit['seconds']:
                        times.popleft()
                    if len(times) > self.rate_limit['count']:
                        alert = {
                            'ip': ip,
                            'type': 'rate_limit',
                            'score': 100,
                            'time': t.strftime('%Y-%m-%d %H:%M'),
                            'log': log_path,
                            'line': line.strip(),
                            'method': method,
                            'path': path,
                            'status': status
                        }
                        self.alerts.append(alert)
                        continue
                    # Pattern-based detection (all matches)
                    matches = detect_threats(line, self.patterns, self.scores)
                    for threat_type, score, pattern in matches:
                        self.ip_scores[ip] += score
                        if self.ip_scores[ip] >= self.alert_threshold:
                            alert = {
                                'ip': ip,
                                'type': threat_type,
                                'score': self.ip_scores[ip],
                                'time': t.strftime('%Y-%m-%d %H:%M'),
                                'log': log_path,
                                'line': line.strip(),
                                'pattern': pattern,
                                'method': method,
                                'path': path,
                                'status': status
                            }
                            self.alerts.append(alert)
        return self.alerts 