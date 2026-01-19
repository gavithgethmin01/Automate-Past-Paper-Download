# improved_playwright_fast_download.py
import os
import re
import time
import signal
import sys
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

# --- Config ---
HEADLESS = False
SAVE_DIR = "physics_2023_grade13_papers_fast"
os.makedirs(SAVE_DIR, exist_ok=True)

# minimal ad / third-party blocking keywords (extend as needed)
AD_KEYWORDS = [
    "doubleclick", "googlesyndication", "adservice", "adsystem", "ads.", "/ads/", "advert",
    "adserver", "tracking", "analytics", "facebook.net", "google-analytics", "gstatic", "taboola",
    "outbrain", "criteo", "scorecardresearch", "/banner", "adrotate"
]

# your pages
urls = [
    "https://pastpapers.wiki/north-central-province-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/visakha-vidyalaya-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/thurstan-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/taxila-central-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/taxila-central-college-physics-1st-term-test-paper-2023-grade-13-2/?swcfpc=1",
    "https://pastpapers.wiki/sripalee-national-school-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/sivali-central-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/seethawaka-national-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/royal-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/royal-college-physics-1st-term-test-paper-2023-grade-13-2/?swcfpc=1",
    "https://pastpapers.wiki/mahanama-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/mahamaya-girls-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/ferguson-high-school-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/dharmapala-vidyalaya-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/devi-balika-vidyalaya-physics-1st-term-test-paper-2023-grade-13-2/?swcfpc=1",
    "https://pastpapers.wiki/devi-balika-vidyalaya-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/anula-vidyalaya-physics-1st-term-test-paper-2023-grade-13-2/?swcfpc=1",
    "https://pastpapers.wiki/ananda-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province-2/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province-3/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2018-north-western-province-tamil-medium/?swcfpc=1"
]

# --- Helpers ---
def safe_filename(s: str) -> str:
    s = re.sub(r"[\\/:\*\?\"<>\|]+", "", s)  # remove forbidden chars
    s = re.sub(r"\s+", " ", s).strip()
    return s

def looks_like_ad(url: str) -> bool:
    lu = url.lower()
    return any(k in lu for k in AD_KEYWORDS)

def domain_of(url: str) -> str:
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""

