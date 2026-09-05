#!/usr/bin/env python3
"""Backend API tests for HR Digital Services - Round 2: Admin Overview, Uploads, Manual Vacancy Tags & Important Links"""
import requests
import json
import io
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

def test_admin_overview():
    """Test 1: Admin Overview endpoint"""
    print("\n" + "="*80)
    print("TEST 1: ADMIN OVERVIEW")
    print("="*80)
    
    # Test 1.1: Without auth - should get 401/403
    print("\n--- Testing GET /api/admin/overview WITHOUT auth ---")
    resp = requests.get(f"{BASE_URL}/admin/overview")
    if resp.status_code in [401, 403]:
        log_pass("Admin overview without auth", f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("Admin overview without auth", f"Expected 401/403, got {resp.status_code}")
    
    # Test 1.2: With admin auth - should get 200 with stats
    print("\n--- Testing GET /api/admin/overview WITH admin auth ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Admin overview with auth", "Admin login failed")
        return
    
    resp = admin_session.get(f"{BASE_URL}/admin/overview")
    if resp.status_code == 200:
        data = resp.json()
        
        # Check required keys
        required_keys = [
            "total_vacancies", "total_views", "total_blogs", "total_reviews",
            "manual_vacancies", "vacancy_views", "blog_views", "contacts"
        ]
        
        missing_keys = [k for k in required_keys if k not in data]
        if missing_keys:
            log_fail("Admin overview with auth", f"Missing keys: {missing_keys}")
        else:
            # Check all values are integers
            non_int_keys = [k for k in required_keys if not isinstance(data[k], int)]
            if non_int_keys:
                log_fail("Admin overview with auth", f"Non-integer values for: {non_int_keys}")
            else:
                # Check total_vacancies > 0
                if data["total_vacancies"] > 0:
                    log_pass("Admin overview with auth", 
                            f"All keys present with integer values. total_vacancies={data['total_vacancies']}, "
                            f"manual_vacancies={data['manual_vacancies']}, total_blogs={data['total_blogs']}, "
                            f"total_reviews={data['total_reviews']}, total_views={data['total_views']}")
                else:
                    log_fail("Admin overview with auth", 
                            f"total_vacancies is {data['total_vacancies']}, expected > 0")
    else:
        log_fail("Admin overview with auth", f"Status {resp.status_code}: {resp.text}")

def test_admin_upload():
    """Test 2: Admin Upload endpoint"""
    print("\n" + "="*80)
    print("TEST 2: ADMIN UPLOAD")
    print("="*80)
    
    # Test 2.1: Without auth - should get 401/403
    print("\n--- Testing POST /api/admin/uploads WITHOUT auth ---")
    
    # Create a small PDF file
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test PDF) Tj\nET\nendstream\nendobj\nxref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000317 00000 n\ntrailer\n<< /Size 5 /Root 1 0 R >>\nstartxref\n410\n%%EOF"
    
    files = {'file': ('test.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    resp = requests.post(f"{BASE_URL}/admin/uploads", files=files)
    if resp.status_code in [401, 403]:
        log_pass("Admin upload without auth", f"Correctly rejected with {resp.status_code}")
    else:
        log_fail("Admin upload without auth", f"Expected 401/403, got {resp.status_code}")
    
    # Test 2.2: With admin auth - should upload successfully
    print("\n--- Testing POST /api/admin/uploads WITH admin auth ---")
    admin_session = admin_login()
    if not admin_session:
        log_fail("Admin upload with auth", "Admin login failed")
        return
    
    files = {'file': ('test_upload.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    resp = admin_session.post(f"{BASE_URL}/admin/uploads", files=files)
    
    if resp.status_code == 200:
        data = resp.json()
        
        # Check required keys
        required_keys = ["url", "name", "size", "mime"]
        missing_keys = [k for k in required_keys if k not in data]
        
        if missing_keys:
            log_fail("Admin upload with auth", f"Missing keys: {missing_keys}")
        else:
            # Check mime type
            if data["mime"] == "application/pdf":
                log_pass("Admin upload with auth", 
                        f"Upload successful. url={data['url']}, name={data['name']}, "
                        f"size={data['size']}, mime={data['mime']}")
                
                # Test 2.3: GET the uploaded file
                print("\n--- Testing GET uploaded file ---")
                upload_url = data["url"]
                
                # The URL should be like /api/uploads/{fname}
                if upload_url.startswith("/api/uploads/"):
                    full_url = f"{BASE_URL.replace('/api', '')}{upload_url}"
                    resp_get = requests.get(full_url)
                    
                    if resp_get.status_code == 200:
                        # Check content type
                        content_type = resp_get.headers.get("Content-Type", "")
                        if "application/pdf" in content_type or "pdf" in content_type.lower():
                            log_pass("GET uploaded file", 
                                    f"File retrieved successfully. Content-Type: {content_type}, "
                                    f"Size: {len(resp_get.content)} bytes")
                        else:
                            log_fail("GET uploaded file", 
                                    f"Unexpected Content-Type: {content_type}")
                    else:
                        log_fail("GET uploaded file", f"Status {resp_get.status_code}")
                else:
                    log_fail("GET uploaded file", f"Invalid URL format: {upload_url}")
            else:
                log_fail("Admin upload with auth", 
                        f"Expected mime='application/pdf', got '{data['mime']}'")
    else:
        log_fail("Admin upload with auth", f"Status {resp.status_code}: {resp.text}")

def test_manual_vacancy_tags_links():
    """Test 3: Manual Vacancy tags and important_links"""
    print("\n" + "="*80)
    print("TEST 3: MANUAL VACANCY TAGS & IMPORTANT_LINKS")
    print("="*80)
    
    admin_session = admin_login()
    if not admin_session:
        log_fail("Manual vacancy tags/links", "Admin login failed")
        return
    
    # Test 3.1: POST manual vacancy with tags and important_links
    print("\n--- Testing POST /api/admin/vacancies with tags & important_links ---")
    
    vacancy_payload = {
        "title": "Test Manual GDS Post",
        "organization": "India Post",
        "category": "other",
        "tags": ["10th pass", "latest"],
        "important_links": [
            {
                "label": "Notification PDF",
                "url": "https://example.com/notif.pdf",
                "type": "pdf"
            },
            {
                "label": "Apply Online",
                "url": "https://example.com/apply",
                "type": "link"
            }
        ]
    }
    
    resp = admin_session.post(f"{BASE_URL}/admin/vacancies", json=vacancy_payload)
    
    if resp.status_code == 200:
        created_vacancy = resp.json()
        vacancy_id = created_vacancy.get("id")
        
        if not vacancy_id:
            log_fail("POST manual vacancy", "No id in response")
            return
        
        log_pass("POST manual vacancy", f"Created vacancy ID: {vacancy_id}")
        
        # Test 3.2: GET the vacancy and verify tags and important_links
        print("\n--- Testing GET /api/vacancies/{id} - verify tags & important_links ---")
        resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Check tags
            returned_tags = data.get("tags", [])
            expected_tags = ["10th pass", "latest"]
            
            if returned_tags == expected_tags:
                log_pass("GET vacancy - tags", f"Tags match: {returned_tags}")
            else:
                log_fail("GET vacancy - tags", 
                        f"Expected {expected_tags}, got {returned_tags}")
            
            # Check important_links
            returned_links = data.get("important_links", [])
            
            if len(returned_links) == 2:
                # Check first link
                link1 = returned_links[0]
                if (link1.get("label") == "Notification PDF" and 
                    link1.get("url") == "https://example.com/notif.pdf" and 
                    link1.get("type") == "pdf"):
                    log_pass("GET vacancy - important_links[0]", 
                            f"First link correct: {link1}")
                else:
                    log_fail("GET vacancy - important_links[0]", 
                            f"Link mismatch: {link1}")
                
                # Check second link
                link2 = returned_links[1]
                if (link2.get("label") == "Apply Online" and 
                    link2.get("url") == "https://example.com/apply" and 
                    link2.get("type") == "link"):
                    log_pass("GET vacancy - important_links[1]", 
                            f"Second link correct: {link2}")
                else:
                    log_fail("GET vacancy - important_links[1]", 
                            f"Link mismatch: {link2}")
            else:
                log_fail("GET vacancy - important_links", 
                        f"Expected 2 links, got {len(returned_links)}")
        else:
            log_fail("GET vacancy", f"Status {resp.status_code}: {resp.text}")
        
        # Test 3.3: PUT update tags and important_links
        print("\n--- Testing PUT /api/admin/vacancies/{id} - update tags & important_links ---")
        
        update_payload = {
            "title": "Test Manual GDS Post",
            "organization": "India Post",
            "category": "other",
            "tags": ["updated"],
            "important_links": [
                {
                    "label": "Result",
                    "url": "https://example.com/result",
                    "type": "link"
                }
            ]
        }
        
        resp = admin_session.put(f"{BASE_URL}/admin/vacancies/{vacancy_id}", json=update_payload)
        
        if resp.status_code == 200:
            log_pass("PUT manual vacancy", "Update successful")
            
            # Test 3.4: GET again to verify update persisted
            print("\n--- Testing GET /api/vacancies/{id} - verify update persisted ---")
            resp = requests.get(f"{BASE_URL}/vacancies/{vacancy_id}")
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Check updated tags
                returned_tags = data.get("tags", [])
                expected_tags = ["updated"]
                
                if returned_tags == expected_tags:
                    log_pass("GET vacancy after update - tags", f"Tags updated: {returned_tags}")
                else:
                    log_fail("GET vacancy after update - tags", 
                            f"Expected {expected_tags}, got {returned_tags}")
                
                # Check updated important_links
                returned_links = data.get("important_links", [])
                
                if len(returned_links) == 1:
                    link = returned_links[0]
                    if (link.get("label") == "Result" and 
                        link.get("url") == "https://example.com/result" and 
                        link.get("type") == "link"):
                        log_pass("GET vacancy after update - important_links", 
                                f"Links updated correctly: {link}")
                    else:
                        log_fail("GET vacancy after update - important_links", 
                                f"Link mismatch: {link}")
                else:
                    log_fail("GET vacancy after update - important_links", 
                            f"Expected 1 link, got {len(returned_links)}")
            else:
                log_fail("GET vacancy after update", f"Status {resp.status_code}: {resp.text}")
        else:
            log_fail("PUT manual vacancy", f"Status {resp.status_code}: {resp.text}")
        
        # Test 3.5: Cleanup - DELETE the test vacancy
        print("\n--- Testing DELETE /api/admin/vacancies/{id} - cleanup ---")
        resp = admin_session.delete(f"{BASE_URL}/admin/vacancies/{vacancy_id}")
        
        if resp.status_code == 200:
            log_pass("DELETE manual vacancy", "Cleanup successful")
        else:
            log_fail("DELETE manual vacancy", f"Status {resp.status_code}: {resp.text}")
    else:
        log_fail("POST manual vacancy", f"Status {resp.status_code}: {resp.text}")

def main():
    print("="*80)
    print("HR DIGITAL SERVICES - BACKEND API TESTS (ROUND 2)")
    print("="*80)
    print(f"Base URL: {BASE_URL}")
    print(f"Admin: {ADMIN_EMAIL}")
    print("="*80)
    
    # Run all tests
    test_admin_overview()
    test_admin_upload()
    test_manual_vacancy_tags_links()
    
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
