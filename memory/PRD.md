# PRD — HR Digital Services (formerly Haryana Enterprises)

## Original Problem Statement
User's existing app (GitHub: sanjivkumar71771-commits/Haryana-Enterprises) — Haryana govt-jobs + solar portal. Requested additions into THEIR code:
1. **WhatsApp Smart Engine** — auto WhatsApp summary per new job (API/manual): 🔥 Job Name 🔥 | ✅ कुल पद | ✅ योग्यता | 📅 आखरी तारीख | 👇 लिंक; Join WhatsApp Channel buttons in header/footer/every post.
2. **SEO Shuffler & Manager** — rotate API jobs' Title/Description for uniqueness; Rank Math style per-job SEO (Custom Title, Focus Keyword, Description) in admin.
3. **Homepage Swap** — vacancy listing at `/`, solar homepage at `/solar`, menu link 'Solar Services'.
4. **Performance & Admin** — 20 vacancies/page with pagination; Resume/CV template upload system in admin.
5. **Blogs Section** — public blogs + admin 'Manage Blogs' with text editor & image upload.
6. **Rebrand** — "Haryana Enterprises" → "HR DIGITAL SERVICES" (एचआर डिजिटल सर्विसेज).

## User Choices
- WhatsApp Channel: https://whatsapp.com/channel/0029Va4Owji5Ui2bLEktCl1C
- WhatsApp summary: auto-generate + copy button in admin (no auto-send)
- Admin: simple email/password (credentials provisioned via ADMIN_EMAIL / ADMIN_PASSWORD env vars — not committed)
- Jobs source: existing FreeJobAlert scraper (API) + manual admin posts

## Architecture
- **Backend**: FastAPI + Motor (MongoDB), APScheduler (6h scrape refresh), JWT+cookie auth (auth.py), Emergent object storage for uploads (blog images, CV files) served via `/api/uploads/{fname}`.
- **Frontend**: React CRA, react-helmet-async SEO, i18n (hi/en), dark/glass theme, react-icons.
- **DB collections**: vacancies (manual + scraped), blogs, resume_templates, uploads, users, site_content, etc.

## Implemented (2026-09-03)
- WhatsApp Smart Engine: `build_whatsapp_summary()` in server.py; auto on manual create/update, scraper refresh, startup backfill; copy buttons in AdminVacancies rows + Job SEO Manager; WhatsAppSummaryCard on vacancy detail; Join Channel buttons in Header (desktop+mobile), Footer, vacancy listing banner, job detail, blog detail.
- SEO Shuffler: `_seo_variant()` + 6 title prefixes/6 desc openers; auto-applied to scraped jobs; POST `/api/admin/vacancies/shuffle-seo` re-rotates; per-job SEO edit PUT `/api/admin/vacancies/{id}/seo`; live SEO score in VacancyForm + AdminJobSEO.
- Homepage swap: `/` = Vacancies, `/solar` = old Home, `/vacancies` redirects to `/`; nav + footer updated.
- Pagination: GET `/api/vacancies` returns `{items,total,page,pages}` (20/page default); UI controls on homepage.
- Resume/CV templates: admin upload (PDF/DOC/DOCX/images → object storage), public list on /downloads.
- Blogs: full CRUD (multipart + image upload), public /blogs + /blogs/{slug}, admin rich-text editor.
- Rebrand: strings.js, Header, Footer, index.html, backend seeds, DEFAULT_SITE_CONTENT (added seo:solar, seo:blogs keys).
- Migrated 24 demo Haryana jobs into `vacancies` (manual source) so homepage has Haryana-specific content.
- Fixed CORS: frontend now same-origin (REACT_APP_BACKEND_URL = current preview URL); backend CORS_ORIGINS explicit list.

