# Improved Playwright script for pastpapers.wiki Grade 13 Physics downloads
# Requirements: pip install playwright
# Then: playwright install

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import os
import re
import time

# Your list of URLs (add/remove as needed)
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
    "https://pastpapers.wiki/devi-balika-vidyalaya-physics-1st-term-test-paper-2023-grade-13/   ?swcfpc=1",
    "https://pastpapers.wiki/anula-vidyalaya-physics-1st-term-test-paper-2023-grade-13-2/?swcfpc=1",
    "https://pastpapers.wiki/ananda-college-physics-1st-term-test-paper-2023-grade-13/?swcfpc=1",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province-2/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2020-north-western-province-3/",
    "https://pastpapers.wiki/grade-13-physics-1st-term-test-paper-2018-north-western-province-tamil-medium/?swcfpc=1"
]

# Extended ad/tracker domains to block (helps prevent pop-ups & download errors)
blocked_domains = [
    "doubleclick.net", "googlesyndication.com", "googleadservices.com",
    "adservice.google.com", "adnxs.com", "pubmatic.com", "rubiconproject.com",
    "openx.net", "casalemedia.com", "smartadserver.com", "criteo.com",
    "taboola.com", "outbrain.com", "mgid.com", "revcontent.com",
    "adsafeprotected.com", "moatads.com", "scorecardresearch.com",
    "quantserve.com", "facebook.net", "connect.facebook.net",
    "onesignal.com", "pushengage.com",  # common push notification scripts
]

def should_block(url: str) -> bool:
    url_lower = url.lower()
    return any(domain in url_lower for domain in blocked_domains)

# Output folder
save_dir = "physics_2023_grade13_papers"
os.makedirs(save_dir, exist_ok=True)

with sync_playwright() as p:
    # Use headless=False if you want to watch what's happening (good for debugging)
    browser = p.chromium.launch(headless=True, args=["--disable-extensions", "--disable-popup-blocking"])
    context = browser.new_context(
        viewport={"width": 1280, "height": 800},
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    page = context.new_page()

    # Block ads/trackers globally
    page.route("**/*", lambda route: route.abort() if should_block(route.request.url) else route.continue_())

    # Close any unexpected popups/new tabs
    def handle_popup(popup):
        print("→ Popup/new tab detected → closing it")
        popup.close()

    page.on("popup", handle_popup)
    context.on("page", lambda new_page: new_page.close() if new_page != page else None)

    for i, url in enumerate(urls, 1):
        try:
            print(f"\n[{i}/{len(urls)}] Visiting: {url}")
            page.goto(url, wait_until="networkidle", timeout=45000)

            # Try to find the best download link
            download_link = None

            # Priority 1: Direct .pdf link with class wpfd_downloadlink
            pdf_links = page.locator('a.wpfd_downloadlink[href$=".pdf"]')
            if pdf_links.count() > 0:
                download_link = pdf_links.first
                print("Found direct .pdf link with wpfd_downloadlink class")

            # Priority 2: Any link ending with .pdf
            if not download_link:
                all_pdf = page.locator('a[href$=".pdf"]')
                if all_pdf.count() > 0:
                    download_link = all_pdf.first
                    print("Found generic .pdf link")

            # Priority 3: admin-ajax.php download endpoint
            if not download_link:
                ajax_links = page.locator('a[href*="admin-ajax.php"][href*="task=file.download"]')
                if ajax_links.count() > 0:
                    download_link = ajax_links.first
                    print("Found admin-ajax download link")

            if not download_link:
                print("→ No download link found. Skipping...")
                continue

            # Extract filename suggestion
            href = download_link.get_attribute("href")
            filename_match = re.search(r'([^/]+\.pdf)$', href)
            filename = filename_match.group(1) if filename_match else f"paper_{i}.pdf"

            # Try to make filename more readable from URL
            school_match = re.search(r'([a-z0-9\-]+)-physics', url)
            school = school_match.group(1).replace('-', ' ').title() if school_match else "Unknown"

            nice_name = f"{school} - 2023 Grade 13 Physics 1st Term - Sinhala.pdf"
            safe_name = re.sub(r'[^\w\s-]', '', nice_name).replace(' ', '_') + ".pdf"
            full_path = os.path.join(save_dir, safe_name)

            # Trigger download
            print(f"→ Clicking download → Saving as: {safe_name}")

            with page.expect_download(timeout=60000) as download_info:
                download_link.click()

            download = download_info.value
            download.save_as(full_path)
            print(f"✓ Success! Saved → {full_path}")

            time.sleep(1.5)  # polite delay

        except PlaywrightTimeoutError:
            print("→ Timeout while waiting for download or page load")
        except Exception as e:
            print(f"→ Error: {str(e)}")

    browser.close()

print("\nAll done! Check folder:", save_dir)
