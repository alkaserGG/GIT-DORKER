#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         GitDorker-Elite v1.0                               ║
║         GitHub Secret Reconnaissance via Official REST API v3              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  ⚠  LEGAL NOTICE: This tool is intended exclusively for authorised         ║
║     security assessments — i.e. domains/organisations you own or have      ║
║     explicit written permission to test. Misuse may violate computer-      ║
║     fraud laws. The author assumes no liability for unauthorised use.      ║
╚══════════════════════════════════════════════════════════════════════════════╝

Architecture
─────────────
Uses the GitHub Code Search REST API v3 (api.github.com/search/code) instead
of HTML scraping, which avoids login walls and produces reliable JSON output.

For every dork the tool:
  1. POSTs a query "domain + dork" to the API.
  2. Reads only the `total_count` integer from the response.
  3. Silently skips zero-result dorks (zero terminal noise).
  4. On any hit, prints a green banner + saves a clickable browser URL.

Rate limiting
─────────────
GitHub Search API cap: 30 requests/minute when authenticated.
Hard floor of REQUEST_DELAY_S=2.2 s between every call keeps us ≤ 27 req/min.
On 403 / 429 the tool pauses 60 s and retries the EXACT same dork automatically.
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests
from colorama import Fore, Style, init
from dotenv import load_dotenv

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════

GITHUB_API_URL     : str   = "https://api.github.com/search/code"
GITHUB_BROWSER_URL : str   = "https://github.com/search"

# 2.2 s floor → stays comfortably under the 30 req/min authenticated cap
REQUEST_DELAY_S    : float = 2.8

# How long to cool down when a secondary rate-limit (403 / 429) is hit
RATE_LIMIT_SLEEP_S : int   = 60

# Per-request HTTP timeout to prevent indefinite hangs
HTTP_TIMEOUT_S     : int   = 20


# ══════════════════════════════════════════════════════════════════════════════
#  TERMINAL COLOURS  (colorama)
# ══════════════════════════════════════════════════════════════════════════════

# autoreset=True means we never need to manually write Style.RESET_ALL after
# every single coloured string — colorama resets the escape code automatically.
init(autoreset=True)


# ══════════════════════════════════════════════════════════════════════════════
#  BANNER
# ══════════════════════════════════════════════════════════════════════════════

def print_banner() -> None:
    """Print the ASCII-art tool header to stdout."""
    cyan_b = Fore.CYAN + Style.BRIGHT
    reset  = Style.RESET_ALL

    print(f"""
{cyan_b}
  ██████╗ ██╗████████╗██████╗  ██████╗ ██████╗ ██╗  ██╗███████╗██████╗
 ██╔════╝ ██║╚══██╔══╝██╔══██╗██╔═══██╗██╔══██╗██║ ██╔╝██╔════╝██╔══██╗
 ██║  ███╗██║   ██║   ██║  ██║██║   ██║██████╔╝█████╔╝ █████╗  ██████╔╝
 ██║   ██║██║   ██║   ██║  ██║██║   ██║██╔══██╗██╔═██╗ ██╔══╝  ██╔══██╗
 ╚██████╔╝██║   ██║   ██████╔╝╚██████╔╝██║  ██║██║  ██╗███████╗██║  ██║
  ╚═════╝ ╚═╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

{reset}{Fore.CYAN}              ─────────  E L I T E   E D I T I O N  ─────────
{reset}{Fore.WHITE}        GitHub Secret Reconnaissance via Official REST API v3
{reset}{Fore.RED}{Style.BRIGHT}   ⚠  Authorized security assessments only — use responsibly.
{reset}""")


# ══════════════════════════════════════════════════════════════════════════════
#  CLI ARGUMENT PARSING
# ══════════════════════════════════════════════════════════════════════════════

