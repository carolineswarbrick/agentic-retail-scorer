"""
Agentic Readiness Scorer — checks a retailer URL across two top-level pillars:

  AGENTIC TRUST    (can an AI agent trust this site?)
  AGENTIC READINESS (can an AI agent *operate* on this site?)

Each pillar is 0–100. The overall score is a weighted average.
All checks are passive HTTP / HTML analysis only — no JS execution.
"""

from __future__ import annotations

import re
import socket
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# Bot UA — used for robots.txt / llms.txt checks (honest bot identity)
BOT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; AgenticReadinessScorer/1.0; "
        "+https://github.com/agentic-retail-scorer)"
    )
}

# Browser UA — used to fetch HTML for content analysis (we're analysing what
# a human / rendered browser would see, not bypassing paywalls)
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-AU,en;q=0.9",
}

HEADERS = BOT_HEADERS  # kept for backwards compat
TIMEOUT = 6          # read timeout for main page fetches
TIMEOUT_SUB = 4      # robots.txt / llms.txt / sitemap — small files, fail fast
CONNECT_TIMEOUT = 4  # max seconds for TCP handshake + TLS


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class CheckResult:
    name: str
    passed: bool
    score: float          # 0.0 – 1.0
    weight: float         # relative weight within its category
    detail: str           # human-readable finding
    category: str         # which pillar / sub-category


@dataclass
class ScoredSite:
    url: str
    domain: str
    trust_score: float
    readiness_score: float
    overall_score: float
    grade: str
    checks: list[CheckResult]
    error: Optional[str] = None
    elapsed: float = 0.0

    def checks_by_category(self) -> dict[str, list[CheckResult]]:
        out: dict[str, list[CheckResult]] = {}
        for c in self.checks:
            out.setdefault(c.category, []).append(c)
        return out


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get(url: str, timeout: int = TIMEOUT, use_browser_ua: bool = False) -> Optional[requests.Response]:
    try:
        headers = BROWSER_HEADERS if use_browser_ua else BOT_HEADERS
        # Split connect/read timeouts: short connect cap, longer read
        r = requests.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, timeout),
                         allow_redirects=True)
        return r
    except Exception:
        return None


def _grade(score: float) -> str:
    if score >= 80:
        return "A"
    if score >= 65:
        return "B"
    if score >= 50:
        return "C"
    if score >= 35:
        return "D"
    return "F"


