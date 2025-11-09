# Git Quest API Testing Guide

## Prerequisites

Before testing, ensure:

1. **Database is running:**
   ```bash
   docker-compose up -d
   docker-compose ps  # Verify postgres & redis are running
   ```

2. **Tutorials are loaded:**
   ```bash
   python3 data-pipeline/scripts/load_to_db.py
   ```

3. **Backend server is running:**
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 -m uvicorn app.main:app --reload
   ```
   Server should be at: `http://localhost:8000`

---

## Testing Flow

### Step 1: Health Check ✅

**Test that the API is running:**

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "git-quest-api",
  "version": "1.0.0"
}
```

---

### Step 2: Register a New User ✅

**Create your first player account:**

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gitquest.com",
    "username": "testplayer",
    "password": "TestPass123",
    "display_name": "Test Player"
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "email": "test@gitquest.com",
  "username": "testplayer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-09T...",
  "last_login": null
}
```

**What happens:**
- User account created in `users` table
- Player profile created in `players` table
- Password hashed with bcrypt
- Initial XP: 0, Level: introduction

**Test error handling:**
```bash
# Try registering same email again (should fail)
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gitquest.com",
    "username": "testplayer2",
    "password": "TestPass123"
  }'
```

**Expected:** `400 Bad Request - Email already registered`

---

### Step 3: Login and Get Tokens 🔑

**Login to get access & refresh tokens:**

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testplayer&password=TestPass123"
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**IMPORTANT:** Save the access_token for next steps!

**For convenience, save it:**
```bash
# Copy the access_token from response and set it as variable
export ACCESS_TOKEN="your-access-token-here"
```

**Test error handling:**
```bash
# Wrong password (should fail)
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testplayer&password=WrongPass123"
```

**Expected:** `401 Unauthorized - Incorrect username or password`

---

### Step 4: Get Current User Info 👤

**Verify authentication works:**

```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "email": "test@gitquest.com",
  "username": "testplayer",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-11-09T...",
  "last_login": "2025-11-09T..."
}
```

**Test without token (should fail):**
```bash
curl -X GET "http://localhost:8000/api/auth/me"
```

**Expected:** `401 Unauthorized - Not authenticated`

---

### Step 5: Get Player Profile 🎮

**Get your game profile:**

```bash
curl -X GET "http://localhost:8000/api/players/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "player-uuid",
  "user_id": "user-uuid",
  "username": "testplayer",
  "display_name": "Test Player",
  "avatar_url": null,
  "created_at": "2025-11-09T...",
  "current_level": "introduction",
  "total_xp": 0
}
```

---

### Step 6: Get Player Statistics 📊

**Check your stats (should be all zeros for new player):**

```bash
curl -X GET "http://localhost:8000/api/players/me/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "player_id": "uuid",
  "username": "testplayer",
  "total_xp": 0,
  "current_level": "introduction",
  "lessons_completed": 0,
  "lessons_in_progress": 0,
  "challenges_completed": 0,
  "achievements_unlocked": 0,
  "total_learning_time_seconds": 0
}
```

---

### Step 7: List All Lessons 📚

**Get all available lessons:**

```bash
curl -X GET "http://localhost:8000/api/lessons"
```

**Expected Response:**
```json
[
  {
    "id": "introduction-version-control",
    "title": "Version control",
    "level": "introduction",
    "order_index": 100,
    "total_sections": 13,
    "git_commands": []
  },
  {
    "id": "introduction-creating-repos",
    "title": "Creating repos",
    "level": "introduction",
    "order_index": 101,
    "total_sections": 10,
    "git_commands": ["git init", "git status", "git clone"]
  },
  ...
]
```

**Filter by level:**

```bash
# Get only introduction lessons
curl -X GET "http://localhost:8000/api/lessons?level=introduction"

# Get only advanced lessons
curl -X GET "http://localhost:8000/api/lessons?level=advanced"
```

---

### Step 8: Get Specific Lesson Content 📖

**Get full lesson with all sections:**

```bash
curl -X GET "http://localhost:8000/api/lessons/introduction-staging-and-committing-files"
```