def parse_args() -> argparse.Namespace:
    """
    Define and return all command-line arguments.

    Required
    ────────
    -d / --domain : Target domain string (e.g. "target.com")
    -k / --dorks  : Path to the newline-delimited dorks file

    Optional
    ────────
    -t / --token  : GitHub Personal Access Token (overrides .env)
    -o / --output : Custom output file path
    """
    parser = argparse.ArgumentParser(
        prog="gitdorker_elite",
        description=(
            "GitDorker-Elite — automated GitHub dork scanner "
            "using the official REST API v3."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python gitdorker_elite.py -d example.com -k dorks.txt\n"
            "  python gitdorker_elite.py -d example.com -k dorks.txt -t ghp_ABC123\n"
            "  python gitdorker_elite.py -d example.com -k dorks.txt -o results.txt\n"
        ),
    )

    parser.add_argument(
        "-d", "--domain",
        required=True,
        metavar="DOMAIN",
        help="Target domain to search for (e.g. target.com)",
    )
    parser.add_argument(
        "-k", "--dorks",
        required=True,
        metavar="FILE",
        help="Path to the newline-delimited dorks list (.txt)",
    )
    parser.add_argument(
        "-t", "--token",
        required=False,
        default=None,
        metavar="TOKEN",
        help=(
            "GitHub Personal Access Token. "
            "Overrides GITHUB_TOKEN in .env file when supplied."
        ),
    )
    parser.add_argument(
        "-o", "--output",
        required=False,
        default=None,
        metavar="FILE",
        help="Output filename for hits (default: <domain>_hits.txt)",
    )

    return parser.parse_args()


# ══════════════════════════════════════════════════════════════════════════════
#  TOKEN RESOLUTION
# ══════════════════════════════════════════════════════════════════════════════

def resolve_token(cli_token: Optional[str]) -> str:
    """
    Determine the GitHub PAT to use, checking sources in priority order:

        1. --token CLI argument    ← highest priority
        2. GITHUB_TOKEN in .env    ← fallback

    Exits with a descriptive error message when no token can be found anywhere.
    A valid PAT is mandatory; the unauthenticated API cap is only 10 req/min
    and frequently returns 403 for code-search endpoints.
    """
    if cli_token:
        return cli_token

    # python-dotenv loads key=value pairs from a .env file into os.environ.
    # Calling load_dotenv() is safe even if no .env file exists — it's a no-op.
    load_dotenv()
    env_token = os.getenv("GITHUB_TOKEN")

    if not env_token:
        print(Fore.RED + "\n[✗] GitHub token not found.")
        print(
            Fore.YELLOW
            + "    Supply one via --token <PAT>  OR  set "
              "GITHUB_TOKEN=<PAT> in a .env file."
        )
        sys.exit(1)

    return env_token


# ══════════════════════════════════════════════════════════════════════════════
#  DORK FILE LOADER
# ══════════════════════════════════════════════════════════════════════════════

def load_dorks(filepath: str) -> list:
    """
    Read and validate a plain-text dorks file.

    File format rules
    ─────────────────
    • One dork per line.
    • Lines whose first non-whitespace character is '#' are comments → skipped.
    • Blank / whitespace-only lines are skipped.
    • No maximum line length is enforced, but GitHub limits query length to
      256 characters; excessively long dorks may return a 422 from the API.

    Returns a list[str] of cleaned dork strings.
    Exits with an error if the file is missing or produces zero valid dorks.
    """
    path = Path(filepath)

    if not path.exists():
        print(Fore.RED + f"\n[✗] Dorks file not found: {filepath}")
        sys.exit(1)

    raw_lines = path.read_text(encoding="utf-8").splitlines()

    dorks = [
        line.strip()
        for line in raw_lines
        if line.strip() and not line.strip().startswith("#")
    ]

    if not dorks:
        print(Fore.RED + "\n[✗] Dorks file is empty (or contains only comments).")
        sys.exit(1)

    return dorks


# ══════════════════════════════════════════════════════════════════════════════
#  REQUEST HEADERS
# ══════════════════════════════════════════════════════════════════════════════

def build_headers(token: str) -> dict:
    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ),
    }

# ══════════════════════════════════════════════════════════════════════════════
#  BROWSER URL BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def make_browser_url(domain: str, dork: str) -> str:
    """
    Produce a human-clickable GitHub code-search URL so a researcher can
    immediately inspect the hits in a browser without retyping anything.

    quote_plus() percent-encodes special characters and converts spaces to '+'
    which is the correct encoding for URL query-string parameters.

    Example output:
        https://github.com/search?q=target.com+filename%3A.env&type=code
    """
    encoded_domain = quote_plus(domain)
    encoded_dork   = quote_plus(dork)
    return f"{GITHUB_BROWSER_URL}?q={encoded_domain}+{encoded_dork}&type=code"


# ══════════════════════════════════════════════════════════════════════════════
#  GITHUB CODE SEARCH API  (with rate-limit auto-retry)
# ══════════════════════════════════════════════════════════════════════════════

