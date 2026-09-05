#!/usr/bin/env python3
"""
Backend API test for HR Digital Services - Bug Fix Verification
Tests the fix for ManualVacancyIn.description max_length (20000 -> 200000)
"""
import os
import sys
import requests
from pathlib import Path

# Read backend URL from frontend/.env
env_path = Path("/app/frontend/.env")
BACKEND_URL = None
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if line.startswith("REACT_APP_BACKEND_URL="):
            BACKEND_URL = line.split("=", 1)[1].strip()
            break

if not BACKEND_URL:
    print("❌ ERROR: Could not read REACT_APP_BACKEND_URL from /app/frontend/.env")
    sys.exit(1)

BASE_URL = f"{BACKEND_URL}/api"
print(f"🔗 Testing backend at: {BASE_URL}\n")

# Admin credentials from review request
ADMIN_EMAIL = "hrdigitalservices.in@gmail.com"
ADMIN_PASSWORD = "Dev@3642"

# Test results tracking
tests_passed = 0
tests_failed = 0
test_details = []

def log_test(name, passed, details=""):
    global tests_passed, tests_failed
    if passed:
        tests_passed += 1
        status = "✅ PASS"
    else:
        tests_failed += 1
        status = "❌ FAIL"
    msg = f"{status}: {name}"
    if details:
        msg += f" - {details}"
    print(msg)
    test_details.append({"name": name, "passed": passed, "details": details})

