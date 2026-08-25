# 🛡️ ThreatByte — Daily Cyber Threat Intelligence & Incident Analysis

[![GitHub Actions Cron](https://img.shields.io/badge/Daily%20Briefing-06%3A00%20UTC-3b82f6?style=for-the-badge&logo=githubactions&logoColor=white)](.github/workflows/daily_briefing.yml)
[![AI Threat Reasoning](https://img.shields.io/badge/AI%20Reasoning-NVIDIA%20NIM%20(Llama%203.1)-76B900?style=for-the-badge&logo=nvidia&logoColor=white)](https://build.nvidia.com)
[![Telegram Bot](https://img.shields.io/badge/Telegram%20Bot-%40threatbytebot-229ED9?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/threatbytebot)
[![Zero Cost](https://img.shields.io/badge/Cost-%240%20%2F%20100%25%20Free%20Tier-10b981?style=for-the-badge)](https://github.com)

> **ThreatByte** is an automated, analyst-grade Cyber Threat Intelligence (CTI) platform that gathers breaking 24-hour cybersecurity news, data leaks, and zero-day disclosures, synthesizes them using **NVIDIA NIM LLM reasoning** (with CVSS severity, CVE tags, root causes, and actionable defense checklists), broadcasts daily morning bulletins to a **Telegram Bot** (`@threatbytebot`), and delivers an interactive **Cyber Threat Portal**.

---

## ⚡ Architecture Flow

```
   ┌─────────────────────────────────────────────────────────────┐
   │             Automated Trigger (100% Free)                   │
   │        GitHub Actions Cron (Every day at 06:00 UTC)         │
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
   │  - Severity Classification (Critical / High / Med / Low)    │
   │  - CVE Extraction & Threat Actor Profiling                  │
   │  - Root Cause & Technical Attack Vector Breakdown           │
   │  - Actionable Defense & Mitigation Checklists               │
   └──────────────────────────────┬──────────────────────────────┘
                                  │
                 ┌────────────────┴────────────────┐
                 ▼                                 ▼
   ┌───────────────────────────┐     ┌───────────────────────────┐
   │    Telegram Bot Channel   │     │    ThreatByte Web Portal  │
   │  - @threatbytebot auto-   │     │  - Editorial Dark UI      │
   │    subscribers & welcome  │     │  - Search & CVE filter    │
   │  - Morning 06:00 UTC brief│     │  - Historical Archives    │
   │  - /today on-demand cmd   │     │  - Mitigation checkbooks  │
   └───────────────────────────┘     └───────────────────────────┘
```

---

## ✨ Key Features

- 🧠 **Analyst-Grade AI Synthesis**: Employs **NVIDIA NIM** (`meta/llama-3.1-70b-instruct`) for human-like threat reasoning, CVE identification, and concrete mitigation steps.
- 🤖 **Interactive Telegram Bot (`@threatbytebot`)**:
  - Anyone can open [t.me/threatbytebot](https://t.me/threatbytebot) and press **Start** to subscribe.
  - Automatically receives morning bulletins every day at `06:00 UTC`.
  - On-demand commands: `/today`, `/subscribe`, `/help`.
- 📰 **Editorial Web Portal**: Clean, human-first editorial design with lead story focus, verified source tags, interactive mitigation accordions, live CVE search, and historical date archives.
- 💸 **100% Free-Tier Architecture**:
  - Compute / Cron: GitHub Actions (Free 2,000 mins/mo)
  - AI Inference: NVIDIA NIM Free Tier
  - Telegram API: Free Bot API
  - Web Hosting: GitHub Pages / Vercel ($0)

---

## 🚀 Quickstart

### 1. Run Pipeline
```bash
# Clone & install dependencies
pip install -r backend/requirements.txt

# Run the pipeline (fetches news, reasons via NVIDIA NIM, updates web data & notifies Telegram)
python backend/generator.py
```

### 2. View Web Dashboard
```bash
python -m http.server 8080
# Open http://localhost:8080/frontend/index.html in your browser
```

### 3. Run Optional 24/7 Telegram Bot Listener
```bash
python backend/bot_service.py
```

---

## 💼 LinkedIn Announcement Post Template

```markdown
🚀 Excited to launch ThreatByte — an open-access, AI-powered Cyber Threat Intelligence platform built on 100% free-tier architecture!

🔍 Security teams and CISOs face a relentless flood of alerts, breaches, and zero-day disclosures every single day. ThreatByte cuts through the noise:
1️⃣ Scrapes & deduplicates breaking 24h threat telemetry across BleepingComputer, The Hacker News, Dark Reading, and KrebsOnSecurity.
2️⃣ Reasons through technical impact via NVIDIA NIM (Llama 3.1 70B) to extract CVSS severities, affected products, root causes, and actionable defense checklists.
3️⃣ Dispatches curated morning briefings directly to our Telegram Bot (@threatbytebot).
4️⃣ Updates an interactive threat portal with historical date archives.

🔗 Live Web Portal: https://mukulgrover.github.io/ThreatByte
📲 Join the Daily Telegram Bot: https://t.me/threatbytebot
💻 Open Source Repository: https://github.com/mukulgrover/ThreatByte

#CyberSecurity #ThreatIntelligence #Infosec #DevSecOps #NVIDIA #AI #Python #OpenSource
```

---

## 📜 License
MIT License. Open-source and free for all security practitioners.