def _normalise_url(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw.rstrip("/")


def _domain(url: str) -> str:
    return urlparse(url).netloc.lstrip("www.")


# ─────────────────────────────────────────────────────────────────────────────
# Individual check functions  →  return CheckResult
# ─────────────────────────────────────────────────────────────────────────────

# ── AGENTIC TRUST ─────────────────────────────────────────────────────────────

def check_https(base_url: str, resp: Optional[requests.Response]) -> CheckResult:
    passed = base_url.startswith("https://") and (resp is not None and resp.url.startswith("https://"))
    return CheckResult(
        name="HTTPS / TLS",
        passed=passed,
        score=1.0 if passed else 0.0,
        weight=1.5,
        detail="Site is served over HTTPS." if passed else "Site does not enforce HTTPS.",
        category="Trust: Security",
    )


def check_security_headers(resp: Optional[requests.Response]) -> CheckResult:
    if resp is None:
        return CheckResult("Security Headers", False, 0.0, 1.0, "Could not fetch page.", "Trust: Security")
    headers = {k.lower(): v for k, v in resp.headers.items()}
    wanted = ["strict-transport-security", "x-content-type-options", "x-frame-options", "content-security-policy"]
    found = [h for h in wanted if h in headers]
    score = len(found) / len(wanted)
    detail = f"Found {len(found)}/{len(wanted)}: {', '.join(found) or 'none'}."
    return CheckResult("Security Headers", len(found) >= 2, score, 1.0, detail, "Trust: Security")


def check_privacy_policy(soup: Optional[BeautifulSoup], base_url: str) -> CheckResult:
    if soup is None:
        return CheckResult("Privacy Policy", False, 0.0, 1.0, "Could not fetch page.", "Trust: Transparency")
    links = [a.get("href", "") for a in soup.find_all("a", href=True)]
    keywords = ["privacy", "privacy-policy"]
    found = any(any(k in (l or "").lower() for k in keywords) for l in links)
    return CheckResult(
        "Privacy Policy",
        found,
        1.0 if found else 0.0,
        1.0,
        "Privacy policy link found." if found else "No privacy policy link detected.",
        "Trust: Transparency",
    )


def check_returns_policy(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Returns Policy", False, 0.0, 1.0, "Could not fetch page.", "Trust: Transparency")
    text = soup.get_text(" ", strip=True).lower()
    links = " ".join([a.get("href", "").lower() for a in soup.find_all("a", href=True)])
    found = any(k in text or k in links for k in ["return", "refund", "exchange"])
    return CheckResult(
        "Returns Policy",
        found,
        1.0 if found else 0.0,
        1.0,
        "Returns/refund information found." if found else "No returns/refund info detected.",
        "Trust: Transparency",
    )


def check_contact_info(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Contact Info", False, 0.0, 0.5, "Could not fetch page.", "Trust: Transparency")
    text = soup.get_text(" ", strip=True).lower()
    signals = ["contact us", "contact", "support", "help", "customer service", "live chat"]
    found = sum(1 for s in signals if s in text)
    score = min(found / 3, 1.0)
    detail = f"Found {found} contact/support signals."
    return CheckResult("Contact Info", found >= 1, score, 0.5, detail, "Trust: Transparency")


def check_robots_txt(base_url: str, skip: bool = False) -> tuple[CheckResult, CheckResult, CheckResult]:
    """Returns three checks: robots exists, AI bots explicitly allowed, AI bots explicitly blocked."""
    if skip:
        detail = "Skipped — site blocks bot requests."
        return (
            CheckResult("robots.txt Present", False, 0.0, 0.5, detail, "Trust: AI Signals"),
            CheckResult("AI Bots Blocked",    False, 0.0, 1.5, detail, "Trust: AI Signals"),
            CheckResult("llms.txt Present",   False, 0.0, 2.0, detail, "Trust: AI Signals"),
        )

    robots_url = urljoin(base_url + "/", "robots.txt")
    resp = _get(robots_url, timeout=TIMEOUT_SUB)
    content = (resp.text if resp and resp.status_code == 200 else "").lower()
    exists = bool(content.strip())

    ai_bots = ["gptbot", "claudebot", "perplexitybot", "anthropic-ai", "google-extended", "cohere-ai", "ccbot"]
    disallowed_bots = [b for b in ai_bots if re.search(rf"user-agent:\s*{re.escape(b)}", content)
                       and re.search(r"disallow:\s*/", content[content.find(b):content.find(b)+200])]
    allowed_bots = [b for b in ai_bots if re.search(rf"user-agent:\s*{re.escape(b)}", content)
                    and re.search(r"allow:\s*/", content[content.find(b):content.find(b)+200])]

    llms_txt_url = urljoin(base_url + "/", "llms.txt")
    llms_resp = _get(llms_txt_url, timeout=TIMEOUT_SUB)
    has_llms = llms_resp is not None and llms_resp.status_code == 200 and len(llms_resp.text.strip()) > 20

    c_robots = CheckResult(
        "robots.txt Present",
        exists,
        1.0 if exists else 0.0,
        0.5,
        "robots.txt found." if exists else "No robots.txt found.",
        "Trust: AI Signals",
    )
    c_blocked = CheckResult(
        "AI Bots Blocked",
        bool(disallowed_bots),
        1.0 if disallowed_bots else 0.0,
        1.5,
        f"Blocked: {', '.join(disallowed_bots)}." if disallowed_bots else "No AI bots explicitly blocked.",
        "Trust: AI Signals",
    )
    # Note: blocking is a negative signal for agentic readiness but a possible trust signal.
    # We score blocking as 0 for agentic readiness (handled separately below).
    c_llms = CheckResult(
        "llms.txt Present",
        has_llms,
        1.0 if has_llms else 0.0,
        2.0,
        "llms.txt found — site has AI-specific guidance." if has_llms else "No llms.txt found.",
        "Trust: AI Signals",
    )
    return c_robots, c_blocked, c_llms


def check_dark_patterns(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Dark Patterns", False, 0.5, 1.0, "Could not fetch page.", "Trust: Transparency")
    text = soup.get_text(" ", strip=True).lower()
    dark = [
        "only [0-9]+ left", r"\d+ (people|others) (viewing|looking)",
        "limited time", "hurry", "expires in", "selling fast", "almost gone",
        "flash sale", "today only",
    ]
    hits = [p for p in dark if re.search(p, text)]
    score = max(0.0, 1.0 - len(hits) * 0.3)
    passed = len(hits) == 0
    detail = f"No dark patterns detected." if passed else f"Possible dark patterns: {len(hits)} signal(s) found."
    return CheckResult("Dark Patterns (absent)", passed, score, 1.0, detail, "Trust: Transparency")


# ── AGENTIC READINESS ─────────────────────────────────────────────────────────

def check_schema_org(soup: Optional[BeautifulSoup], resp: Optional[requests.Response]) -> CheckResult:
    if soup is None:
        return CheckResult("Schema.org Markup", False, 0.0, 2.0, "Could not fetch page.", "Readiness: Data")
    scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    count = len(scripts)
    content = " ".join(s.get_text() for s in scripts).lower()
    product_types = ["product", "offer", "breadcrumblist", "organization", "website", "searchaction"]
    found_types = [t for t in product_types if t in content]
    score = min(len(found_types) / 3, 1.0)
    detail = f"{count} JSON-LD block(s); types: {', '.join(found_types) or 'none'}."
    return CheckResult("Schema.org Markup", len(found_types) >= 1, score, 2.0, detail, "Readiness: Data")


def check_sitemap(base_url: str, skip: bool = False) -> CheckResult:
    if skip:
        return CheckResult("Sitemap", False, 0.0, 1.0, "Skipped — site blocks bot requests.", "Readiness: Data")
    for path in ["/sitemap.xml", "/sitemap_index.xml", "/sitemaps/sitemap.xml"]:
        r = _get(base_url + path, timeout=TIMEOUT_SUB)
        if r and r.status_code == 200 and "<url" in r.text.lower():
            return CheckResult("Sitemap", True, 1.0, 1.0, f"Sitemap found at {path}.", "Readiness: Data")
    return CheckResult("Sitemap", False, 0.0, 1.0, "No sitemap.xml found.", "Readiness: Data")


def check_search(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("On-Site Search", False, 0.0, 1.5, "Could not fetch page.", "Readiness: Navigation")
    forms = soup.find_all("form")
    inputs = soup.find_all("input")
    search_inputs = [i for i in inputs if any(
        k in (i.get("type", "") + i.get("name", "") + i.get("placeholder", "") + i.get("aria-label", "")).lower()
        for k in ["search", "query", "q", "find"]
    )]
    has_search = bool(search_inputs)
    # Also check for SearchAction in JSON-LD
    scripts = " ".join(s.get_text() for s in soup.find_all("script", attrs={"type": "application/ld+json"})).lower()
    has_search_action = "searchaction" in scripts
    passed = has_search or has_search_action
    detail = ("Search input found" + (" + SearchAction schema" if has_search_action else "") + ".") if passed \
        else "No search functionality detected."
    return CheckResult("On-Site Search", passed, 1.0 if passed else 0.0, 1.5, detail, "Readiness: Navigation")


def check_navigation(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Clear Navigation", False, 0.0, 1.0, "Could not fetch page.", "Readiness: Navigation")
    nav_elements = soup.find_all(["nav", "header"])
    links_in_nav = []
    for n in nav_elements:
        links_in_nav += n.find_all("a", href=True)
    score = min(len(links_in_nav) / 10, 1.0)
    detail = f"{len(links_in_nav)} navigation links detected."
    return CheckResult("Clear Navigation", len(links_in_nav) >= 5, score, 1.0, detail, "Readiness: Navigation")


def check_structured_product_data(soup: Optional[BeautifulSoup]) -> CheckResult:
    """Check for price, availability, and product identifiers in markup."""
    if soup is None:
        return CheckResult("Product Data Richness", False, 0.0, 2.0, "Could not fetch page.", "Readiness: Data")
    text = soup.get_text(" ", strip=True).lower()
    scripts = " ".join(s.get_text() for s in soup.find_all("script", attrs={"type": "application/ld+json"})).lower()
    all_text = text + " " + scripts
    signals = {
        "Price": any(p in all_text for p in ["price", "\"price\"", "pricecurrency"]),
        "Availability": any(p in all_text for p in ["instock", "in stock", "availability", "outofstock"]),
        "SKU/GTIN": any(p in all_text for p in ["sku", "gtin", "mpn", "barcode", "isbn"]),
        "Ratings": any(p in all_text for p in ["aggregaterating", "ratingvalue", "reviewcount"]),
        "Shipping": any(p in all_text for p in ["shipping", "delivery", "shippingdetails"]),
    }
    found = sum(1 for v in signals.values() if v)
    score = found / len(signals)
    detail = "Rich: " + ", ".join(k for k, v in signals.items() if v) + (
        f". Missing: {', '.join(k for k, v in signals.items() if not v)}." if found < len(signals) else "."
    )
    return CheckResult("Product Data Richness", found >= 3, score, 2.0, detail, "Readiness: Data")


def check_guest_checkout(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Guest Checkout Signal", False, 0.0, 1.5, "Could not fetch page.", "Readiness: Checkout")
    text = soup.get_text(" ", strip=True).lower()
    links = " ".join(a.get("href", "").lower() for a in soup.find_all("a", href=True))
    signals = ["guest", "checkout", "cart", "basket", "bag", "add to cart", "buy now"]
    found = sum(1 for s in signals if s in text or s in links)
    score = min(found / 3, 1.0)
    detail = f"{found} checkout/cart signals found."
    return CheckResult("Guest Checkout Signal", found >= 2, score, 1.5, detail, "Readiness: Checkout")


def check_bnpl(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("BNPL / Payment Options", False, 0.0, 1.0, "Could not fetch page.", "Readiness: Checkout")
    text = soup.get_text(" ", strip=True).lower()
    bnpl_providers = ["afterpay", "zip pay", "zippay", "zip co", "klarna", "laybuy", "humm", "openpay", "latitude pay"]
    card_schemes = ["visa", "mastercard", "amex", "paypal", "apple pay", "google pay"]
    found_bnpl = [p for p in bnpl_providers if p in text]
    found_cards = [p for p in card_schemes if p in text]
    total = len(found_bnpl) + len(found_cards)
    score = min(total / 4, 1.0)
    detail = f"BNPL: {', '.join(found_bnpl) or 'none'}. Cards/wallets: {', '.join(found_cards) or 'none'}."
    return CheckResult("BNPL / Payment Options", bool(found_bnpl or found_cards), score, 1.0, detail, "Readiness: Checkout")


def check_api_headless(soup: Optional[BeautifulSoup], resp: Optional[requests.Response], base_url: str) -> CheckResult:
    """Detect headless/API-first signals."""
    signals = []
    if resp:
        headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
        if "x-shopify-shop-api-call-limit" in headers or "x-shopify" in str(headers):
            signals.append("Shopify (API-first)")
        if "x-powered-by" in headers and "next" in headers["x-powered-by"]:
            signals.append("Next.js")
        if "cf-ray" in headers:
            signals.append("Cloudflare CDN")
    if soup:
        scripts = [s.get("src", "") for s in soup.find_all("script", src=True)]
        if any("graphql" in s.lower() for s in scripts):
            signals.append("GraphQL endpoint")
        if any("_next" in s for s in scripts):
            signals.append("Next.js (headless)")
        if any("storefront" in s.lower() for s in scripts):
            signals.append("Storefront API")
        page_text = soup.get_text().lower()
        if "api.myshopify" in page_text or "/api/2" in page_text:
            signals.append("Shopify Storefront API")
    # Check for API docs link
    if soup:
        api_links = [a.get("href", "") for a in soup.find_all("a", href=True)
                     if any(k in a.get("href", "").lower() for k in ["api", "developer", "graphql"])]
        if api_links:
            signals.append(f"API/Dev links ({len(api_links)})")

    score = min(len(signals) / 2, 1.0)
    detail = f"Signals: {', '.join(signals)}." if signals else "No headless/API signals detected."
    return CheckResult("Headless / API Readiness", bool(signals), score, 1.5, detail, "Readiness: API")


def check_accessibility(soup: Optional[BeautifulSoup]) -> CheckResult:
    if soup is None:
        return CheckResult("Accessibility Basics", False, 0.0, 1.0, "Could not fetch page.", "Readiness: Navigation")
    imgs = soup.find_all("img")
    imgs_with_alt = [i for i in imgs if i.get("alt") is not None]
    alt_score = len(imgs_with_alt) / max(len(imgs), 1)
    has_lang = bool(soup.find("html") and soup.find("html").get("lang"))
    has_skip = bool(soup.find("a", href="#main") or soup.find("a", string=re.compile("skip", re.I)))
    labels = soup.find_all("label")
    signals = [alt_score >= 0.7, has_lang, bool(labels)]
    score = sum(1 for s in signals if s) / len(signals)
    detail = (
        f"Alt text: {alt_score:.0%} of images. "
        f"Lang attr: {'yes' if has_lang else 'no'}. "
        f"Form labels: {len(labels)}."
    )
    return CheckResult("Accessibility Basics", score >= 0.5, score, 1.0, detail, "Readiness: Navigation")


def check_performance_hints(resp: Optional[requests.Response], soup: Optional[BeautifulSoup]) -> CheckResult:
    if resp is None:
        return CheckResult("Performance Hints", False, 0.0, 0.5, "Could not fetch page.", "Readiness: Data")
    signals = []
    elapsed = getattr(resp, "elapsed", None)
    if elapsed and elapsed.total_seconds() < 3.0:
        signals.append(f"Fast TTFB ({elapsed.total_seconds():.1f}s)")
    headers = {k.lower(): v.lower() for k, v in resp.headers.items()}
    if "cache-control" in headers:
        signals.append("Cache-Control set")
    if "x-cache" in headers or "cf-cache-status" in headers:
        signals.append("CDN caching detected")
    if soup:
        lazy_imgs = soup.find_all("img", attrs={"loading": "lazy"})
        if lazy_imgs:
            signals.append(f"Lazy loading ({len(lazy_imgs)} imgs)")
    score = min(len(signals) / 3, 1.0)
    detail = ", ".join(signals) if signals else "No strong performance signals detected."
    return CheckResult("Performance Hints", bool(signals), score, 0.5, detail, "Readiness: Data")


# ─────────────────────────────────────────────────────────────────────────────
# Main scoring function
# ─────────────────────────────────────────────────────────────────────────────

TRUST_CATEGORIES = {"Trust: Security", "Trust: Transparency", "Trust: AI Signals"}
READINESS_CATEGORIES = {"Readiness: Data", "Readiness: Navigation", "Readiness: Checkout", "Readiness: API"}


def score_url(raw_url: str) -> ScoredSite:
    t0 = time.time()
    url = _normalise_url(raw_url)
    domain = _domain(url)
    checks: list[CheckResult] = []

    # Fire bot and browser fetches concurrently — WAF-blocking sites stall the bot
    # connection, so parallel fetches mean the browser result arrives first.
    # Bot gets a tighter read timeout since we only need its headers/status.
    from concurrent.futures import ThreadPoolExecutor as _TPE
    with _TPE(max_workers=2) as _ex:
        _f_bot  = _ex.submit(_get, url, 4, False)   # bot: 4s connect, 4s read
        _f_brow = _ex.submit(_get, url, TIMEOUT, True)
        resp_bot = _f_bot.result()
        resp     = _f_brow.result()

    bot_hard_blocked    = resp_bot is not None and resp_bot.status_code in (403, 429, 503)
    bot_silently_dropped = resp_bot is None  # timed out / connection reset
    soup: Optional[BeautifulSoup] = None
    if resp and resp.status_code < 400:
        try:
            soup = BeautifulSoup(resp.content, "lxml")
        except Exception:
            try:
                soup = BeautifulSoup(resp.content, "html.parser")
            except Exception:
                pass

    # Use bot resp for header checks (those are what agents see); browser resp for HTML
    security_resp = resp_bot if resp_bot and resp_bot.status_code < 400 else resp

    # Skip all subsequent bot sub-requests if the site is silently dropping bot connections —
    # the site is unreachable for bots, and each sub-request would burn its full timeout.
    site_down = resp is None  # even the browser fetch failed — truly unreachable
    skip_bot_requests = bot_silently_dropped and not site_down

    error = None
    if resp is None:
        error = f"Could not connect to {url}."
    elif resp.status_code >= 400:
        error = f"HTTP {resp.status_code} from {url}."

    # ── Trust checks ──────────────────────────────────────────────────────────
    checks.append(check_https(url, resp))
    checks.append(check_security_headers(security_resp))
    checks.append(check_privacy_policy(soup, url))
    checks.append(check_returns_policy(soup))
    checks.append(check_contact_info(soup))
    checks.append(check_dark_patterns(soup))

    r_robots, r_blocked, r_llms = check_robots_txt(url, skip=skip_bot_requests)
    checks.append(r_robots)
    # AI blocking is a negative for agentic readiness but neutral/positive for trust
    checks.append(r_blocked)
    checks.append(r_llms)

    # ── Readiness checks ──────────────────────────────────────────────────────
    checks.append(check_schema_org(soup, resp))
    checks.append(check_sitemap(url, skip=skip_bot_requests))
    checks.append(check_search(soup))
    checks.append(check_navigation(soup))
    checks.append(check_structured_product_data(soup))
    checks.append(check_guest_checkout(soup))
    checks.append(check_bnpl(soup))
    checks.append(check_api_headless(soup, resp, url))
    checks.append(check_accessibility(soup))
    checks.append(check_performance_hints(resp, soup))

    # ── Compute scores ────────────────────────────────────────────────────────
    def weighted_avg(cat_checks: list[CheckResult]) -> float:
        total_weight = sum(c.weight for c in cat_checks)
        if total_weight == 0:
            return 0.0
        return sum(c.score * c.weight for c in cat_checks) / total_weight * 100

    # For AI blocking: it counts against readiness, not trust
    trust_checks = [c for c in checks if c.category in TRUST_CATEGORIES and c.name != "AI Bots Blocked"]
    readiness_checks = [c for c in checks if c.category in READINESS_CATEGORIES]

    # Penalise readiness if AI bots are blocked in robots.txt
    ai_blocked_robots = next((c for c in checks if c.name == "AI Bots Blocked"), None)
    if ai_blocked_robots and ai_blocked_robots.passed:
        readiness_checks = readiness_checks + [
            CheckResult("AI Access Permitted", False, 0.0, 2.0,
                        "AI crawlers explicitly disallowed in robots.txt.", "Readiness: API")
        ]
    else:
        readiness_checks = readiness_checks + [
            CheckResult("AI Access Permitted", True, 1.0, 2.0,
                        "No AI crawler restrictions in robots.txt.", "Readiness: API")
        ]

    # Penalise readiness if bot UA is hard-blocked or silently dropped
    if bot_hard_blocked:
        readiness_checks = readiness_checks + [
            CheckResult("Bot HTTP Access", False, 0.0, 1.5,
                        f"HTTP {resp_bot.status_code} returned to bot user-agent — agents cannot access this site.",
                        "Readiness: API")
        ]
    elif bot_silently_dropped:
        readiness_checks = readiness_checks + [
            CheckResult("Bot HTTP Access", False, 0.0, 1.5,
                        "Bot connection timed out — site appears to silently block automated requests.",
                        "Readiness: API")
        ]
    else:
        readiness_checks = readiness_checks + [
            CheckResult("Bot HTTP Access", True, 1.0, 1.5,
                        "Site responds to bot user-agent requests.", "Readiness: API")
        ]

    trust_score = weighted_avg(trust_checks)
    readiness_score = weighted_avg(readiness_checks)

    # Overall: 40% trust, 60% readiness
    overall = trust_score * 0.4 + readiness_score * 0.6

    elapsed = time.time() - t0

    return ScoredSite(
        url=url,
        domain=domain,
        trust_score=round(trust_score, 1),
        readiness_score=round(readiness_score, 1),
        overall_score=round(overall, 1),
        grade=_grade(overall),
        checks=checks,
        error=error,
        elapsed=round(elapsed, 1),
    )