def test_admin_login():
    """Test 1: Admin login with provided credentials"""
    print("\n" + "="*80)
    print("TEST 1: Admin Login")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Check if we got a token or success indicator
            has_token = "access_token" in data or "token" in data
            has_cookies = bool(response.cookies)
            
            if has_token or has_cookies:
                log_test("Admin login", True, f"Status 200, auth mechanism present")
                return response.cookies
            else:
                log_test("Admin login", False, f"Status 200 but no token/cookies in response")
                return None
        else:
            log_test("Admin login", False, f"Status {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        log_test("Admin login", False, f"Exception: {str(e)}")
        return None

def test_list_scraped_vacancies(cookies):
    """Test 2: List scraped/API vacancies and pick one"""
    print("\n" + "="*80)
    print("TEST 2: List Scraped Vacancies")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/admin/vacancies-seo?page=1&per_page=20",
            cookies=cookies,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            items = data.get("items", [])
            
            if not items:
                log_test("List scraped vacancies", False, "No vacancies returned")
                return None
            
            # Find a scraped vacancy (source != "manual")
            scraped = None
            for item in items:
                if item.get("source") != "manual":
                    scraped = item
                    break
            
            if scraped:
                log_test("List scraped vacancies", True, 
                        f"Found {len(items)} vacancies, picked scraped ID: {scraped['id']}, source: {scraped.get('source')}")
                return scraped
            else:
                log_test("List scraped vacancies", False, "No scraped vacancies found (all are manual)")
                return None
        else:
            log_test("List scraped vacancies", False, f"Status {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        log_test("List scraped vacancies", False, f"Exception: {str(e)}")
        return None

def test_get_vacancy_detail(vacancy_id):
    """Test 2b: Get full vacancy details"""
    print("\n" + "="*80)
    print("TEST 2b: Get Vacancy Detail")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/vacancies/{vacancy_id}",
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Get vacancy detail", True, 
                    f"Retrieved vacancy: {data.get('title', '')[:50]}...")
            return data
        else:
            log_test("Get vacancy detail", False, f"Status {response.status_code}: {response.text[:200]}")
            return None
            
    except Exception as e:
        log_test("Get vacancy detail", False, f"Exception: {str(e)}")
        return None

def test_edit_with_long_description(vacancy_id, vacancy_data, cookies):
    """Test 3: THE KEY TEST - Edit vacancy with LONG description (~30000 chars)"""
    print("\n" + "="*80)
    print("TEST 3: Edit Vacancy with LONG Description (~30000 chars)")
    print("="*80)
    print("This is the KEY BUG FIX TEST - should now succeed (200), not 422")
    
    # Create a long description (~30000 characters)
    long_description = "<h2>Detailed Job Description</h2>\n"
    long_description += "<p>This is a comprehensive job posting with extensive details about the position, requirements, and application process.</p>\n"
    
    # Add repetitive content to reach ~30000 chars
    section_template = """
    <h3>Section {num}: Important Information</h3>
    <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. 
    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
    <ul>
        <li>Qualification requirement {num}.1: Graduate degree in relevant field</li>
        <li>Qualification requirement {num}.2: Minimum 2 years of experience</li>
        <li>Qualification requirement {num}.3: Age limit between 18-35 years</li>
        <li>Qualification requirement {num}.4: Valid government ID proof required</li>
        <li>Qualification requirement {num}.5: Computer literacy certificate mandatory</li>
    </ul>
    <p>Additional details about the application process, selection criteria, and important dates. 
    Candidates must ensure they meet all eligibility criteria before applying. 
    The selection process will include written examination, skill test, and personal interview rounds.</p>
    """
    
    for i in range(1, 51):  # 50 sections to reach ~30000 chars
        long_description += section_template.format(num=i)
    
    print(f"Generated description length: {len(long_description)} characters")
    
    # Prepare the payload - use existing vacancy data as base
    payload = {
        "title": vacancy_data.get("title", "Test Vacancy Title"),
        "organization": vacancy_data.get("organization", "Test Organization"),
        "category": vacancy_data.get("category", "other"),
        "description": long_description  # THE KEY FIELD - long description
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/vacancies/{vacancy_id}",
            json=payload,
            cookies=cookies,
            timeout=60  # Longer timeout for large payload
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            log_test("Edit with long description", True, 
                    f"✅ SUCCESS! Status 200 - Long description accepted (bug fix working)")
            return True
        elif response.status_code == 422:
            error_detail = response.json().get("detail", "")
            log_test("Edit with long description", False, 
                    f"❌ BUG NOT FIXED! Status 422 (validation error): {error_detail}")
            return False
        else:
            log_test("Edit with long description", False, 
                    f"Status {response.status_code}: {response.text[:500]}")
            return False
            
    except Exception as e:
        log_test("Edit with long description", False, f"Exception: {str(e)}")
        return False

def test_verify_saved_description(vacancy_id, cookies):
    """Test 3b: Verify the long description was saved"""
    print("\n" + "="*80)
    print("TEST 3b: Verify Saved Description")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/vacancies/{vacancy_id}",
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            # Check content_html field (where full description is stored)
            content_html = data.get("content_html", "")
            structured_desc = data.get("structured", {}).get("description", "")
            
            # Either field should have the long description
            desc_length = max(len(content_html), len(structured_desc))
            
            print(f"content_html length: {len(content_html)} chars")
            print(f"structured.description length: {len(structured_desc)} chars")
            
            if desc_length > 20000:
                log_test("Verify saved description", True, 
                        f"Description saved correctly, length: {desc_length} chars (in content_html/structured.description)")
                return True
            else:
                log_test("Verify saved description", False, 
                        f"Description too short: {desc_length} chars (expected >20000)")
                return False
        else:
            log_test("Verify saved description", False, f"Status {response.status_code}")
            return False
            
    except Exception as e:
        log_test("Verify saved description", False, f"Exception: {str(e)}")
        return False

def test_validation_still_works(vacancy_id, cookies):
    """Test 4: Validation error check - send invalid payload"""
    print("\n" + "="*80)
    print("TEST 4: Validation Still Works (Invalid Payload)")
    print("="*80)
    print("Testing that validation errors are still properly returned")
    
    # Send invalid payload: title="" violates min_length=3
    invalid_payload = {
        "title": "",  # Invalid: min_length=3
        "organization": "Test Org",
        "category": "other"
    }
    
    try:
        response = requests.put(
            f"{BASE_URL}/admin/vacancies/{vacancy_id}",
            json=invalid_payload,
            cookies=cookies,
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 422:
            data = response.json()
            has_detail = "detail" in data
            
            if has_detail:
                detail = data["detail"]
                is_array = isinstance(detail, list)
                log_test("Validation error check", True, 
                        f"Status 422 with detail field (array: {is_array})")
                return True
            else:
                log_test("Validation error check", False, 
                        f"Status 422 but no 'detail' field in response")
                return False
        else:
            log_test("Validation error check", False, 
                    f"Expected 422, got {response.status_code}: {response.text[:200]}")
            return False
            
    except Exception as e:
        log_test("Validation error check", False, f"Exception: {str(e)}")
        return False

def main():
    print("="*80)
    print("HR DIGITAL SERVICES - BUG FIX VERIFICATION TEST")
    print("Bug: ManualVacancyIn.description max_length 20000 -> 200000")
    print("="*80)
    
    # Test 1: Admin login
    cookies = test_admin_login()
    if not cookies:
        print("\n❌ CRITICAL: Admin login failed. Cannot proceed with other tests.")
        return
    
    # Test 2: List scraped vacancies
    scraped_vacancy = test_list_scraped_vacancies(cookies)
    if not scraped_vacancy:
        print("\n❌ CRITICAL: Could not find scraped vacancy. Cannot proceed with edit tests.")
        return
    
    vacancy_id = scraped_vacancy["id"]
    
    # Test 2b: Get full vacancy details
    vacancy_data = test_get_vacancy_detail(vacancy_id)
    if not vacancy_data:
        print("\n⚠️  WARNING: Could not get vacancy details. Using scraped data for edit test.")
        vacancy_data = scraped_vacancy
    
    # Test 3: THE KEY TEST - Edit with long description
    edit_success = test_edit_with_long_description(vacancy_id, vacancy_data, cookies)
    
    if edit_success:
        # Test 3b: Verify saved description
        test_verify_saved_description(vacancy_id, cookies)
    
    # Test 4: Validation still works
    test_validation_still_works(vacancy_id, cookies)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Total:  {tests_passed + tests_failed}")
    print("="*80)
    
    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED! Bug fix verified successfully.")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Review details above.")
    
    print("\nDetailed Results:")
    for i, test in enumerate(test_details, 1):
        status = "✅" if test["passed"] else "❌"
        print(f"{i}. {status} {test['name']}")
        if test["details"]:
            print(f"   {test['details']}")

if __name__ == "__main__":
    main()
