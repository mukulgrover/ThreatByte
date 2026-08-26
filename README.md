# 🛡️ ThreatByte — Automated Cyber Threat Intelligence & Incident Platform

[![Live Portal](https://img.shields.io/badge/Live%20Portal-ThreatByte-3b82f6?style=for-the-badge&logo=googlechrome&logoColor=white)](https://mukulgrover.github.io/ThreatByte)
[![Daily Briefing](https://img.shields.io/badge/Daily%20Briefing-06%3A00%20UTC-3b82f6?style=for-the-badge&logo=githubactions&logoColor=white)](.github/workflows/daily_briefing.yml)
[![AI Threat Engine](https://img.shields.io/badge/AI%20Engine-NVIDIA%20NIM%20(Llama%203.1)-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-%40threatbytebot-229ED9?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/threatbytebot)
[![LinkedIn Post](https://img.shields.io/badge/LinkedIn-Announcement%20Post-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://lnkd.in/p/dQvbGb7g)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge)](LICENSE)

> **ThreatByte** is an automated, analyst-grade Cyber Threat Intelligence (CTI) platform. It continuously aggregates breaking 24-hour telemetry on zero-days, ransomware intrusions, data breaches, and active software exploits across premier security feeds, synthesizes deep technical dossiers via **NVIDIA NIM AI reasoning**, broadcasts morning intelligence bulletins to **Telegram**, and publishes an interactive **Cyber Threat Intelligence Web Portal**.

---

## 🌐 Live Access & Community

- **Web Portal**: [https://mukulgrover.github.io/ThreatByte](https://mukulgrover.github.io/ThreatByte)
- **Telegram Bot**: [@threatbytebot](https://t.me/threatbytebot) *(Type `/start` or `/today` for instant bulletins)*
- **Author Profile**: [Mukul Kumar on LinkedIn](https://www.linkedin.com/in/mukul-kumar-169215245/)
- **LinkedIn Announcement**: [Read the Launch Post](https://lnkd.in/p/dQvbGb7g)

---

## ⚡ System Architecture

```
   ┌─────────────────────────────────────────────────────────────┐
   │             Automated Trigger (100% Free)                   │
   │        GitHub Actions Cron (Every day at 08:00 AM IST)      │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │            Ingestion & 24h Deduplication Engine             │
   │  BleepingComputer • The Hacker News • Krebs • Dark Reading  │
   │           SecurityWeek • SANS Internet Storm Center         │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                                  ▼
   ┌─────────────────────────────────────────────────────────────┐
   │           AI Threat Reasoning Engine (NVIDIA NIM)           │
   │  - Severity Scoring (CVSS 1.0–10.0 / Critical / High / Med) │
   │  - CVE Identifier Extraction & Threat Actor Profiling       │
   │  - Technical Root Cause & Attack Vector Analysis            │
   │  - Actionable Defense & Mitigation Checklists               │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
   ┌───────────────────────────┐     ┌───────────────────────────┐
   │    Telegram Bot Channel   │     │    ThreatByte Web Portal  │
   │  - @threatbytebot auto-   │     │  - Editorial Dark UI      │
   │    subscriber broadcast   │     │  - Live CVE & Tag Search  │
   │  - Morning 08:00 AM IST   │     │  - Historical Archives    │
   │  - /today on-demand cmd   │     │  - Defense Checklists     │
   └───────────────────────────┘     └───────────────────────────┘
```

---

## ✨ Core Capabilities

- 🧠 **Analyst-Grade AI Synthesis**: Employs **NVIDIA NIM** (`meta/llama-3.1-8b-instruct` / `70b`) to extract root causes, affected software versions, CVEs, and actionable defense checklists.
- 🤖 **Automated Telegram Subscriber Delivery**:
  - Anyone can open [t.me/threatbytebot](https://t.me/threatbytebot) and press **Start** to subscribe.
  - Automatically receives morning bulletins every day at `08:00 AM IST` (`02:30 UTC`).
  - Supports on-demand intelligence commands: `/today`, `/subscribe`, `/help`.
- 📰 **Editorial Web Portal**: Designed with an authentic, human-curated publication layout featuring lead story focus, verified source tags, interactive mitigation accordions, live CVE search, and historical date archives.
- 💸 **Zero-Maintenance & 100% Free-Tier Architecture**:
  - **Scheduler**: GitHub Actions (Scheduled Cron)
  - **Inference**: NVIDIA NIM Free API Tier
  - **Distribution**: Telegram Bot API
  - **Hosting**: GitHub Pages

---

## 🛠️ Tech Stack & Infrastructure

| Component | Technology | Description |
|---|---|---|
| **Collector & Scraper** | Python 3.12, BeautifulSoup4, Feedparser | Multi-source CTI feed aggregation with 24h window deduplication |
| **Reasoning Engine** | NVIDIA NIM API (`meta/llama-3.1-8b-instruct`) | Structured threat extraction, severity classification & mitigation generation |
| **Broadcasting** | Telegram Bot API (`@threatbytebot`) | Subscriber registration and automated morning HTML bulletin delivery |
| **Web Frontend** | Vanilla HTML5, CSS3, JavaScript (ES6+) | Dark editorial portal, live search, CVSS meters, and date archives |
| **Automation** | GitHub Actions Workflow | Daily automated cron at 08:00 AM IST (02:30 UTC) with auto-commit & deploy |

---

## 📂 Repository Structure

```
ThreatByte/
├── .github/
│   └── workflows/
│       └── daily_briefing.yml        # Scheduled GitHub Actions cron runner
├── backend/
│   ├── config.py                     # CTI feed configs, prompts, and settings
│   ├── scraper.py                    # RSS & feed scrapers with deduplication
│   ├── ai_enricher.py                # NVIDIA NIM AI reasoning & threat analysis
│   ├── telegram_bot.py               # Telegram subscriber manager & broadcaster
│   ├── bot_service.py                # Background Telegram bot interactive listener
│   ├── generator.py                  # Master orchestration pipeline
│   └── requirements.txt              # Python dependencies
├── data/
│   ├── latest.json                   # Latest day's structured threat intelligence
│   ├── archive.json                  # Historical archive index
│   ├── subscribers.json              # Registered Telegram bot subscriber chat IDs
│   └── daily/                        # Historical daily intelligence payloads
├── frontend/
│   ├── index.html                    # Editorial Web Portal SPA
│   ├── css/
│   │   └── style.css                 # Dark editorial theme & responsive grid
│   └── js/
│       └── app.js                    # Dynamic feed rendering, search & filters
├── index.html                        # Root redirect for GitHub Pages deployment
├── .env.example                      # Environment variables template
├── LICENSE                           # MIT License
└── README.md                         # Project documentation
```

---

## 💻 Local Development

### 1. Clone & Setup
```bash
git clone https://github.com/mukulgrover/ThreatByte.git
cd ThreatByte

# Install dependencies
pip install -r backend/requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` and fill in your keys:
```env
NVIDIA_API_KEY=your_nvidia_nim_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_BOT_USERNAME=threatbytebot
SITE_URL=https://mukulgrover.github.io/ThreatByte
```

### 3. Run Pipeline
```bash
# Execute aggregation, AI reasoning, and data generation
python backend/generator.py

# Launch web portal locally
python -m http.server 8080
# Open http://localhost:8080/frontend/index.html in your browser
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE) — free and open for the global cybersecurity community.