def signal_handler(sig, frame):
    print("\n→ Ctrl+C detected — exiting cleanly.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# --- Main script ---
with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS, args=["--no-sandbox", "--disable-dev-shm-usage"])
    # set a context; accept_downloads not required because we do direct fetch where possible
    context = browser.new_context(user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36")
    page = context.new_page()
    page.set_default_timeout(30_000)  # safer default

    # route: abort useless/third-party resources to speed up loading
    def route_handler(route, request):
        url = request.url
        resource = request.resource_type
        # Abort obvious ad/tracking URLs
        if looks_like_ad(url):
            return route.abort()
        # If it's a third-party image/font/media, abort to speed things up
        req_domain = domain_of(url)
        # allow same-origin resources but block third-party heavy resources
        if req_domain and req_domain not in domain_of(page.url):
            if resource in ("image", "font", "media"):
                return route.abort()
        # let everything else through
        return route.continue_()

    # attach route
    try:
        page.route("**/*", route_handler)
    except PlaywrightError:
        # in case route fails, continue without routing
        pass

    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] Visiting: {url}")
        try:
            page.goto(url, wait_until="networkidle", timeout=45_000)
        except PlaywrightTimeoutError:
            print("→ initial navigation timed out — attempting a reload with longer timeout")
            try:
                page.reload(timeout=60_000, wait_until="networkidle")
            except Exception as e:
                print("→ reload failed:", e)
                continue
        except Exception as e:
            print("→ navigation error:", e)
            continue

        # find candidate download anchors
        download_href = None
        try:
            # first try the known selector
            el = page.locator('a.wpfd_downloadlink[href$=".pdf"]')
            if el.count() > 0:
                download_href = el.first.get_attribute("href")
            else:
                # fallback: any anchor that ends with .pdf
                anchors = page.locator('a[href*=".pdf"]')
                if anchors.count() > 0:
                    # choose the first one that looks like a direct pdf
                    for idx in range(anchors.count()):
                        href = anchors.nth(idx).get_attribute("href")
                        if href and href.lower().endswith(".pdf"):
                            download_href = href
                            break
                # last fallback: look for buttons that may trigger pdf via JS and get their href if present
                if not download_href:
                    btns = page.locator('a, button')
                    for idx in range(min(40, btns.count())):
                        try:
                            href = btns.nth(idx).get_attribute("href")
                            if href and ".pdf" in href.lower():
                                download_href = href
                                break
                        except Exception:
                            continue
        except Exception as e:
            print("→ error searching for links:", e)

        def write_bytes_to_file(bts, path):
            with open(path, "wb") as f:
                f.write(bts)

        # Build a nice file name
        def make_nice_name(base_url, original_name=None):
            school_match = re.search(r'([a-z0-9\-]+)-physics', base_url, re.I)
            school = school_match.group(1).replace('-', ' ').title() if school_match else None
            if original_name:
                base = original_name
            else:
                base = f"{school or 'paper'} - 2023 Grade 13 Physics 1st Term"
            name = safe_filename(base)
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            return name

        # If we found a direct href ending with .pdf -> fetch via Playwright request (fast & ad bypass)
        saved = False
        if download_href and download_href.lower().endswith(".pdf"):
            try:
                # normalize relative URLs
                if download_href.startswith("/"):
                    parsed = urlparse(url)
                    download_href = f"{parsed.scheme}://{parsed.hostname}{download_href}"
                print("→ Found direct PDF href. Fetching directly (no click).")
                # use the context's request to GET the pdf
                resp = context.request.get(download_href, timeout=60_000)
                if resp.status == 200:
                    content_type = resp.headers.get("content-type", "")
                    if "pdf" in content_type or download_href.lower().endswith(".pdf"):
                        body = resp.body()
                        fname = make_nice_name(url, os.path.basename(download_href))
                        out_path = os.path.join(SAVE_DIR, fname)
                        write_bytes_to_file(body, out_path)
                        print(f"✓ Saved direct PDF → {out_path}")
                        saved = True
                    else:
                        print("→ fetched resource is not a PDF according to Content-Type, will try clicking instead.")
                else:
                    print(f"→ Direct fetch returned status {resp.status}. Will try clicking.")
            except Exception as e:
                print("→ Direct fetch failed:", e)

        # If not saved yet, try clicking the download element (but capture the actual PDF response)
        if not saved:
            try:
                print("→ Attempting JS-click flow and watching for a PDF response (works if a click streams a PDF).")
                # try to find any clickable element that likely triggers download
                click_locator = None
                try:
                    if page.locator('a.wpfd_downloadlink').count() > 0:
                        click_locator = page.locator('a.wpfd_downloadlink').first
                    elif page.locator('a[href*=".pdf"]').count() > 0:
                        click_locator = page.locator('a[href*=".pdf"]').first
                    else:
                        # fallback: any button or link with text "download"
                        cand = page.locator("text=/download/i")
                        if cand.count() > 0:
                            click_locator = cand.first
                except Exception:
                    click_locator = None

                # Prepare to catch a PDF response
                pdf_response = None
                try:
                    matcher = lambda r: "content-type" in r.headers and "pdf" in r.headers["content-type"].lower()
                    with page.expect_response(matcher, timeout=45_000) as resp_info:
                        if click_locator:
                            click_locator.click(timeout=20_000)
                        else:
                            # if no click locator, try clicking the first anchor to trigger something
                            anchors = page.locator("a")
                            if anchors.count() > 0:
                                anchors.first.click(timeout=20_000)
                            else:
                                raise RuntimeError("No clickable download element found.")
                    pdf_response = resp_info.value
                except PlaywrightTimeoutError:
                    print("→ No PDF response captured within timeout after clicking.")
                except Exception as e:
                    print("→ Clicking attempt raised:", e)

                if pdf_response:
                    try:
                        body = pdf_response.body()
                        # attempt to get filename from content-disposition header
                        cd = pdf_response.headers.get("content-disposition", "")
                        fn = None
                        m = re.search(r'filename\*?=([^;]+)', cd)
                        if m:
                            fn = m.group(1).strip().strip('\"\' ')
                        # fallback to URL basename
                        if not fn:
                            fn = os.path.basename(urlparse(pdf_response.url).path) or None
                        nice = make_nice_name(url, fn)
                        out_path = os.path.join(SAVE_DIR, nice)
                        write_bytes_to_file(body, out_path)
                        print(f"✓ Saved captured PDF response → {out_path}")
                        saved = True
                    except Exception as e:
                        print("→ failed to save captured PDF:", e)

            except Exception as outer_e:
                print("→ Download-by-click flow failed:", outer_e)

        if not saved:
            print("→ Couldn't get the PDF automatically. Trying a last-resort approach (open in new tab and wait for download).")
            try:
                # open a new page and click with expect_download (handles real download events)
                newp = context.new_page()
                newp.goto(url, wait_until="networkidle", timeout=30_000)
                el = None
                if newp.locator('a.wpfd_downloadlink').count() > 0:
                    el = newp.locator('a.wpfd_downloadlink').first
                elif newp.locator('a[href*=".pdf"]').count() > 0:
                    el = newp.locator('a[href*=".pdf"]').first

                if el:
                    try:
                        with newp.expect_download(timeout=60_000) as dl_info:
                            el.click()
                        dl = dl_info.value
                        suggested = dl.suggested_filename or f"paper_{i}.pdf"
                        fname = make_nice_name(url, suggested)
                        out_path = os.path.join(SAVE_DIR, fname)
                        dl.save_as(out_path)
                        print(f"✓ Downloaded via download event → {out_path}")
                        saved = True
                    except PlaywrightTimeoutError:
                        print("→ download event timed out.")
                newp.close()
            except Exception as e:
                print("→ last-resort approach failed:", e)

        # small polite delay but keep it short
        time.sleep(1.1)

    try:
        browser.close()
    except Exception:
        pass

print("\nAll done. Check folder:", SAVE_DIR)
