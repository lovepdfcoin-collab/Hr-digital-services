#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Add to the HR Digital Services app (blogs + vacancies):
  1) Per-post Verification code / custom <head> meta tag option (blogs + vacancies).
  2) Public reviews (star rating + comment) on posts; reviews show immediately; admin can hide/delete.
  3) View counter per post (blogs + vacancies) shown on the public page and in admin.
  4) Fix the Vacancies search bar — searching "gds", "india post" or "gramin dak" did not surface the
     "India Post — Gramin Dak Sevak – 23757 Posts" vacancy. Root cause: q was never sent to the server
     (client-side filtered only the 20 loaded rows). Added debounced server-side search + acronym synonyms.

backend:
  - task: "Vacancy search server-side + acronym synonyms (gds→gramin dak sevak)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "GET /api/vacancies?q=... — added SEARCH_SYNONYMS expansion so 'gds' matches 'Gramin Dak Sevak'. Verify q=gds, q=india post, q=gramin dak all return the India Post GDS vacancy."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: All 3 search queries (gds, india post, gramin dak) successfully return the 'India Post — Gramin Dak Sevak – 23757 Posts' vacancy. Synonym expansion working correctly. Response includes proper pagination (items, total, page, pages)."
  - task: "View counter increment on blog + vacancy detail GET"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "GET /api/blogs/{slug} and GET /api/vacancies/{id} now $inc views and return views. Verify views increments on repeated GETs."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: Both blog and vacancy view counters increment correctly. Blog views: 4→5, Vacancy views: 8→9. Views field is returned in response and persists across requests."
  - task: "Reviews CRUD (public post/list, admin list/toggle/delete)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "POST /api/reviews (public), GET /api/reviews?target_type=&target_id=, GET /api/admin/reviews, PUT /api/admin/reviews/{id}/toggle, DELETE /api/admin/reviews/{id}. Admin endpoints require admin auth. Verify average/count, hidden filtering, and admin moderation."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: All review endpoints working correctly. POST creates reviews for both blog and vacancy. GET returns {items, count, average} with correct calculations. Invalid target_type correctly rejected with 400. Admin endpoints: GET returns reviews with target_title, toggle hides/unhides reviews (hidden reviews excluded from public GET), DELETE removes reviews. Auth correctly enforced (401/403 without credentials)."
  - task: "Custom head / verification meta per post (blogs via form, vacancies via /seo)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Blog create/update accept custom_head form field; PUT /api/admin/vacancies/{id}/seo accepts custom_head. Verify persisted + returned in GET."
        -working: true
        -agent: "testing"
        -comment: "✅ VERIFIED: Custom head functionality working for both blogs and vacancies. Blog: PUT /api/admin/blogs/{id} with custom_head form field persists and returns in GET /api/blogs/{slug}. Vacancy: PUT /api/admin/vacancies/{id}/seo with custom_head JSON field persists and returns in GET /api/vacancies/{id}. Tested with Google site verification meta tag."

