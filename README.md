# GIT-DORKER
⚡ Elite GitHub Dorking Engine – API-powered secret scanner for authorized security assessments.

![GitHub stars](https://img.shields.io/github/stars/alkaserGG/GIT-DORKER?style=social) ![GitHub license](https://img.shields.io/github/license/alkaserGG/GIT-DORKER) ![Python version](https://img.shields.io/badge/python-3.7+-blue)[![Facebook](https://img.shields.io/badge/Facebook-Abdo%20Alkaser-1877F2?style=flat&logo=facebook)](https://www.facebook.com/abdo.alkaser.5)

```
██████╗ ██╗████████╗██████╗  ██████╗ ██████╗ ██╗  ██╗███████╗██████╗
██╔════╝ ██║╚══██╔══╝██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
██║  ███╗██║   ██║   ██║  ██║██║   ██║██████╔╝█████╔╝ █████╗  ██████╔╝
██║   ██║██║   ██║   ██║  ██║██║   ██║██╔══██╗██╔═██╗ ██╔══╝  ██╔══██╗
╚██████╔╝██║   ██║   ██████╔╝╚██████╔╝██║  ██║██║  ██╗███████╗██║  ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

              ─────────  E L I T E   E D I T I O N  ─────────
        GitHub Secret Reconnaissance via Official REST API v3
   ⚠  Authorized security assessments only — use responsibly.
```

---

## 📋 Table of Contents

- [✨ Features](#-features)
- [🧠 How It Works](#-how-it-works)
- [📦 Prerequisites](#-prerequisites)
- [⚙️ Installation](#️-installation)
  - [Linux (Kali / Ubuntu / Parrot)](#linux-kali--ubuntu--parrot)
  - [Windows 10 / 11](#windows-10--11)
  - [macOS](#macos)
- [🚀 Usage](#-usage)
- [📖 CLI Reference](#-cli-reference)
- [📂 Dorks File Format](#-dorks-file-format)
- [📊 Output](#-output)
- [🔔 Optional: Discord Notifications](#-optional-discord-notifications)
- [⚖️ Legal Notice](#️-legal-notice)
- [📄 License](#-license)
- [🤝 Contributing](#-contributing)

---

## ✨ Features

| Feature | Detail |
|---|---|
| 🔍 REST API v3 | Uses official GitHub Code Search endpoint, no HTML scraping |
| 🤫 Zero Noise | Skips dorks with zero results — only prints hits |
| 🧠 Smart Retry | 75s cooldown on secondary rate limits, resumes exact query |
| 🛡️ Abuse Detector | Stops immediately if token is invalid or banned |
| 🕵️ WAF-Proof | Realistic browser User-Agent, avoids blocking |
| 🔗 Clickable Output | Each hit generates a direct GitHub search URL for inspection |
| 🗃️ Any Dorks List | Compatible with Jhaddix, custom, or built-in keyword files |
| ⚡ Performance | Enforces 2.8s delay, stays under 30 req/min authenticated cap |
| 📝 Token Safety | Supports `.env` file — never hardcode your secret |

---

## 🧠 How It Works

1. Loads a plain-text list of dorks (one per line).
2. For each dork, sends a search query to `api.github.com/search/code` with your target domain.
3. Reads only the `total_count` field from the JSON response.
4. If `total_count > 0`, prints a green hit line with a clickable browser URL and appends it to the output file.
5. If a rate limit occurs (403/429), pauses 75 seconds and retries — no dorks are skipped.
6. At the end, prints a summary of total dorks tested and hits found.

---

## 📦 Prerequisites

- Python 3.7 or higher
- A GitHub Personal Access Token (classic, **no scopes required**)
- A dorks file (see [Dorks File Format](#-dorks-file-format))

---

## ⚙️ Installation

### Linux (Kali / Ubuntu / Parrot)

```bash
# Install system dependencies
sudo apt update && sudo apt install -y python3 python3-pip git

# Clone the repository
git clone https://github.com/yourusername/GIT-DORKER.git
cd GIT-DORKER

# Install Python requirements
pip3 install -r requirements.txt
```

### Windows 10 / 11

```powershell
# Install Python 3 from python.org (tick "Add Python to PATH")
# Open PowerShell or Command Prompt

git clone https://github.com/yourusername/GIT-DORKER.git
cd GIT-DORKER
pip install -r requirements.txt
```

### macOS

```bash
# Using Homebrew
brew install python3 git

git clone https://github.com/yourusername/GIT-DORKER.git
cd GIT-DORKER
pip3 install -r requirements.txt
```

---

## 🚀 Usage

### Minimal run

```bash
python gitdorker_elite.py -d target.com -k dorks.txt -t YOUR_GITHUB_TOKEN
```

### With custom output file

```bash
python gitdorker_elite.py -d target.com -k dorks.txt -t YOUR_GITHUB_TOKEN -o my_results.txt
```

### Using `.env` (recommended)

Create a `.env` file in the project directory:

```
GITHUB_TOKEN=ghp_XXXXXXXXXXXXXXXXXXXX
```

Then run without `-t`:

```bash
python gitdorker_elite.py -d target.com -k dorks.txt
```

---

## 📖 CLI Reference

```
usage: gitdorker_elite [-h] -d DOMAIN -k FILE [-t TOKEN] [-o OUTPUT]

options:
  -h, --help                    Show help and exit

required:
  -d DOMAIN, --domain DOMAIN    Target domain (e.g., monash.edu)
  -k FILE,  --dorks  FILE       Path to dorks file (one dork per line)

optional:
  -t TOKEN, --token  TOKEN      GitHub Personal Access Token (overrides .env)
  -o OUTPUT,--output OUTPUT     Output filename (default: <domain>_hits.txt)
```

---

## 📂 Dorks File Format

A simple text file with **one keyword or pattern per line**.  
Comments are supported — lines starting with `#` are ignored.

Example (`dorks.txt`):

```text
# API keys
api_key
client_secret
-----BEGIN RSA PRIVATE KEY-----

# File patterns
filename:.env
filename:.npmrc _auth

# AWS
AWS_ACCESS_KEY_ID=
AKIA[0-9A-Z]{16}
```

You can use any existing dorks list (Jhaddix, custom, etc.).

---

## 📊 Output

The tool writes hits to a text file (default: `<domain>_hits.txt`).  
Each line contains the hit count and a clickable browser URL:

```
[HIT - 3 results] -> https://github.com/search?q=target.com+api_key&type=code
[HIT - 1 result] -> https://github.com/search?q=target.com+filename:.env&type=code
```

Open the URL to browse the actual code matches on GitHub.

---

## 🔔 Optional: Discord Notifications

You can easily extend the tool to send Discord alerts when hits are found.  
A simple webhook integration example will be added in `v1.1`.  
Meanwhile, you can pipe the output to a notification script:

```bash
python gitdorker_elite.py -d target.com -k dorks.txt -t $GH_TOKEN | grep HIT >> discord_alert.txt
```

---

## ⚖️ Legal Notice

> **GitDorker-Elite is intended exclusively for authorized security assessments.**  
> Always obtain explicit written permission from the target organization before scanning.  
> Unauthorized use may violate the Computer Fraud and Abuse Act (CFAA) and similar laws worldwide.  
> The author assumes no liability for misuse.

---

## 📄 License

MIT © 2025 — Your Name  
See [LICENSE](LICENSE) for full terms.

---

## 🤝 Contributing

Pull requests and issues are welcome!  
Please open an issue first for major changes.

```bash
git clone https://github.com/yourusername/GIT-DORKER.git
cd GIT-DORKER
git checkout -b feature/my-improvement
```

---

_Made with ❤️ for the Bug Bounty Community._