def query_github(query: str, headers: dict) -> Optional[dict]:
    """
    Execute one GitHub Code Search API request and return the parsed JSON body.

    Parameters
    ──────────
    query   : The full search string, e.g. "target.com filename:.env"
    headers : Pre-built auth + Accept headers

    Return value
    ────────────
    dict  → Parsed JSON on HTTP 200 (contains at minimum a `total_count` key)
    None  → Non-retriable error; caller should skip this dork

    Rate-limit handling  (the crucial part)
    ──────────────────────────────────────
    403 / 429  → GitHub secondary rate-limit or abuse trigger.
                 Print yellow warning, sleep RATE_LIMIT_SLEEP_S seconds,
                 then retry the EXACT same request (infinite retry loop).

    422        → Unprocessable query (syntax error or too short).
                 Log the error and return None — no retry, nothing to gain.

    Other ≠200 → Unexpected API error. Log and return None.

    Network ex → Connection / timeout error. Log and return None.

    Performance note: per_page=1 is intentional.
    We only need `total_count` — not the items themselves — so requesting
    one item per page minimises response payload and latency.
    """
    smart_query = (
    f"{query} -filename:package-lock.json "
    f"-filename:yarn.lock -filename:pnpm-lock.yaml"
)
    params = {"q": smart_query, "per_page": 1}

    while True:   # ← Retry loop; only exits on success or non-retriable error
        try:
            response = requests.get(
                GITHUB_API_URL,
                headers=headers,
                params=params,
                timeout=HTTP_TIMEOUT_S,
            )
        except requests.RequestException as exc:
            # Network-level failure (DNS, timeout, SSL, etc.)
            print(Fore.RED + f"\n[✗] Network error: {exc}")
            return None

        # ── Rate limit hit (secondary limit or abuse detection) ───────────
        if response.status_code in (403, 429):
            err_body = response.json()
            err_msg  = err_body.get("message", "").lower()

            # تفكيك الـ 403: هل هي مشكلة حظر توكن وليست زحمة؟
            if any(w in err_msg for w in ["bad credentials", "maximum number", "auth", "abuse"]):
                print(Fore.RED + f"\n[✗] Fatal API Block (403): {err_body.get('message')}")
                print(Fore.RED + "    Your Token is invalid or blocked by GitHub Anti-Abuse. Aborting.")
                sys.exit(1)

            # التعديل الجديد: نوم عميق 75 ثانية لضمان تصفير العداد تماماً من جيت هب
            print(Fore.YELLOW + f"\n[!] Rate limit hit ({response.status_code}). Cooling down for 75s...")
            time.sleep(75)
            continue   # دي السحر اللي بيرجع يبعت نفس الريكويست تاني

        # ── Malformed / unsupported query ─────────────────────────────────
        if response.status_code == 422:
            error_msg = response.json().get("message", "unknown reason")
            print(Fore.RED + f"\n[✗] Invalid query syntax (422): {query!r}")
            print(Fore.RED + f"    API says: {error_msg}")
            return None

        # ── Any other unexpected HTTP error ───────────────────────────────
        if response.status_code != 200:
            print(
                Fore.RED
                + f"\n[✗] Unexpected API response HTTP {response.status_code} "
                  f"for query: {query!r}"
            )
            return None

        # ── Success ───────────────────────────────────────────────────────
        return response.json()


# ══════════════════════════════════════════════════════════════════════════════
#  IN-PLACE PROGRESS INDICATOR
# ══════════════════════════════════════════════════════════════════════════════