frontend:
  - task: "Vacancies search box triggers debounced server search"
    implemented: true
    working: "NA"
    file: "frontend/src/pages/Vacancies.jsx"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Needs user permission before automated frontend testing."
  - task: "Reviews UI + views on BlogDetail/VacancyDetail; admin Reviews page; custom_head admin fields"
    implemented: true
    working: "NA"
    file: "frontend/src/components/Reviews.jsx"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "Needs user permission before automated frontend testing."

  - task: "Admin overview stats + admin upload (PDF) + manual vacancy tags & important_links"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW round 2: GET /api/admin/overview (counts+view sums). POST /api/admin/uploads (admin, PDF/image -> returns url). ManualVacancyIn now accepts tags[] and important_links[{label,url,type}]; POST/PUT /api/admin/vacancies persist & GET /api/vacancies/{id} returns them."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 13 TESTS PASSED. (1) Admin Overview: GET /api/admin/overview without auth→401✅, with auth→200 with all required keys (total_vacancies=973, manual_vacancies=0, total_blogs=1, total_reviews=3, total_views=26)✅. (2) Admin Upload: POST /api/admin/uploads without auth→401✅, with auth→200 {url,name,size,mime=application/pdf}✅, GET uploaded file→200 with correct Content-Type✅. (3) Manual Vacancy tags & important_links: POST with tags=['10th pass','latest'] and important_links[{pdf},{link}]→200✅, GET returns correct tags✅ and both important_links✅, PUT update tags=['updated'] and important_links[{result}]→200✅, GET confirms update persisted✅, DELETE cleanup→200✅. Object storage working correctly."
        -working: true
        -agent: "testing"
        -comment: "✅ ROUND 3 RE-VERIFICATION: ALL 13 TESTS PASSED (13/13). Comprehensive re-testing completed successfully. (1) Admin Overview: No auth→401✅, With auth→200 with all 8 required keys (total_vacancies, total_views, total_blogs, total_reviews, manual_vacancies, vacancy_views, blog_views, contacts) all numeric✅. (2) Admin Upload: No auth→401✅, With auth→200 {url=/api/uploads/f700147d78e64048a2e6c66407d0557d.pdf, name=test_upload.pdf, size=312, mime=application/pdf}✅, GET uploaded file→200 with Content-Type: application/pdf✅. (3) Manual Vacancy tags & important_links: POST with tags=['10th pass','haryana','latest'] and 2 important_links→200 with ID=6a9ad96ccf0bd9746fdcef44✅, GET returns exact tags✅ and both links preserved (label/url/type)✅, PUT update to tags=['updated'] and 1 link→200✅, GET confirms update persisted correctly✅, DELETE cleanup→200✅. All endpoints working correctly with proper auth enforcement, data validation, and persistence."

  - task: "Search analytics logging and admin endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW search analytics feature: GET /api/vacancies?q=... silently logs searches to search_logs collection (q, q_lower, results, at). GET /api/admin/search-analytics (admin) returns {days, total_searches, unique_terms, top[], zero_results[]} with aggregated search data. Top searches sorted by count descending. Supports days query param."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 14 TESTS PASSED (14/14). (1) Search Logging: GET /api/vacancies?q=police (3 times) returned 4 results each, logged silently✅. GET /api/vacancies?q=zzqqxx-nomatch returned 0 results, logged silently✅. (2) Admin Search Analytics: No auth→401✅. With admin auth→200 with all required keys (days=30, total_searches=19, unique_terms=12)✅. All data types correct (days/total_searches/unique_terms are int, top/zero_results are arrays)✅. (3) Top Searches: 'police' found in top with count=5 (>=2), avg_results=4✅. Top array has correct structure (query, count, avg_results, last_at)✅. Top array correctly sorted by count descending [5,3,2,1,1...]✅. (4) Zero Results: 'zzqqxx-nomatch' found in zero_results with avg_results=0✅. (5) Days Parameter: GET /api/admin/search-analytics?days=7 returns days=7✅. All endpoints working correctly with proper auth enforcement, silent logging, and accurate analytics aggregation."

  - task: "SEO edit converts scraped API post to manual (protects from shuffle)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW round-3 feature: PUT /api/admin/vacancies/{id}/seo now converts scraped (API) posts to source='manual' so they are protected from future shuffle-seo operations. POST /api/admin/vacancies/shuffle-seo only touches vacancies with source != 'manual'."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 6 TESTS PASSED (6/6). (1) Found scraped vacancy with source=freejobalert✅. (2) PUT /api/admin/vacancies/{id}/seo with custom seo_title='MYCUSTOM SEO TITLE' → 200✅. (3) GET /api/vacancies/{id} → source changed to 'manual' (was freejobalert)✅, seo_title='MYCUSTOM SEO TITLE' persisted✅. (4) POST /api/admin/vacancies/shuffle-seo → 200, shuffled 972 vacancies✅. (5) GET /api/vacancies/{id} again → seo_title STILL 'MYCUSTOM SEO TITLE' (shuffle did NOT overwrite manual post)✅. SEO edit protection working correctly."

  - task: "Full edit converts scraped API post to manual"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW round-3 feature: PUT /api/admin/vacancies/{id} now works for both manual and scraped posts. Editing a scraped post converts it to source='manual' so it ranks better and is never touched by auto-refresh or shuffle-seo again."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 5 TESTS PASSED (5/5). (1) Found scraped vacancy with source=freejobalert✅. (2) PUT /api/admin/vacancies/{id} with title='Edited Full Title', tags=['tagx'], important_links=[{Official link}] → 200✅. (3) GET /api/vacancies/{id} → source changed to 'manual' (was freejobalert)✅, title='Edited Full Title'✅, tags=['tagx']✅, important_links contains Official link with correct label/url/type✅. Full edit conversion working correctly."

  - task: "Promo cleanup endpoint"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW round-3 feature: POST /api/admin/vacancies/clean-promo (admin only) strips FreeJobAlert promo links/blocks from scraped vacancy content and important_links. Returns {ok: true, cleaned: <int>}."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 2 TESTS PASSED (2/2). (1) POST /api/admin/vacancies/clean-promo without auth → 401✅. (2) POST /api/admin/vacancies/clean-promo with admin auth → 200 with {ok: true, cleaned: 2}✅. Auth enforcement and response structure correct."

  - task: "Channel link settings (WhatsApp, Telegram, etc.)"
    implemented: true
    working: true
    file: "backend/server.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
        -working: "NA"
        -agent: "main"
        -comment: "NEW round-3 feature: PUT /api/admin/site-settings (admin) accepts channel_whatsapp, channel_telegram, channel_arattai, channel_youtube, channel_instagram, channel_app. GET /api/site-settings (public) returns all these fields."
        -working: true
        -agent: "testing"
        -comment: "✅ ALL 6 TESTS PASSED (6/6). (1) PUT /api/admin/site-settings without auth → 401✅. (2) PUT /api/admin/site-settings with admin auth and {channel_whatsapp, channel_telegram} → 200✅. (3) GET /api/site-settings → 200 with all 6 required keys (channel_whatsapp, channel_telegram, channel_arattai, channel_youtube, channel_instagram, channel_app)✅. (4) channel_whatsapp value correct ('https://whatsapp.com/channel/abc')✅. (5) channel_telegram value correct ('https://t.me/mychan')✅. All endpoints working correctly with proper auth enforcement and data persistence."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 4
  run_ui: false

