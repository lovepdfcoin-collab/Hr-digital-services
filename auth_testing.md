# Custom Email/Password JWT Authentication - Testing Playbook

> Admin credentials are provisioned from environment variables (`ADMIN_EMAIL`,
> `ADMIN_PASSWORD`) and seeded on backend startup. They are NOT committed to the
> repo. See `/app/memory/test_credentials.md` (gitignored working note) for the
> values used in this environment.

## Step 1: MongoDB Verification
```
mongosh
use test_database
db.users.find({role: "admin"}).pretty()
```
Verify: bcrypt hash starts with `$2b$`, unique index on users.email.

## Step 2: API Testing
```
TOKEN=$(curl -s -X POST $API/api/auth/login -H "Content-Type: application/json" -d '{"email":"'"$ADMIN_EMAIL"'","password":"'"$ADMIN_PASSWORD"'"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")
curl -s $API/api/auth/me -H "Authorization: Bearer $TOKEN"
```
Login returns access_token + user; /me returns admin user without password_hash.

## Step 3: Admin Protection
```
curl -s $API/api/admin/jobs   # expect 401
curl -s $API/api/admin/jobs -H "Authorization: Bearer $TOKEN"   # expect 200
```

## Auth hardening notes
- Passwords hashed with bcrypt (`$2b$`).
- Auth cookies are HttpOnly + Secure + SameSite=None (see `backend/auth.py::set_auth_cookies`).
- `JWT_SECRET` is read from the environment; no default fallback.