def render_progress(current: int, total: int, dork: str) -> None:
    """
    Write a single-line status indicator that overwrites itself on each call.

    How it works
    ────────────
    '\r' (carriage return without newline) resets the cursor to the very start
    of the current terminal line without advancing to the next one.  The next
    call to this function then overwrites that line in-place.

    A fixed-width dork display (padded / truncated to MAX_DORK_WIDTH chars)
    guarantees that longer text from a previous call doesn't "bleed" through
    when a shorter dork replaces it on screen.

    sys.stdout.flush() forces the write to appear immediately rather than
    waiting for the output buffer to fill up.

    This function should only be called for misses.  When a hit is found,
    main() writes '\n' first so the hit message appears on its own fresh line.
    """
    MAX_DORK_WIDTH = 55

    # Truncate and pad so the line width stays constant
    dork_display = (
        dork if len(dork) <= MAX_DORK_WIDTH
        else dork[: MAX_DORK_WIDTH - 3] + "..."
    )

    counter_label = f"[{current}/{total} dorks tested]"

    line = (
        f"\r{Fore.CYAN}{Style.BRIGHT}{counter_label:<24}{Style.RESET_ALL}"
        f"{Fore.WHITE}Testing: "
        f"{Fore.BLUE}{dork_display:<{MAX_DORK_WIDTH}}{Style.RESET_ALL}"
    )

    sys.stdout.write(line)
    sys.stdout.flush()


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Full GitDorker-Elite scan lifecycle:

        Setup     : Parse args → resolve token → load dorks → build headers
        Loop      : For each dork → query API → skip (0 results) or
                    report + save (> 0 results)
        Discipline: Enforce per-request delay; auto-retry on rate limits
        Summary   : Print totals and output-file path on completion
    """
    print_banner()

    # ── Initialisation ────────────────────────────────────────────────────────
    args        = parse_args()
    token       = resolve_token(args.token)
    dorks       = load_dorks(args.dorks)
    headers     = build_headers(token)
    output_file = args.output or f"{args.domain}_hits.txt"
    total_dorks = len(dorks)
    total_hits  = 0

    # ── Configuration summary ─────────────────────────────────────────────────
    sep = Fore.YELLOW + "  " + "─" * 68 + Style.RESET_ALL
    print(sep)
    print(f"  {Fore.WHITE}Target domain  : {Fore.CYAN}{args.domain}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Dorks file     : {Fore.CYAN}{args.dorks}  ({total_dorks} dorks loaded){Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Output file    : {Fore.CYAN}{output_file}{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Delay/request  : {Fore.CYAN}{REQUEST_DELAY_S}s  (GitHub cap: 30 req/min){Style.RESET_ALL}")
    print(sep)
    print()

    # ── Main dorking loop ─────────────────────────────────────────────────────
    # داخل دالة main()
    # تنظيف الدومين مرة واحدة قبل اللوب
    clean_domain = re.sub(r"^https?://|/.*$", "", args.domain)

    for idx, dork in enumerate(dorks, start=1):
        render_progress(idx, total_dorks, dork)

        query  = f"{clean_domain} {dork}"
        result = query_github(query, headers)

        # Non-retriable error — skip this dork silently (already logged inside)
        if result is None:
            time.sleep(REQUEST_DELAY_S)
            continue

        total_count: int = result.get("total_count", 0)

        # ── The Decision Engine ───────────────────────────────────────────────
        if total_count == 0:
            # MISS — do absolutely nothing.
            # The in-place progress line already reflects the current dork.
            pass

        else:
            # HIT ─────────────────────────────────────────────────────────────
            #  1. Build the browser URL
            browser_url = make_browser_url(clean_domain, dork)
            noun        = "result" if total_count == 1 else "results"
            hit_line    = f"[HIT - {total_count} {noun}] -> {browser_url}"

            #  2. Print a bright-green hit message on a *fresh* line so it
            #     doesn't overwrite the progress counter we just rendered.
            sys.stdout.write("\n")
            print(Fore.GREEN + Style.BRIGHT + hit_line)

            #  3. Persist to the output file.
            #     "a" mode (append) is intentional: safe for multiple runs
            #     against the same domain without losing previous results.
            with open(output_file, "a", encoding="utf-8") as fh:
                fh.write(hit_line + "\n")

            total_hits += 1

        # Hard rate-limit delay between EVERY request — non-negotiable
        time.sleep(REQUEST_DELAY_S)

    # ── Scan summary ──────────────────────────────────────────────────────────
    sys.stdout.write("\n")   # Terminate the final progress / hit line cleanly

    print(f"\n{sep}")
    print(f"  {Fore.WHITE}Scan complete!{Style.RESET_ALL}")
    print(f"  {Fore.WHITE}Dorks tested : {Fore.CYAN}{total_dorks}{Style.RESET_ALL}")

    if total_hits > 0:
        print(
            f"  {Fore.WHITE}Hits found   : "
            f"{Fore.GREEN}{Style.BRIGHT}{total_hits}{Style.RESET_ALL}"
        )
        print(
            f"  {Fore.WHITE}Results saved: "
            f"{Fore.CYAN}{output_file}{Style.RESET_ALL}"
        )
    else:
        print(
            f"  {Fore.WHITE}Hits found   : "
            f"{Fore.YELLOW}0  —  No public exposure detected for this domain.{Style.RESET_ALL}"
        )

    print(sep + "\n")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()
