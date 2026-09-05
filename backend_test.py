#!/usr/bin/env python3
"""Backend API tests for HR Digital Services app - Round 3: SEO edit, Full edit, Promo cleanup, Channel settings"""
import requests
import json
import time
from urllib.parse import quote

# Base URL from frontend env
BASE_URL = "https://copy-manager-5.preview.emergentagent.com/api"

# Admin credentials
ADMIN_EMAIL = "admin@hrdigitalservices.in"
ADMIN_PASSWORD = "Admin@12345"

# Test results
results = {
    "passed": [],
    "failed": [],
}

def log_pass(test_name, details=""):
    print(f"✅ PASS: {test_name}")
    if details:
        print(f"   {details}")
    results["passed"].append(test_name)

def log_fail(test_name, details=""):
    print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   {details}")
    results["failed"].append(test_name)

def admin_login():
    """Login as admin and return session"""
    session = requests.Session()
    resp = session.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        print(f"✓ Admin login successful")
        return session
    else:
        print(f"✗ Admin login failed: {resp.status_code} - {resp.text}")
        return None

def test_seo_edit_converts_to_manual():
    """Test 1: SEO edit converts a scraped API post → manual (protects from shuffle)"""
    print("\n" + "="*80)
    print("TEST 1: SEO EDIT CONVERTS SCRAPED POST TO MANUAL")
    print("="*80)
    
    admin_session = admin_login()
    if not admin_session:
        log_fail("SEO edit test", "Admin login failed")
        return
    
    # Step 1: GET /api/admin/vacancies-seo and find an item with source != "manual"
    print("\n--- Step 1: Finding a scraped vacancy ---")
    resp = admin_session.get(f"{BASE_URL}/admin/vacancies-seo?per_page=50")
    
    if resp.status_code != 200:
        log_fail("GET /api/admin/vacancies-seo", f"Status {resp.status_code}: {resp.text}")
        return
    
    data = resp.json()
    items = data.get("items", [])
    
    # Find a scraped vacancy (source != "manual")
    scraped_vacancy = None
    for item in items:
        if item.get("source") != "manual":
            scraped_vacancy = item
            break
    
    if not scraped_vacancy:
        log_fail("Find scraped vacancy", "No scraped vacancies found (all are manual)")
        return
    
    vacancy_id = scraped_vacancy.get("id")
    original_seo_title = scraped_vacancy.get("seo_title", "")
    original_source = scraped_vacancy.get("source", "")
    
    log_pass("Find scraped vacancy", 
            f"Found vacancy ID={vacancy_id}, source={original_source}, seo_title={original_seo_title[:50]}...")
    
    # Step 2: PUT /api/admin/vacancies/{id}/seo with custom SEO
    print("\n--- Step 2: Updating SEO (should convert to manual) ---")
    custom_seo_title = "MYCUSTOM SEO TITLE"
    custom_seo_desc = "my desc"
    
    seo_payload = {
        "seo_title": custom_seo_title,
        "seo_description": custom_seo_desc
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/vacancies/{vacancy_id}/seo", json=seo_payload)
    
    if resp.status_code != 200:
        log_fail("PUT /api/admin/vacancies/{id}/seo", f"Status {resp.status_code}: {resp.text}")
        return
    
    log_pass("PUT /api/admin/vacancies/{id}/seo", "SEO update successful")
    
    # Step 3: GET /api/vacancies/{id} and verify source is now "manual" and seo_title is custom
    print("\n--- Step 3: Verifying source changed to 'manual' and SEO persisted ---")
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
    
    if resp.status_code != 200:
        log_fail("GET /api/vacancies/{id} after SEO edit", f"Status {resp.status_code}: {resp.text}")
        return
    
    updated_vacancy = resp.json()
    new_source = updated_vacancy.get("source", "")
    new_seo_title = updated_vacancy.get("seo_title", "")
    
    if new_source == "manual":
        log_pass("Source converted to manual", f"source={new_source} (was {original_source})")
    else:
        log_fail("Source converted to manual", f"Expected 'manual', got '{new_source}'")
    
    if new_seo_title == custom_seo_title:
        log_pass("SEO title persisted", f"seo_title={new_seo_title}")
    else:
        log_fail("SEO title persisted", f"Expected '{custom_seo_title}', got '{new_seo_title}'")
    
    # Step 4: POST /api/admin/vacancies/shuffle-seo and verify this vacancy is NOT touched
    print("\n--- Step 4: Running shuffle-seo (should NOT touch manual posts) ---")
    resp = admin_session.post(f"{BASE_URL}/admin/vacancies/shuffle-seo")
    
    if resp.status_code != 200:
        log_fail("POST /api/admin/vacancies/shuffle-seo", f"Status {resp.status_code}: {resp.text}")
        return
    
    shuffle_data = resp.json()
    shuffled_count = shuffle_data.get("shuffled", 0)
    log_pass("POST /api/admin/vacancies/shuffle-seo", f"Shuffled {shuffled_count} vacancies")
    
    # Step 5: GET /api/vacancies/{id} again and verify seo_title is STILL the custom one
    print("\n--- Step 5: Verifying SEO title unchanged after shuffle ---")
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
    
    if resp.status_code != 200:
        log_fail("GET /api/vacancies/{id} after shuffle", f"Status {resp.status_code}: {resp.text}")
        return
    
    final_vacancy = resp.json()
    final_seo_title = final_vacancy.get("seo_title", "")
    
    if final_seo_title == custom_seo_title:
        log_pass("SEO title protected from shuffle", 
                f"seo_title still '{custom_seo_title}' (shuffle did not overwrite)")
    else:
        log_fail("SEO title protected from shuffle", 
                f"Expected '{custom_seo_title}', got '{final_seo_title}' (shuffle overwrote it!)")

def test_full_edit_converts_to_manual():
    """Test 2: Full edit converts a scraped API post → manual"""
    print("\n" + "="*80)
    print("TEST 2: FULL EDIT CONVERTS SCRAPED POST TO MANUAL")
    print("="*80)
    
    admin_session = admin_login()
    if not admin_session:
        log_fail("Full edit test", "Admin login failed")
        return
    
    # Step 1: GET /api/admin/vacancies-seo and find ANOTHER scraped vacancy
    print("\n--- Step 1: Finding another scraped vacancy ---")
    resp = admin_session.get(f"{BASE_URL}/admin/vacancies-seo?per_page=50")
    
    if resp.status_code != 200:
        log_fail("GET /api/admin/vacancies-seo", f"Status {resp.status_code}: {resp.text}")
        return
    
    data = resp.json()
    items = data.get("items", [])
    
    # Find a scraped vacancy (source != "manual"), skip the first one (used in test 1)
    scraped_vacancies = [item for item in items if item.get("source") != "manual"]
    
    if len(scraped_vacancies) < 2:
        log_fail("Find second scraped vacancy", "Not enough scraped vacancies (need at least 2)")
        # Use the first one if we only have one
        if scraped_vacancies:
            scraped_vacancy = scraped_vacancies[0]
        else:
            return
    else:
        scraped_vacancy = scraped_vacancies[1]  # Use second one
    
    vacancy_id = scraped_vacancy.get("id")
    original_source = scraped_vacancy.get("source", "")
    original_title = scraped_vacancy.get("title", "")
    
    log_pass("Find second scraped vacancy", 
            f"Found vacancy ID={vacancy_id}, source={original_source}, title={original_title[:50]}...")
    
    # Step 2: PUT /api/admin/vacancies/{id} with full edit
    print("\n--- Step 2: Full edit (should convert to manual) ---")
    
    edit_payload = {
        "title": "Edited Full Title",
        "organization": "My Org",
        "category": "other",
        "tags": ["tagx"],
        "important_links": [
            {
                "label": "Official",
                "url": "https://example.gov.in",
                "type": "link"
            }
        ]
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/vacancies/{vacancy_id}", json=edit_payload)
    
    if resp.status_code != 200:
        log_fail("PUT /api/admin/vacancies/{id}", f"Status {resp.status_code}: {resp.text}")
        return
    
    log_pass("PUT /api/admin/vacancies/{id}", "Full edit successful")
    
    # Step 3: GET /api/vacancies/{id} and verify changes
    print("\n--- Step 3: Verifying full edit persisted and source is 'manual' ---")
    resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
    
    if resp.status_code != 200:
        log_fail("GET /api/vacancies/{id} after full edit", f"Status {resp.status_code}: {resp.text}")
        return
    
    updated_vacancy = resp.json()
    new_source = updated_vacancy.get("source", "")
    new_title = updated_vacancy.get("title", "")
    new_tags = updated_vacancy.get("tags", [])
    new_links = updated_vacancy.get("important_links", [])
    
    # Verify source is manual
    if new_source == "manual":
        log_pass("Source converted to manual (full edit)", f"source={new_source} (was {original_source})")
    else:
        log_fail("Source converted to manual (full edit)", f"Expected 'manual', got '{new_source}'")
    
    # Verify title
    if new_title == "Edited Full Title":
        log_pass("Title updated", f"title={new_title}")
    else:
        log_fail("Title updated", f"Expected 'Edited Full Title', got '{new_title}'")
    
    # Verify tags
    if new_tags == ["tagx"]:
        log_pass("Tags updated", f"tags={new_tags}")
    else:
        log_fail("Tags updated", f"Expected ['tagx'], got {new_tags}")
    
    # Verify important_links
    if len(new_links) >= 1:
        official_link = None
        for link in new_links:
            if link.get("label") == "Official":
                official_link = link
                break
        
        if official_link:
            if (official_link.get("url") == "https://example.gov.in" and 
                official_link.get("type") == "link"):
                log_pass("Important links updated", f"Official link present: {official_link}")
            else:
                log_fail("Important links updated", f"Official link mismatch: {official_link}")
        else:
            log_fail("Important links updated", "Official link not found in important_links")
    else:
        log_fail("Important links updated", f"Expected at least 1 link, got {len(new_links)}")

def test_promo_cleanup():
    """Test 3: Promo cleanup endpoint"""
    print("\n" + "="*80)
    print("TEST 3: PROMO CLEANUP ENDPOINT")
    print("="*80)
    
    # Test 3.1: Without admin auth - should get 401/403
    print("\n--- Step 1: Testing without auth (should fail) ---")
    resp = requests.post(f"{BASE_URL}/admin/vacancies/clean-promo")
    
    if resp.status_code in [401, 403]:
        log_pass("POST /api/admin/vacancies/clean-promo (no auth)", 
                f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("POST /api/admin/vacancies/clean-promo (no auth)", 
                f"Expected 401/403, got {resp.status_code}")
    
    # Test 3.2: With admin auth - should return {ok: true, cleaned: <int>}
    print("\n--- Step 2: Testing with admin auth ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Promo cleanup test", "Admin login failed")
        return
    
    resp = admin_session.post(f"{BASE_URL}/admin/vacancies/clean-promo")
    
    if resp.status_code != 200:
        log_fail("POST /api/admin/vacancies/clean-promo (with auth)", 
                f"Status {resp.status_code}: {resp.text}")
        return
    
    data = resp.json()
    
    # Verify response structure
    if "ok" not in data:
        log_fail("Promo cleanup response", "Missing 'ok' field")
        return
    
    if "cleaned" not in data:
        log_fail("Promo cleanup response", "Missing 'cleaned' field")
        return
    
    if not isinstance(data["cleaned"], int):
        log_fail("Promo cleanup response", f"'cleaned' should be int, got {type(data['cleaned'])}")
        return
    
    log_pass("POST /api/admin/vacancies/clean-promo (with auth)", 
            f"Success: ok={data['ok']}, cleaned={data['cleaned']}")

def test_channel_link_settings():
    """Test 4: Channel link settings"""
    print("\n" + "="*80)
    print("TEST 4: CHANNEL LINK SETTINGS")
    print("="*80)
    
    # Test 4.1: PUT without admin auth - should get 401/403
    print("\n--- Step 1: Testing PUT without auth (should fail) ---")
    settings_payload = {
        "channel_whatsapp": "https://whatsapp.com/channel/test",
        "channel_telegram": "https://t.me/test"
    }
    
    resp = requests.put(f"{BASE_URL}/admin/site-settings", json=settings_payload)
    
    if resp.status_code in [401, 403]:
        log_pass("PUT /api/admin/site-settings (no auth)", 
                f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("PUT /api/admin/site-settings (no auth)", 
                f"Expected 401/403, got {resp.status_code}")
    
    # Test 4.2: PUT with admin auth
    print("\n--- Step 2: Testing PUT with admin auth ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Channel settings test", "Admin login failed")
        return
    
    test_whatsapp = "https://whatsapp.com/channel/abc"
    test_telegram = "https://t.me/mychan"
    
    settings_payload = {
        "channel_whatsapp": test_whatsapp,
        "channel_telegram": test_telegram
    }
    
    resp = admin_session.put(f"{BASE_URL}/admin/site-settings", json=settings_payload)
    
    if resp.status_code != 200:
        log_fail("PUT /api/admin/site-settings (with auth)", 
                f"Status {resp.status_code}: {resp.text}")
        return
    
    log_pass("PUT /api/admin/site-settings (with auth)", "Settings updated successfully")
    
    # Test 4.3: GET /api/site-settings and verify
    print("\n--- Step 3: Testing GET /api/site-settings (public) ---")
    resp = requests.get(f"{BASE_URL}/site-settings")
    
    if resp.status_code != 200:
        log_fail("GET /api/site-settings", f"Status {resp.status_code}: {resp.text}")
        return
    
    data = resp.json()
    
    # Verify required keys are present
    required_keys = [
        "channel_whatsapp", "channel_telegram", "channel_arattai",
        "channel_youtube", "channel_instagram", "channel_app"
    ]
    
    missing_keys = [k for k in required_keys if k not in data]
    
    if missing_keys:
        log_fail("GET /api/site-settings (keys)", f"Missing keys: {missing_keys}")
    else:
        log_pass("GET /api/site-settings (keys)", 
                f"All required keys present: {required_keys}")
    
    # Verify the values we just set
    returned_whatsapp = data.get("channel_whatsapp", "")
    returned_telegram = data.get("channel_telegram", "")
    
    if returned_whatsapp == test_whatsapp:
        log_pass("GET /api/site-settings (channel_whatsapp)", 
                f"channel_whatsapp={returned_whatsapp}")
    else:
        log_fail("GET /api/site-settings (channel_whatsapp)", 
                f"Expected '{test_whatsapp}', got '{returned_whatsapp}'")
    
    if returned_telegram == test_telegram:
        log_pass("GET /api/site-settings (channel_telegram)", 
                f"channel_telegram={returned_telegram}")
    else:
        log_fail("GET /api/site-settings (channel_telegram)", 
                f"Expected '{test_telegram}', got '{returned_telegram}'")

def main():
    print("="*80)
    print("HR DIGITAL SERVICES - BACKEND API TESTS (ROUND 3)")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*80)
    
    # Run all tests
    test_seo_edit_converts_to_manual()
    test_full_edit_converts_to_manual()
    test_promo_cleanup()
    test_channel_link_settings()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ PASSED: {len(results['passed'])}")
    print(f"❌ FAILED: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed tests:")
        for test in results['failed']:
            print(f"  - {test}")
    
    print("="*80)
    
    return 0 if not results['failed'] else 1

if __name__ == "__main__":
    exit(main())
