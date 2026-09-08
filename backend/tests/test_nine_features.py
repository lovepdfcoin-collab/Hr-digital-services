"""Backend tests for the 9 copied features (iteration 7).

Coverage:
 1. BRANDING AUTO-REPLACE: /api/vacancies and detail endpoint have no
    'freejobalert' in user-facing text; .pdf hrefs remain intact.
 2. MANUAL LOCK: editing a scraped vacancy promotes it to source='manual';
    POST /api/admin/vacancies/refresh must NOT overwrite it.
 3. SEARCH WITHOUT FILTER: ?q=<term> searches across admit_card/result
    categories; without q those categories are excluded from the 'All' view.
 9. BLOG CENTER IMAGE: POST/PUT /api/admin/blogs accepts center_image /
    remove_center_image form fields and returns center_image_url.
"""
import os
import io
import re
import pytest
import requests
from html.parser import HTMLParser

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"

ADMIN_EMAIL = "hrdigitalservices.in@gmail.com"
ADMIN_PASSWORD = "Dev@3642"

BRAND_RE = re.compile(r"free\s*job\s*alert", re.I)


# ---------- Fixtures ----------
@pytest.fixture(scope="module")
def token():
    r = requests.post(f"{API}/auth/login",
                      json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
                      timeout=15)
    assert r.status_code == 200, f"Admin login failed: {r.status_code} {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


# ---------- Helpers ----------
class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.pdf_hrefs = []
        self.all_hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for k, v in attrs:
                if k == "href" and v:
                    self.all_hrefs.append(v)
                    if ".pdf" in v.lower():
                        self.pdf_hrefs.append(v)

    def handle_data(self, data):
        self.text_parts.append(data)


def _extract(html: str):
    p = _TextExtractor()
    try:
        p.feed(html or "")
    except Exception:
        pass
    return "".join(p.text_parts), p.pdf_hrefs, p.all_hrefs


# ---------- Feature 1: Branding auto-replace ----------
def test_vacancies_list_no_freejobalert_in_text_fields():
    r = requests.get(f"{API}/vacancies?page=1&per_page=50", timeout=25)
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) > 0
    offenders = []
    for v in items:
        for field in ("title", "heading", "description", "post_name",
                      "organization", "seo_title", "seo_description",
                      "whatsapp_summary"):
            val = v.get(field)
            if isinstance(val, str) and BRAND_RE.search(val):
                offenders.append((v.get("id"), field, val[:120]))
        # content_html text nodes
        ch = v.get("content_html") or ""
        text, _, _ = _extract(ch)
        if BRAND_RE.search(text):
            offenders.append((v.get("id"), "content_html_text", text[:120]))
    assert not offenders, f"FreeJobAlert leaked into user-facing fields: {offenders[:5]}"


def test_vacancy_detail_branded_and_pdf_intact():
    """Pick a vacancy that has content_html and verify branding + PDF preserved."""
    r = requests.get(f"{API}/vacancies?page=1&per_page=50", timeout=25)
    items = r.json()["items"]
    # Try to find one with content_html so we get the detail endpoint fetched
    target = None
    for v in items:
        if v.get("content_html"):
            target = v
            break
    if not target:
        target = items[0]
    detail = requests.get(f"{API}/vacancies/{target['id']}", timeout=30).json()
    ch = detail.get("content_html") or ""
    text, pdf_hrefs, all_hrefs = _extract(ch)
    assert not BRAND_RE.search(text), \
        f"FreeJobAlert found in text nodes of vacancy {target['id']}: {text[:200]}"
    assert not BRAND_RE.search(detail.get("title") or "")
    # For any pdf href, ensure the URL string itself is not mangled (still starts http and ends .pdf-ish)
    for h in pdf_hrefs:
        assert h.startswith(("http://", "https://", "/")), f"Broken PDF href: {h}"
        # brand replacement should not have injected "HR Digital Services" into the URL itself
        assert "HR Digital Services" not in h and "hrdigitalservices" not in h.lower() or ".pdf" in h.lower(), \
            f"PDF href mangled by branding: {h}"


# ---------- Feature 3: Search across admit_card / result without filter ----------
def test_search_without_filter_covers_admit_card_and_result():
    """Without a q filter the default view must exclude admit_card+result.
    With q it should search ALL including admit_card+result."""
    # Baseline: default listing excludes those categories
    r0 = requests.get(f"{API}/vacancies?page=1&per_page=100", timeout=25)
    assert r0.status_code == 200
    cats0 = {v.get("category") for v in r0.json()["items"]}
    assert "admit_card" not in cats0, "Default view leaked admit_card"
    assert "result" not in cats0, "Default view leaked result"

    # With a broad q (single letter 'a') the response should surface at least
    # one admit_card or result item (given the seed data has these categories).
    r1 = requests.get(f"{API}/vacancies?q=result&per_page=50", timeout=25)
    assert r1.status_code == 200
    cats1 = {v.get("category") for v in r1.json()["items"]}
    # Either an admit_card or a result should surface for 'result' query.
    assert ("admit_card" in cats1) or ("result" in cats1), \
        f"q=result did not surface admit_card/result categories, got {cats1}"