**Expected Response:**
```json
{
  "id": "introduction-staging-and-committing-files",
  "title": "Staging and committing files",
  "level": "introduction",
  "order_index": 103,
  "story_hook": null,
  "content": [
    {
      "section_number": 1,
      "title": "Staging and committing files",
      "timestamp_start": "00:00",
      "timestamp_end": "00:08",
      "content": "We've set up our repo...",
      "git_commands": []
    },
    ...
  ],
  "learning_objectives": [
    "Staging and committing files",
    "The Git workflow",
    ...
  ],
  "practice_prompt": "Now it's your turn to save files using Git!",
  "git_commands": ["git add", "git add .", "git commit"],
  "word_count": 435,
  "total_sections": 6
}
```

---

### Step 9: Start a Lesson 🚀

**Mark a lesson as "in progress":**

```bash
curl -X POST "http://localhost:8000/api/lessons/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "introduction-staging-and-committing-files"
  }'
```

**Expected Response:**
```json
{
  "id": "progress-uuid",
  "player_id": "player-uuid",
  "lesson_id": "introduction-staging-and-committing-files",
  "status": "in_progress",
  "started_at": "2025-11-09T...",
  "completed_at": null,
  "time_spent_seconds": 0,
  "score": null,
  "attempts": 0
}
```

---

### Step 10: Get Lesson Progress 📈

**Check your progress on a lesson:**

```bash
curl -X GET "http://localhost:8000/api/lessons/progress/introduction-staging-and-committing-files" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "id": "progress-uuid",
  "player_id": "player-uuid",
  "lesson_id": "introduction-staging-and-committing-files",
  "status": "in_progress",
  "started_at": "2025-11-09T...",
  "completed_at": null,
  "time_spent_seconds": 0,
  "score": null,
  "attempts": 0
}
```

---

### Step 11: Complete a Lesson ✅

**Mark lesson as completed (awards XP!):**

```bash
curl -X POST "http://localhost:8000/api/lessons/complete" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "introduction-staging-and-committing-files",
    "time_spent_seconds": 300,
    "score": 85
  }'
```

**Expected Response:**
```json
{
  "id": "progress-uuid",
  "player_id": "player-uuid",
  "lesson_id": "introduction-staging-and-committing-files",
  "status": "completed",
  "started_at": "2025-11-09T...",
  "completed_at": "2025-11-09T...",
  "time_spent_seconds": 300,
  "score": 85,
  "attempts": 1
}
```

**What happens:**
- Lesson marked as completed
- XP awarded: 50 (base) + 8 (score bonus) = 58 XP
- Player's total_xp updated

---

### Step 12: Verify XP Award 🏆

**Check your updated stats:**

```bash
curl -X GET "http://localhost:8000/api/players/me/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "player_id": "uuid",
  "username": "testplayer",
  "total_xp": 58,  // ← Should be updated!
  "current_level": "introduction",
  "lessons_completed": 1,  // ← Should be 1
  "lessons_in_progress": 0,
  "challenges_completed": 0,
  "achievements_unlocked": 0,
  "total_learning_time_seconds": 300  // ← Should match time spent
}
```

---

### Step 13: Get All Your Progress 📋

**See all lessons you've started/completed:**

```bash
curl -X GET "http://localhost:8000/api/lessons/progress/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected Response:**
```json
[
  {
    "id": "progress-uuid",
    "player_id": "player-uuid",
    "lesson_id": "introduction-staging-and-committing-files",
    "status": "completed",
    "started_at": "2025-11-09T...",
    "completed_at": "2025-11-09T...",
    "time_spent_seconds": 300,
    "score": 85,
    "attempts": 1
  }
]
```

---

### Step 14: Refresh Token 🔄

**Get a new access token using refresh token:**

```bash
# Save refresh token from login response
export REFRESH_TOKEN="your-refresh-token-here"

curl -X POST "http://localhost:8000/api/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{
    \"refresh_token\": \"$REFRESH_TOKEN\"
  }"
```

**Expected Response:**
```json
{
  "access_token": "new-access-token...",
  "refresh_token": "new-refresh-token...",
  "token_type": "bearer"
}
```

**What happens:**
- Old refresh token is revoked
- New access token issued (30 min expiry)
- New refresh token issued (7 day expiry)

---

### Step 15: Logout 🚪

**Revoke all refresh tokens:**

```bash
curl -X POST "http://localhost:8000/api/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