## Implemented (2026-09-03, round 2)
- Homepage redesign per user's FreeJobAlert reference images: filter panel simplified to Search + Qualification only (state select, saved toggle, category chips, offline-mode chip removed from panel to reduce customer confusion).
- "New Updates" section below email-alerts box: 9 latest vacancies in numbered modern cards (3-col grid), blue gradient header with live pulse dot, "View All" button scrolls to listing.
- Category pills (modern gradient blue, rounded-full) + State pills (HR, DL, PB... short codes) above the listing — both functional (set filters + scroll).
- Webpushr push notifications: snippet in public/index.html (site key placeholder WEBPUSHR_SITE_KEY_HERE — awaiting user's key), public/webpushr-sw.js (standard importScripts worker), PushSubscribeButton (bell) in New Updates header, backend POST /api/webpushr/subscriber stores subscriber IDs in Mongo `push_subscribers`.

## Admin Panel Tabs
Manual Vacancies | Job SEO Manager | Manage Blogs | CV Templates | Site SEO | Front-page Text

## Backlog
- P1: WhatsApp auto-post to channel (needs WhatsApp Business API key from user)
- P1: Public /resume-templates standalone page (currently inside /downloads)
- P1: Webpushr site key from user (placeholder in index.html — everything else ready)
- P2: Blog categories/tags, blog SEO fields
- P2: Sitemap.xml update for /solar + /blogs routes
- P2: Admin inquiries view for solar enquiry form

## Implemented (2026-09-03, round 3)
- **2nd job source: Haryana DC Rate / HKRN** — `fetch_haryana_dcrate()` in scrapers.py scrapes jobpulse.in DC-Rate + HKRN category pages (official HKRN portal blocks non-India traffic; haryanadcratejobs.com is now a spam preset site, so jobpulse mirrors are used). Tagged source="haryana_dcrate", auto category/state (default haryana), WhatsApp summaries + SEO variants auto-applied.
- **Cross-source dedupe** — every vacancy gets `dedupe_key` (normalized title); refresh merges same-title-different-URL posts into one doc (alt_urls) instead of duplicating; one-time startup backfill; cleaned 44 legacy duplicates.
- **Scheduler: 6h → 1h** auto refresh for BOTH sources; frontend text updated ("हर 1 घंटे में automatic update").
- `_cat_from_title` now recognizes hkrn/dc-rate keywords → haryana category.

## Bug Fix (2026-09-03)
- **"Failed to load" cross-origin bug**: frontend had env-baked backend URL; opening the site via a different preview domain broke credentialed CORS requests. Fixed with dynamic same-origin BACKEND_URL in lib/api.js (all 10 files now import from it). Verified by testing_agent on both domains — 100% pass (iteration_2.json).

## Test Credentials
- Admin: provisioned via ADMIN_EMAIL / ADMIN_PASSWORD env vars (see /app/memory/test_credentials.md, gitignored)
- Leaked credential (nyolkrish142@gmail.com) rotated out on 2026-06.

## Color Re-theme + Security Fix (2026-06)
Task: apply blue (#2563EB) + mint (#EAF7F0) palette from reference; color-only, no layout/component changes; skip /solar structure.
- **App migrated in** from GitHub (nyolkrish142-hub/newapp) — this pod started as a blank template.
- **Security fix**: JWT_SECRET added to backend/.env (no fallback); admin creds moved to ADMIN_EMAIL/ADMIN_PASSWORD env (rotated to a fresh strong password, old leaked pw purged from auth_testing.md, backend_test.py, PRD.md, test_credentials.md); confirmed HttpOnly+Secure+SameSite=None auth cookies (auth.py::set_auth_cookies). Verified: old cred 401, unauth admin 401, new admin 200.
- **Theme tokens** (source of truth): index.css `:root` now defines --primary #2563EB, --primary-dark #1D4ED8, --success #EAF7F0, --success-border #A7D8BE, --accent #EFF4FF, --page-bg #F8FAFC, --ink #1E293B, --wa-green #25D366. tailwind.config.js gained primary/primary-dark/accent/success/whatsapp/bg/text tokens.
- **Light theme** (already the site default) retuned to exact reference hexes: page bg #F8FAFC, text #1E293B, chips #EFF4FF/blue, mint zones #EAF7F0 + green border. Fixed btn-mint/btn-amber/signin-badge text to white for AA contrast.
- **Amber/orange purge**: all `amber-*`/`orange-*` Tailwind classes → `blue-*` (same shade) across in-scope public+admin files only (Vacancies, VacancyDetail, Footer, Notices, About, FAQ, Enquiry, JobAlertSubscribe, NoticeTicker, AdminAnalytics, admin/*). Home.jsx (/solar) + solar components (HeroSlider, SchemesInfo, SolarCalculator) left untouched. WhatsApp green kept.
- Admin panel already used blue-600/slate light theme (blue-600 = #2563EB) — needed no change.

## Note on git history rewrite
Remote GitHub history (nyolkrish142-hub/newapp) still contains the old leaked password in past commits. Rewriting remote history requires the user's push access/token (not provided). Since the password is now ROTATED, the old exposed value is useless. User should still run git filter-repo/BFG + force-push if they want it scrubbed from history.

---

## Update (2026-06 session) — Theme system: finished pending remap

Continued from GitHub repo `nikhilsahu6782-sys/2026` (HR Digital Services). Existing
CSS-variable theme system (ThemeContext/ThemeSwitcher, light/dark, palette switcher,
custom color picker, admin site-default) was already in place. Completed the two pending items:

- **Ambient glows now theme-aware**: hardcoded greenish `bg-emerald-500/*.blur-3xl`
  glow blobs remapped to the active accent via `body.has-theme` in `frontend/src/themes.css`.
- **Hardcoded emerald/green Tailwind classes remapped app-wide** (CSS-only, no JSX
  touched): text/bg/border/gradient/ring/shadow emerald+green utilities, the arbitrary-hex
  New-Updates banner gradient (`from-[#065f46] via-[#059669] to-[#10b981]`), and key custom
  classes (`.btn-mint`, `.pill-3d`, `.stat-emerald`, `.nu-*`, `.fee-row`) all follow the theme
  accent when a named theme OR custom primary is active. Default Light/Dark stay untouched.
- **ThemeSwitcher dropdown z-index fix**: `.top-strip` given `position:relative; z-index:50`
  and panel bumped to `z-[80]` so the palette dropdown floats above the Free-Alert / New-Updates
  sections instead of rendering behind them.

Verified via screenshots: Dracula (purple), Nature (light green), custom primary #E11D48
(crimson) all re-skin fully incl. the banner; default untouched; dropdown renders on top.

Files: `frontend/src/themes.css`, `frontend/src/index.css`, `frontend/src/components/ThemeSwitcher.jsx`.

## Update (2026-09-05 session) — Harmony palette preview, UX polish, Resend email, Admin Site Theme & Links
- **Harmony palette (PREVIEW ONLY, not live)**: `frontend/src/harmony.css` + `?preview=harmony` / `?preview=off` toggle (sessionStorage `harmonyPreview`, `body.harmony`). 3-colour palette per theme (--emerald + --accent-2 warm + --accent-3 cool), glass → clean solid surfaces, amber/blue glow blobs theme-aware, muted banner, gentle pills. Custom primary derives companions (ThemeContext `companions()`). **User decision pending: apply live / tweak / remove.**
- **UX edits (live)**: nu-pill text black(light)/grey(dark); poster share buttons → chip style; hover-only card shadows (global rule in index.css); New-Updates section = single glass card, title in section-title font w/ amber accent, OrgAvatar monogram (components/OrgAvatar.jsx) instead of briefcase; WhatsApp banner brand-green `.wa-banner` + popping `.wa-pop` CTA; Job-alert subscribe CTA = popping btn-mint; filters combine (no reset) + "सभी फ़िल्टर हटाएँ"; Haryana removed from category select; footer light/dark aware (`.footer-main`), contact = address + 8168762016 + email; SocialShare row (components/SocialShare.jsx) on VacancyDetail + BlogDetail; header WhatsApp btn shadow removed; header "फ्री सर्वे बुक करें" → wa.me/918168762016 prefilled.
- **Push button fix**: PushSubscribeButton requests Notification permission directly (Webpushr key still placeholder) — verified iteration_4/5.
- **Email delivery**: emails.py now sends via **Resend** when RESEND_API_KEY set (backend/.env; sender onboarding@resend.dev, free tier → only verified recipient until domain verified). Verified iteration_5.
- **Admin → Site Theme & Links** (`/admin/site`, pages/admin/AdminSite.jsx): theme cards, primary colour, lock toggle, footer social links (facebook/twitter/instagram/whatsapp/youtube). Backend `/site-settings` adds theme_locked, theme_updated_at, social_*; PUT validates theme whitelist + #RRGGBB. ThemeContext adopts admin theme live for everyone when stamp changes / locked (switcher hidden when locked). Footer icons always visible; unset → link to `/`. Verified iteration_6.
- Backlog: decide Harmony live; Webpushr site key; Resend domain verification (SENDER_EMAIL).

## Update (2026-06 session, fork) — 9 features copied from GitHub repo `suresh-hr`
User asked to copy ONLY these 9 features' code from their repo (sureshkhetlan256-creator/suresh-hr) into current app, leaving everything else unchanged. Done by diffing repo vs /app and copying 13 changed files. Tested (iteration_7.json: backend 6/6, frontend 9/9, 0 issues).
1. **Branding auto-replace** — scrapers.py `apply_brand()`/`brand_html()` swap "FreeJobAlert"→"HR Digital Services" in text nodes; PDF/href links preserved. One-time startup backfill (`settings._id=brand_applied_v1`).
2. **Manual lock** — refresh_vacancies_into_db skips `source=='manual'` posts; admin edit already promotes to manual; only manual delete removes.
3. **Search without filter** — GET /api/vacancies: when `q` present, search spans ALL categories (incl admit_card/result); without q, those stay excluded from default view (server.py ~L694).
4. **Sticky navbar** — Header.jsx wraps in `<header className="sticky top-0 z-50" data-testid="site-header">`.
5. **Image aspect (no crop)** — HeroCarousel/BlogDetail/Blogs card/AdminSlides use object-contain; new `fitImageToSize()` in imagePresets.js used by AdminBlogs/AdminSlides uploads.
6. **RTE pre-fill on edit** — RichTextEditor.jsx syncs external `value` when editor unfocused (fixes blank description on edit).
7. **Working TOC** — htmlContent.js `buildTableOfContents()` builds nav.post-toc clickable smooth-scroll links, removes duplicate raw TOC; CSS in index.css.
8. **Admin Views column** — AdminVacancies.jsx shows Views count (data-testid admin-vac-views-<id>).
9. **Blog center image** — backend blog create/update accept `center_image`/`remove_center_image` → `center_image_url`; AdminBlogs.jsx optional Center image upload; BlogDetail renders it (data-testid blog-center-image).
Files copied: backend/scrapers.py, backend/server.py, frontend/src/{components/Header.jsx, components/HeroCarousel.jsx, components/RichTextEditor.jsx, index.css, lib/htmlContent.js, lib/imagePresets.js, pages/BlogDetail.jsx, pages/Blogs.jsx, pages/admin/AdminBlogs.jsx, pages/admin/AdminSlides.jsx, pages/admin/AdminVacancies.jsx}.

## Bug fix (2026-06) — TOC duplicate not removed for "On this Page" posts
- Reported: generated pills TOC nav rendered fine, but the raw scraped duplicate TOC block still showed below (a `<details class="jump-nav-mobile">` + space-blob label line). Happened on posts whose TOC label is "On this Page" (some posts use "Table Of Contents", others "On this Page"). Old builder only matched the literal string "table of contents", so the mobile block for other-labelled posts survived.
- Fix (frontend/src/lib/htmlContent.js `buildTableOfContents`): added `TOC_TITLE_RE` (table of contents | on this page | in this article/post/page | contents | index | jump to) and `TOC_CLASS_RE` (jump-nav | jump-mobile | toc). Detection now matches TOC title variants OR the source's stable wrapper classes; parseLabels strips any variant prefix; listSibling check uses both. Result: BOTH desktop `<nav class="jump-nav-desktop">` and mobile `<details class="jump-nav-mobile">` are detected → one working pills-nav kept, all other raw TOC blocks removed. Length guard raised 900→1200.
- Verified iteration_8.json (frontend 100%): both variants render 1 pills-nav, zero raw duplicate, smooth-scroll on click, no regression on TOC-less posts.
- NOTE (unrelated, not fixed): /api/site-settings/public returns 401 for anonymous users on every page load — harmless, flagged by testing agent.