test_plan:
  current_focus:
    - "SEO edit converts scraped API post to manual (protects from shuffle)"
    - "Full edit converts scraped API post to manual"
    - "Promo cleanup endpoint"
    - "Channel link settings (WhatsApp, Telegram, etc.)"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
    -agent: "main"
    -message: |
      ROUND 2 — please test these NEW backend endpoints (admin auth cookie via POST /api/auth/login
      email=admin@hrdigitalservices.in password=Admin@12345):
      1) GET /api/admin/overview → returns {total_vacancies,total_views,total_blogs,total_reviews,manual_vacancies,
         vacancy_views,blog_views,contacts}. Requires admin; 401/403 without auth.
      2) POST /api/admin/uploads (admin, multipart 'file') with a small PDF → returns {url,name,size,mime}; the url
         should be GET-able at /api/uploads/{fname}. Object storage is now configured (EMERGENT_LLM_KEY set).
      3) Manual vacancy tags + important_links:
         - POST /api/admin/vacancies with JSON including tags:["a","b"] and important_links:[{"label":"Notification","url":"https://x.com/n.pdf","type":"pdf"},{"label":"Apply","url":"https://x.com/apply","type":"link"}] → 200.
         - GET /api/vacancies/{id} returns tags and important_links exactly.
         - PUT /api/admin/vacancies/{id} updating tags/important_links persists.
      Note: previous round (search synonyms, views increment, reviews CRUD, custom_head) already PASSED — no need to retest unless quick.
    -agent: "testing"
    -message: |
      ✅ ALL BACKEND TESTS PASSED (20/20)
      
      Comprehensive testing completed for all 4 backend tasks:
      
      1. VACANCY SEARCH (3/3 tests passed):
         - GET /api/vacancies?q=gds ✅
         - GET /api/vacancies?q=india%20post ✅
         - GET /api/vacancies?q=gramin%20dak ✅
         All queries correctly return "India Post — Gramin Dak Sevak – 23757 Posts" vacancy.
         Synonym expansion (gds → gramin dak sevak) working perfectly.
      
      2. VIEW COUNTER (2/2 tests passed):
         - Blog view counter: increments correctly (4→5) ✅
         - Vacancy view counter: increments correctly (8→9) ✅
         Views persist and are returned in GET responses.
      
      3. REVIEWS CRUD (10/10 tests passed):
         - POST /api/reviews (blog) ✅
         - POST /api/reviews (vacancy) ✅
         - GET /api/reviews with count & average ✅
         - Invalid target_type rejection (400) ✅
         - GET /api/admin/reviews with target_title ✅
         - Admin auth enforcement (401/403) ✅
         - PUT /api/admin/reviews/{id}/toggle (hide) ✅
         - Hidden review exclusion from public GET ✅
         - PUT /api/admin/reviews/{id}/toggle (unhide) ✅
         - DELETE /api/admin/reviews/{id} ✅
      
      4. CUSTOM HEAD (4/4 tests passed):
         - Blog custom_head update via PUT /api/admin/blogs/{id} ✅
         - Blog custom_head returned in GET /api/blogs/{slug} ✅
         - Vacancy custom_head update via PUT /api/admin/vacancies/{id}/seo ✅
         - Vacancy custom_head returned in GET /api/vacancies/{id} ✅
      
      All endpoints functioning correctly with proper validation, authentication, and data persistence.
    -agent: "main"
    -message: |
      ROUND 3 — Re-verify the Round 2 endpoints as requested:
      1) GET /api/admin/overview (admin) → must return JSON with keys: total_vacancies, total_views, total_blogs, 
         total_reviews, manual_vacancies, vacancy_views, blog_views, contacts (all numbers). Without admin auth → 401/403.
      2) POST /api/admin/uploads (admin, multipart form field name 'file') — upload a tiny generated PDF (application/pdf). 
         Expect 200 with {url, name, size, mime}. Then GET the returned url (it is like /api/uploads/{fname}) and confirm 
         200 with PDF content-type. Object storage is configured (EMERGENT_LLM_KEY set). Also confirm non-admin gets 401/403.
      3) Manual vacancy tags + important_links:
         - POST /api/admin/vacancies (JSON) with tags and important_links → 200; capture returned id.
         - GET /api/vacancies/{id} → returns tags and important_links (label/url/type preserved).
         - PUT /api/admin/vacancies/{id} (JSON) changing tags and important_links → 200; GET again confirms update persisted.
         - Cleanup: DELETE /api/admin/vacancies/{id}.
    -agent: "testing"
    -message: |
      ✅ ROUND 3 COMPLETE: ALL 13 TESTS PASSED (13/13)
      
      Re-verification testing completed successfully for all 3 backend endpoint groups:
      
      1. ADMIN OVERVIEW (2/2 tests passed):
         - GET /api/admin/overview without auth → 401 ✅
         - GET /api/admin/overview with admin auth → 200 ✅
           * All 8 required keys present: total_vacancies, total_views, total_blogs, total_reviews, 
             manual_vacancies, vacancy_views, blog_views, contacts
           * All values are numeric (total_vacancies=973, manual_vacancies=0, total_blogs=1, 
             total_reviews=3, total_views=26)
      
      2. ADMIN UPLOADS (3/3 tests passed):
         - POST /api/admin/uploads without auth → 401 ✅
         - POST /api/admin/uploads with admin auth → 200 ✅
           * Response contains all required keys: url, name, size, mime
           * mime=application/pdf ✅
           * Uploaded file: url=/api/uploads/f700147d78e64048a2e6c66407d0557d.pdf, size=312 bytes
         - GET /api/uploads/{fname} → 200 with Content-Type: application/pdf ✅
           * Object storage working correctly
      
      3. MANUAL VACANCY TAGS & IMPORTANT_LINKS (8/8 tests passed):
         - POST /api/admin/vacancies with tags=['10th pass','haryana','latest'] and 
           important_links=[{Notification,pdf},{Apply Online,link}] → 200 ✅
           * Created vacancy ID: 6a9ad96ccf0bd9746fdcef44
         - GET /api/vacancies/{id} → 200 ✅
           * Tags returned correctly: ['10th pass', 'haryana', 'latest'] ✅
           * important_links[0]: {label:'Notification', url:'https://example.com/notif.pdf', type:'pdf'} ✅
           * important_links[1]: {label:'Apply Online', url:'https://example.com/apply', type:'link'} ✅
         - PUT /api/admin/vacancies/{id} with tags=['updated'] and 
           important_links=[{Syllabus,pdf}] → 200 ✅
         - GET /api/vacancies/{id} after update → 200 ✅
           * Updated tags: ['updated'] ✅
           * Updated important_links: [{label:'Syllabus', url:'https://example.com/s.pdf', type:'pdf'}] ✅
         - DELETE /api/admin/vacancies/{id} → 200 ✅
      
      All endpoints working correctly with:
      - Proper authentication enforcement (401 for non-admin)
      - Correct response structure and data types
      - Data persistence across GET/PUT operations
      - Object storage integration functional
      - Tags and important_links arrays preserved with all fields (label, url, type)
    -agent: "main"
    -message: |
      ROUND 4 — Test the NEW search analytics feature in /app/backend/server.py. Base URL = REACT_APP_BACKEND_URL + "/api". 
      Admin auth cookie via POST /api/auth/login {"email":"admin@hrdigitalservices.in","password":"Admin@12345"}; 
      admin routes use require_admin.
      
      1) Search logging: GET /api/vacancies?q=police&page=1 a couple of times, and GET /api/vacancies?q=zzqqxx-nomatch&page=1 
         (a term that returns 0 results). These calls should silently log to a search_logs collection (no error, still returns 
         normal paginated JSON).
      
      2) GET /api/admin/search-analytics (admin) → 200 JSON with keys: days, total_searches (number), unique_terms (number), 
         top (array), zero_results (array).
         - Each item in top has {query, count, avg_results, last_at}.
         - top should be sorted by count descending.
         - "police" should appear in top with count>=2.
         - zero_results should contain the nonsense term "zzqqxx-nomatch" (avg_results 0 / results 0), since it returns no vacancies.
         - Test the days query param: GET /api/admin/search-analytics?days=7 → 200 and days==7.
         - Without admin auth → 401/403.
      
      Report pass/fail per item with status codes and key response fields. Do not modify code.
    -agent: "testing"
    -message: |
      ✅ ROUND 4 COMPLETE: ALL 14 TESTS PASSED (14/14)
      
      Search analytics feature testing completed successfully:
      
      1. SEARCH LOGGING (2/2 tests passed):
         - GET /api/vacancies?q=police&page=1 (3 times) → 200 with 4 results each ✅
           * Searches logged silently (no errors, normal paginated JSON returned)
         - GET /api/vacancies?q=zzqqxx-nomatch&page=1 → 200 with 0 results ✅
           * Zero-result search logged silently
      
      2. ADMIN SEARCH ANALYTICS ENDPOINT (12/12 tests passed):
         - GET /api/admin/search-analytics without auth → 401 ✅
         - GET /api/admin/search-analytics with admin auth → 200 ✅
           * Response structure: all required keys present (days, total_searches, unique_terms, top, zero_results) ✅
           * Data types correct: days=30 (int), total_searches=19 (int), unique_terms=12 (int) ✅
           * top is array with 12 items ✅
           * zero_results is array with 3 items ✅
         
         - Top searches verification:
           * 'police' found in top with count=5 (>=2 as required) ✅
           * avg_results=4 for 'police' searches ✅
           * Top item structure correct: {query, count, avg_results, last_at} ✅
           * Top array correctly sorted by count descending: [5, 3, 2, 1, 1...] ✅
         
         - Zero results verification:
           * 'zzqqxx-nomatch' found in zero_results with avg_results=0 ✅
         
         - Days parameter:
           * GET /api/admin/search-analytics?days=7 → 200 with days=7 ✅
      
      All requirements met:
      - Silent search logging working (no errors, normal responses)
      - Admin endpoint requires authentication (401 without auth)
      - Response structure matches specification exactly
      - Top searches sorted by count descending
      - "police" appears with count>=2
      - "zzqqxx-nomatch" appears in zero_results with avg_results=0
      - Days query parameter working correctly
    -agent: "main"
    -message: |
      ROUND 5 — Test these NEW round-3 backend behaviors in /app/backend/server.py (HR Digital Services). 
      Base URL = REACT_APP_BACKEND_URL + "/api". Admin auth cookie via POST /api/auth/login 
      {"email":"admin@hrdigitalservices.in","password":"Admin@12345"}; admin routes use require_admin.

      1) SEO edit converts a scraped API post -> manual (protects from shuffle):
         - GET /api/admin/vacancies-seo (admin) and find an item with source != "manual". Capture its id and current seo_title.
         - PUT /api/admin/vacancies/{id}/seo (admin, JSON) {"seo_title":"MYCUSTOM SEO TITLE","seo_description":"my desc"} → 200.
         - GET /api/vacancies/{id} → source MUST now be "manual" and seo_title == "MYCUSTOM SEO TITLE".
         - POST /api/admin/vacancies/shuffle-seo (admin) → 200. Then GET /api/vacancies/{id} again → seo_title MUST still be "MYCUSTOM SEO TITLE" (shuffle must NOT touch it because it's manual now).

      2) Full edit converts a scraped API post -> manual:
         - From GET /api/admin/vacancies-seo find ANOTHER item with source != "manual". Capture id.
         - PUT /api/admin/vacancies/{id} (admin, JSON) {"title":"Edited Full Title","organization":"My Org","category":"other","tags":["tagx"],"important_links":[{"label":"Official","url":"https://example.gov.in","type":"link"}]} → 200 (previously this endpoint returned 400 for non-manual; now it must succeed).
         - GET /api/vacancies/{id} → source=="manual", title=="Edited Full Title", tags==["tagx"], important_links contains the Official link.

      3) Promo cleanup endpoint:
         - POST /api/admin/vacancies/clean-promo (admin) → 200 with {ok:true, cleaned:<int>}.
         - Without admin auth → 401/403.

      4) Channel link settings:
         - PUT /api/admin/site-settings (admin, JSON) {"channel_whatsapp":"https://whatsapp.com/channel/abc","channel_telegram":"https://t.me/mychan"} → 200.
         - GET /api/site-settings → returns channel_whatsapp and channel_telegram with those exact values, and also includes keys channel_arattai, channel_youtube, channel_instagram, channel_app (may be empty strings).
         - Without admin auth, PUT → 401/403.

      Report pass/fail per item with status codes and key response fields. Do not modify code.
    -agent: "testing"
    -message: |
      ✅ ROUND 5 COMPLETE: ALL 19 TESTS PASSED (19/19)
      
      Round-3 backend behaviors testing completed successfully:
      
      1. SEO EDIT CONVERTS TO MANUAL (6/6 tests passed):
         - Found scraped vacancy: ID=6a9ac89f673c1f9a5e67fe06, source=freejobalert ✅
         - PUT /api/admin/vacancies/{id}/seo with seo_title='MYCUSTOM SEO TITLE' → 200 ✅
         - GET /api/vacancies/{id} → source changed to 'manual' (was freejobalert) ✅
         - seo_title persisted as 'MYCUSTOM SEO TITLE' ✅
         - POST /api/admin/vacancies/shuffle-seo → 200, shuffled 972 vacancies ✅
         - GET /api/vacancies/{id} after shuffle → seo_title STILL 'MYCUSTOM SEO TITLE' (protected from shuffle) ✅
      
      2. FULL EDIT CONVERTS TO MANUAL (5/5 tests passed):
         - Found second scraped vacancy: ID=6a9ac89f673c1f9a5e67fe04, source=freejobalert ✅
         - PUT /api/admin/vacancies/{id} with full edit → 200 ✅
         - GET /api/vacancies/{id} → source changed to 'manual' (was freejobalert) ✅
         - title='Edited Full Title' ✅
         - tags=['tagx'] ✅
         - important_links contains Official link {label:'Official', url:'https://example.gov.in', type:'link'} ✅
      
      3. PROMO CLEANUP ENDPOINT (2/2 tests passed):
         - POST /api/admin/vacancies/clean-promo without auth → 401 ✅
         - POST /api/admin/vacancies/clean-promo with admin auth → 200 {ok:true, cleaned:2} ✅
      
      4. CHANNEL LINK SETTINGS (6/6 tests passed):
         - PUT /api/admin/site-settings without auth → 401 ✅
         - PUT /api/admin/site-settings with admin auth → 200 ✅
         - GET /api/site-settings → 200 with all 6 required keys ✅
           * channel_whatsapp='https://whatsapp.com/channel/abc' ✅
           * channel_telegram='https://t.me/mychan' ✅
           * Also includes: channel_arattai, channel_youtube, channel_instagram, channel_app ✅
      
      All requirements met:
      - SEO edit protection working (manual posts not touched by shuffle)
      - Full edit conversion working (scraped posts become manual)
      - Promo cleanup endpoint working with proper auth
      - Channel settings CRUD working with all required fields
      - All endpoints have proper authentication enforcement (401/403 without admin auth)
