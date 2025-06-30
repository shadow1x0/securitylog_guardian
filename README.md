[![Build](https://github.com/shadow1x0/securitylog_guardian/actions/workflows/ci.yml/badge.svg)](https://github.com/shadow1x0/securitylog_guardian/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

# 🛡️ SecurityLog Guardian

**Lightweight, smart, open-source log analyzer for web servers**

SecurityLog Guardian is a powerful yet simple tool that monitors your web server logs (Apache/Nginx/SSH) to detect suspicious activities like brute-force attacks, XSS attempts, SQL injection, and more. It sends real-time alerts via Telegram, Slack, or Email.

## ✨ Features

- **🔍 Advanced Detection**: Detects XSS, SQL injection, brute-force attacks, and rate-limiting
- **📊 Real-time Monitoring**: Continuously monitors log files for threats
- **🚨 Smart Alerts**: Configurable notifications via Telegram, Slack, or Email
- **📈 Beautiful Dashboard**: Web-based dashboard with filtering, sorting, and export
- **⚙️ Flexible Configuration**: Support for custom patterns and multiple log formats
- **🛡️ Rate Limiting**: Built-in protection against notification spam
- **📁 Multiple Formats**: Support for Nginx, Apache, IIS, and custom log formats

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/shadow1x0/securitylog_guardian.git
cd securitylog-guardian

# Install dependencies
pip install -r requirements.txt

# For dashboard support
pip install -e .[dashboard]
```

### Basic Usage

1. **Copy the config template:**
```bash
cp assets/config_template.yaml my_config.yaml
```

2. **Edit the configuration:**
```yaml
log_paths:
  - /var/log/nginx/access.log
  - /var/log/auth.log

alert_threshold: 70
notification:
  telegram_token: "YOUR_BOT_TOKEN"
  telegram_chat_id: "YOUR_CHAT_ID"
  slack_webhook_url: "YOUR_SLACK_WEBHOOK"
  smtp_server: "smtp.gmail.com"
  smtp_port: 587
  email_username: "your-email@gmail.com"
  email_password: "your-app-password"
  email_to: "admin@yourcompany.com"
```

3. **Run the analyzer:**
```bash
python3 -m guardian.cli --config my_config.yaml
```

## 📊 Dashboard

Start the web dashboard to view alerts in real-time:

```bash
python3 dashboard/app.py
```

Then visit `http://localhost:5000` in your browser.

### Dashboard Features

- **📈 Real-time Statistics**: View total alerts, unique IPs, and recent activity
- **🔍 Advanced Filtering**: Filter by IP, alert type, and date
- **📋 Sorting**: Sort by time, score, IP, or type
- **📄 Pagination**: Handle large numbers of alerts efficiently
- **📤 Export**: Download alerts as CSV
- **🔄 Auto-refresh**: Updates every 30 seconds

## ⚙️ Configuration

### Log Paths
```yaml
log_paths:
  - /var/log/nginx/access.log
  - /var/log/apache2/access.log
  - /var/log/auth.log
```

### Alert Threshold
```yaml
alert_threshold: 70  # Minimum score to trigger alert
```

### Rate Limiting
```yaml
rate_limit:
  count: 20    # Max requests per time window
  seconds: 60  # Time window in seconds
```

### Log Formats
```yaml
log_format: auto  # auto, nginx, iis, custom

# For custom format:
log_format: custom
log_regex: '^(?P<ip>\d+\.\d+\.\d+\.\d+) - - \[(?P<time>[^\]]+)\] "(?P<method>\w+) (?P<path>[^ ]+) HTTP/1.1" (?P<status>\d{3})'
```

### Custom Detection Patterns
```yaml
custom_patterns:
  my_custom_threat:
    - "custompattern1"
    - "custompattern2"
  another_threat:
    - "anotherpattern"
```

## 🔧 Advanced Usage

### CLI Options

```bash
# Basic analysis
python3 -m guardian.cli --config config.yaml

# Save alerts to specific file
python3 -m guardian.cli --config config.yaml --output alerts.json

# Export as CSV
python3 -m guardian.cli --config config.yaml --format csv --output alerts.csv
```

### Environment Variables

You can use environment variables for sensitive configuration:

```bash
export TELEGRAM_TOKEN="your_token"
export TELEGRAM_CHAT_ID="your_chat_id"
export SLACK_WEBHOOK_URL="your_webhook"
```

### Continuous Monitoring

For production use, set up a cron job or systemd service:

```bash
# Add to crontab (runs every 5 minutes)
*/5 * * * * cd /path/to/securitylog-guardian && python3 -m guardian.cli --config config.yaml
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install -e .[dev]

# Run tests
pytest tests/

# Run with coverage
pytest tests/ --cov=guardian
```

## 📁 Project Structure

```
SecurityLogGuardian/
├── guardian/              # Core package
│   ├── __init__.py
│   ├── core.py           # Main analyzer logic
│   ├── detectors.py      # Threat detection patterns
│   ├── notifiers.py      # Alert notifications
│   ├── storage.py        # Alert storage
│   └── cli.py           # Command-line interface
├── dashboard/            # Web dashboard
│   ├── app.py           # Flask application
│   └── templates/
│       └── index.html   # Dashboard template
├── assets/              # Configuration files
│   ├── config_template.yaml
│   ├── regex_patterns.json
│   └── threat_score_rules.yaml
├── data/               # Data storage
│   ├── logs/
│   ├── alerts/
│   └── reports/
├── tests/              # Test suite
├── requirements.txt    # Dependencies
├── setup.py           # Package configuration
└── README.md          # This file
```

## 🔍 Detection Capabilities

### Built-in Threats

- **XSS (Cross-Site Scripting)**: Detects `<script>`, `alert()`, `onerror=` patterns
- **SQL Injection**: Detects `UNION SELECT`, `OR 1=1`, `DROP TABLE`, `--` patterns
- **Brute Force**: Detects repeated login attempts and 401/403 responses
- **Rate Limiting**: Detects excessive requests from single IPs

### Custom Patterns

Add your own detection rules:

```yaml
custom_patterns:
  file_inclusion:
    - "\.\./"
    - "include.*php"
  command_injection:
    - "\\|.*cat"
    - "\\|.*ls"
```

## 🚨 Alert Examples

### Telegram Alert
```
🚨 SecurityLog Guardian Alert

IP: 192.168.1.100
Type: Xss
Score: 80/100
Time: 2025-06-30 13:44
Log: /var/log/nginx/access.log
Method: GET
Path: /index.php
Status: 200
Pattern: <script>

GET /index.php?q=<script>alert(1)</script> HTTP/1.1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by the need for simple, effective log monitoring
- Built with Python, Flask, and modern web technologies
- Thanks to the open-source community for various libraries and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/shadow1x0/securitylog_guardianissues)
- **Discussions**: [GitHub Discussions](https://github.com/shadow1x0/securitylog_guardiandiscussions)
- **Email**: None

---

**Made with ❤️ for the security community** 