**Expected:** `204 No Content` (success, empty response)

**What happens:**
- All refresh tokens for this user are revoked
- Access token still works until it expires (30 min)
- Cannot refresh tokens anymore

---

## 🧪 Alternative: Use Swagger UI (Easier!)

Instead of curl commands, you can use the interactive API docs:

1. Open browser: `http://localhost:8000/api/docs`
2. Click "Authorize" button (top right)
3. Enter your access token: `Bearer your-token-here`
4. Click "Authorize"
5. Now you can test all endpoints with a nice UI!

**Benefits:**
- No need to copy/paste curl commands
- See request/response schemas
- Try different parameters easily
- Auto-formatted JSON

---

## 📊 Test Summary

### ✅ What Works Now:

| Feature | Endpoint | Auth Required |
|---------|----------|---------------|
| Register user | POST /auth/register | ❌ |
| Login | POST /auth/login | ❌ |
| Get current user | GET /auth/me | ✅ |
| Refresh token | POST /auth/refresh | ❌ |
| Logout | POST /auth/logout | ✅ |
| List lessons | GET /lessons | ❌ |
| Get lesson | GET /lessons/{id} | ❌ |
| Start lesson | POST /lessons/start | ✅ |
| Complete lesson | POST /lessons/complete | ✅ |
| Get progress | GET /lessons/progress/me | ✅ |
| Get player profile | GET /players/me | ✅ |
| Get player stats | GET /players/me/stats | ✅ |

### ⏳ Not Implemented Yet:

- Password reset email sending (token generation works)
- Challenges API
- Achievements auto-unlock
- Game sessions tracking
- Git command simulator
- Leaderboard

---

## 🐛 Troubleshooting

**Issue: "Could not validate credentials"**
- Check your access token is correct
- Token might be expired (30 min lifespan)
- Get new token with refresh endpoint

**Issue: "Connection refused"**
- Make sure FastAPI server is running on port 8000
- Check: `curl http://localhost:8000/health`

**Issue: "Lesson not found"**
- Make sure you ran `load_to_db.py` to load tutorials
- Check lesson IDs with: `curl http://localhost:8000/api/lessons`

**Issue: "Database error"**
- Ensure PostgreSQL is running: `docker-compose ps`
- Check database connection in .env file

---

## 🎯 Full Test Script

Run all tests in sequence:

```bash
#!/bin/bash

# Test 1: Health check
echo "1. Health check..."
curl http://localhost:8000/health

# Test 2: Register
echo "\n2. Registering user..."
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@gitquest.com",
    "username": "testplayer",
    "password": "TestPass123",
    "display_name": "Test Player"
  }'

# Test 3: Login
echo "\n3. Logging in..."
RESPONSE=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testplayer&password=TestPass123")

# Extract access token (requires jq)
ACCESS_TOKEN=$(echo $RESPONSE | jq -r '.access_token')
echo "Access token: $ACCESS_TOKEN"

# Test 4: Get user info
echo "\n4. Getting user info..."
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Test 5: List lessons
echo "\n5. Listing lessons..."
curl -X GET "http://localhost:8000/api/lessons?level=introduction"

# Test 6: Start lesson
echo "\n6. Starting lesson..."
curl -X POST "http://localhost:8000/api/lessons/start" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "introduction-staging-and-committing-files"
  }'

# Test 7: Complete lesson
echo "\n7. Completing lesson..."
curl -X POST "http://localhost:8000/api/lessons/complete" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "introduction-staging-and-committing-files",
    "time_spent_seconds": 300,
    "score": 85
  }'

# Test 8: Get stats
echo "\n8. Getting player stats..."
curl -X GET "http://localhost:8000/api/players/me/stats" \
  -H "Authorization: Bearer $ACCESS_TOKEN"

echo "\n✅ All tests complete!"
```

Save as `test_api.sh`, make executable (`chmod +x test_api.sh`), and run!

---

**Ready to test? Start with Step 1 and work through the steps!** 🚀
