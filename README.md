# GIT-DORKER
⚡ Elite GitHub Dorking Engine – API-powered secret scanner for authorized security assessments.

# 🚀 GitDorker-Elite v1.0

A high-performance GitHub reconnaissance tool for professional security assessments. It leverages the **official GitHub REST API v3** to conduct fast, reliable, and stealthy secret discovery.

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

## 🧠 How It Works
- Sends dork queries to `api.github.com/search/code` and reads the `total_count` field.
- Completely **skips** dorks that return zero results – zero terminal noise.
- When hits are found, prints a green banner + a clickable browser URL.
- Includes an intelligent retry engine for seamless rate-limit handling.

---

## ✨ Key Features
- **Zero-Noise Engine**: Only displays dorks that actually return results.
- **Smart Retry Logic**: Automatically pauses for 75s on secondary rate limits (403/429) and resumes from the exact same dork.
- **Abuse Detector**: Instantly halts if your token is invalid or flagged, protecting your credentials.
- **WAF-Proof**: Uses realistic browser User-Agent strings to blend in.
- **Clickable Browser URLs**: Every hit generates a direct GitHub search link for immediate manual inspection.
- **Compatible with any dorks list**: Use your own keyword files (e.g., Jhaddix's list, or the one provided).

---

## 📦 Prerequisites
- Python 3.7+
- A GitHub Personal Access Token (classic, no scopes required).
- A text file containing your dorks (one per line).

---

## ⚙️ Installation

git clone https://github.com/yourusername/GitDorker-Elite.git
cd GitDorker-Elite
pip install requests colorama python-dotenv
```

---

## 🚀 Usage

python gitdorker_elite.py -d target.com -k dorks.txt -t YOUR_GITHUB_TOKEN
```

### Full Options:
| Flag | Description |
|------|-------------|
| `-d`, `--domain` | Target domain (e.g., `monash.edu`) |
| `-k`, `--dorks` | Path to the dorks file (one dork per line) |
| `-t`, `--token` | GitHub Personal Access Token (can also be set in `.env`) |
| `-o`, `--output` | Output filename (default: `<domain>_hits.txt`) |

### Examples:

# Basic scan
python gitdorker_elite.py -d example.com -k dorks.txt -t ghp_xxxx

# Custom output file
python gitdorker_elite.py -d example.com -k dorks.txt -t ghp_xxxx -o results.txt

# Using .env file (create a .env containing GITHUB_TOKEN=ghp_xxxx)
python gitdorker_elite.py -d example.com -k dorks.txt
```

---

## 🛡️ Token Setup
1. Go to [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens/new).
2. Generate a new token with **no scopes**.
3. Copy the token and use it with `-t` or place it in your `.env` file as `GITHUB_TOKEN`.

---

## 📂 Project Structure
```
GitDorker-Elite/
├── gitdorker_elite.py   # Main script
├── dorks.txt            # Your dorks list
├── .env                 # Optional: store GITHUB_TOKEN here
└── README.md            # This file
```

---

## ⚖️ Legal Notice
This tool is intended **exclusively for authorized security assessments** (domains you own or have explicit written permission to test). Unauthorized use may violate local and international computer fraud laws. The author assumes no liability for misuse.

---

## 🤝 Contributing
Pull requests and issues are welcome! Let's make this tool even better.

---

**Made with ❤️ for the Bug Bounty Community**
كده جاهز، والتنسيق مظبوط. لو عايز تعدل حاجة تاني قلي.