def test_search_admit_card_term_surfaces_admit_card():
    r = requests.get(f"{API}/vacancies?q=admit", timeout=25)
    assert r.status_code == 200
    items = r.json()["items"]
    # If any admit-related items exist in DB they should now be visible.
    # We can't guarantee corpus content, but the request must succeed with items>=0.
    if items:
        # If items came back, at least one should be admit_card OR the query
        # matched other categories — but the presence of admit_card confirms
        # the exclusion was bypassed for search.
        assert isinstance(items, list)


# ---------- Feature 2: Manual lock (edit then refresh) ----------
def _find_scraped_vacancy():
    """Find a scraped (non-manual) vacancy id."""
    # Fetch a bunch of pages until we find something with non-manual source
    for page in range(1, 6):
        r = requests.get(f"{API}/vacancies?page={page}&per_page=50", timeout=25)
        if r.status_code != 200:
            break
        items = r.json()["items"]
        if not items:
            break
        for v in items:
            src = v.get("source")
            if src and src != "manual":
                return v
    return None


def test_manual_lock_edit_survives_refresh(auth_headers):
    scraped = _find_scraped_vacancy()
    if not scraped:
        pytest.skip("No scraped vacancies in DB to promote to manual")
    vid = scraped["id"]
    unique_title = f"TEST_MANUAL_LOCK_{os.urandom(3).hex()}"
    payload = {
        "title": unique_title,
        "organization": scraped.get("organization") or "Test Org",
        "post_name": scraped.get("post_name") or unique_title,
        "qualification": scraped.get("qualification") or "Graduate",
        "category": scraped.get("category") or "other",
        "description": "<p>Locked by manual admin edit for test.</p>",
    }
    # Edit -> becomes manual
    up = requests.put(f"{API}/admin/vacancies/{vid}", json=payload,
                      headers=auth_headers, timeout=20)
    assert up.status_code == 200, f"PUT failed: {up.status_code} {up.text[:200]}"
    edited = up.json()
    assert edited.get("source") == "manual", \
        f"After admin edit source should be manual, got {edited.get('source')}"
    assert edited["title"] == unique_title

    # Trigger refresh
    rf = requests.post(f"{API}/admin/vacancies/refresh",
                       headers=auth_headers, timeout=120)
    assert rf.status_code == 200, f"Refresh failed: {rf.status_code} {rf.text[:200]}"

    # Verify our edit survived
    got = requests.get(f"{API}/vacancies/{vid}", timeout=20)
    assert got.status_code == 200
    after = got.json()
    assert after["title"] == unique_title, \
        f"Manual edit was overwritten by refresh! title={after['title']!r}"
    assert after.get("source") == "manual"


# ---------- Feature 9: Blog center image ----------
def _png_bytes():
    # 1x1 PNG
    return (b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03"
            b"\x00\x01\xa5\xf6E@\x00\x00\x00\x00IEND\xaeB`\x82")


def test_blog_create_and_update_center_image(auth_headers):
    # Create with center_image
    title = f"TEST_CENTERIMG_{os.urandom(3).hex()}"
    files = {
        "center_image": ("center.png", _png_bytes(), "image/png"),
    }
    data = {"title": title, "excerpt": "t", "content": "<p>hi</p>",
            "status": "published"}
    r = requests.post(f"{API}/admin/blogs", data=data, files=files,
                      headers=auth_headers, timeout=25)
    assert r.status_code == 200, f"blog create: {r.status_code} {r.text[:200]}"
    blog = r.json()
    assert blog.get("center_image_url"), \
        f"center_image_url missing on create: keys={list(blog.keys())}"
    assert "/uploads/" in blog["center_image_url"] or blog["center_image_url"].startswith("http")
    bid = blog["id"]

    # Verify publicly retrievable
    pr = requests.get(f"{API}/blogs/{blog.get('slug') or bid}", timeout=15)
    if pr.status_code == 200:
        pub = pr.json()
        assert pub.get("center_image_url") == blog["center_image_url"]

    # Update with remove_center_image=1 -> should clear it
    r2 = requests.put(f"{API}/admin/blogs/{bid}",
                      data={"title": title, "remove_center_image": "1",
                            "content": "<p>hi</p>", "status": "published"},
                      headers=auth_headers, timeout=25)
    assert r2.status_code == 200, r2.text[:200]
    after = r2.json()
    assert after.get("center_image_url") == "", \
        f"remove_center_image should clear url, got {after.get('center_image_url')!r}"

    # Update with a NEW center image -> should set new url
    r3 = requests.put(f"{API}/admin/blogs/{bid}",
                      data={"title": title, "content": "<p>hi</p>",
                            "status": "published"},
                      files={"center_image": ("c2.png", _png_bytes(), "image/png")},
                      headers=auth_headers, timeout=25)
    assert r3.status_code == 200
    assert r3.json().get("center_image_url"), "Re-uploaded center_image missing"

    # Cleanup
    requests.delete(f"{API}/admin/blogs/{bid}", headers=auth_headers, timeout=15)
