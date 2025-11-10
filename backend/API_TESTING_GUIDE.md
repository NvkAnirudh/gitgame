# Git Quest API Testing Guide

Complete guide to test all backend API endpoints.

## Prerequisites

1. **Backend Running**:
   ```bash
   cd /home/user/gitgame/backend
   python -m uvicorn app.main:app --reload --port 8000
   ```

2. **Database Running**: PostgreSQL should be running with the git_quest_db database

3. **Tool**: Use `curl` or any API client (Postman, Insomnia, etc.)

---

## Testing Workflow

### 1. Health Check (No Auth Required)

**Check API is running**:
```bash
curl http://localhost:8000/health
```

Expected: `{"status":"healthy","service":"git-quest-api","version":"1.0.0"}`

**Check Sandbox Health**:
```bash
curl http://localhost:8000/api/sandbox/health
```

Expected: Should show `"status":"healthy"` with GitPython installed and test sandbox working.

---

### 2. Authentication Endpoints

#### Register New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testplayer",
    "email": "test@gitquest.com",
    "password": "TestPass123!"
  }'
```

Expected Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

**Save the access_token** - you'll need it for authenticated requests!

#### Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testplayer&password=TestPass123!"
```

Expected: Same token response as registration.

#### Refresh Token

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

---

### 3. Player Endpoints (Requires Auth)

**Set your token** (use the access_token from registration/login):
```bash
export TOKEN="YOUR_ACCESS_TOKEN_HERE"
```

#### Get My Profile

```bash
curl http://localhost:8000/api/players/me \
  -H "Authorization: Bearer $TOKEN"
```

Expected:
```json
{
  "id": "...",
  "user_id": "...",
  "username": "testplayer",
  "email": "test@gitquest.com",
  "level": 1,
  "total_xp": 0,
  "current_streak": 0
}
```

#### Get My Stats

```bash
curl http://localhost:8000/api/players/me/stats \
  -H "Authorization: Bearer $TOKEN"
```

---

### 4. Lessons Endpoints

#### Get All Lessons (No Auth)

```bash
curl http://localhost:8000/api/lessons
```

Expected: Array of lessons.

#### Get Lessons by Level

```bash
curl "http://localhost:8000/api/lessons?level=introduction"
```

#### Get Single Lesson

First, get a lesson ID from the list above, then:

```bash
curl http://localhost:8000/api/lessons/LESSON_ID
```

#### Start a Lesson (Requires Auth)

```bash
curl -X POST http://localhost:8000/api/lessons/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "LESSON_ID"
  }'
```

#### Complete a Lesson (Requires Auth)

```bash
curl -X POST http://localhost:8000/api/lessons/complete \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "LESSON_ID",
    "time_spent_seconds": 300,
    "xp_earned": 100
  }'
```

#### Get My Progress (Requires Auth)

```bash
curl http://localhost:8000/api/players/me/progress \
  -H "Authorization: Bearer $TOKEN"
```

---

### 5. Challenges Endpoints

#### Get All Challenges (No Auth)

```bash
curl http://localhost:8000/api/challenges
```

#### Get Challenges for a Lesson

```bash
curl "http://localhost:8000/api/challenges?lesson_id=LESSON_ID"
```

#### Get Single Challenge

```bash
curl http://localhost:8000/api/challenges/CHALLENGE_ID
```

#### Start a Challenge (Requires Auth)

```bash
curl -X POST http://localhost:8000/api/challenges/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "challenge_id": "CHALLENGE_ID"
  }'
```

Expected: Returns attempt_id and sandbox information.

#### Submit Challenge Solution (Requires Auth)

```bash
curl -X POST http://localhost:8000/api/challenges/CHALLENGE_ID/submit \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "commands_used": ["git init", "git status"],
    "time_spent_seconds": 120
  }'
```

Expected: Shows success, score, and feedback.

#### Get My Attempts (Requires Auth)

```bash
curl http://localhost:8000/api/challenges/CHALLENGE_ID/attempts \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Leaderboard

```bash
curl http://localhost:8000/api/challenges/leaderboard?limit=10
```

#### Get Challenge Stats

```bash
curl http://localhost:8000/api/challenges/stats
```

---

### 6. Game Sessions Endpoints (Requires Auth)

#### Start a Session

```bash
curl -X POST http://localhost:8000/api/sessions/start \
  -H "Authorization: Bearer $TOKEN"
```

Expected: Returns session_id.

**Save the session_id** for next requests!

#### Get Current Session

```bash
curl http://localhost:8000/api/sessions/current \
  -H "Authorization: Bearer $TOKEN"
```

#### End a Session

```bash
curl -X POST http://localhost:8000/api/sessions/end \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "SESSION_ID"
  }'
```

#### Get Session History

```bash
curl "http://localhost:8000/api/sessions/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get My Session Stats

```bash
curl http://localhost:8000/api/sessions/stats/me \
  -H "Authorization: Bearer $TOKEN"
```

---

### 7. Story Endpoints

#### Get All Characters (No Auth)

```bash
curl http://localhost:8000/api/story/characters
```

Expected: Array of mentors (Alex, Sam, Jordan).

#### Get All Story Arcs (Requires Auth)

```bash
curl http://localhost:8000/api/story/arcs \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Single Story Arc

```bash
curl http://localhost:8000/api/story/arcs/ARC_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### Get My Story Progress

```bash
curl http://localhost:8000/api/story/progress \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Story Context

```bash
curl http://localhost:8000/api/story/context \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Mentor Tip for Lesson

```bash
curl "http://localhost:8000/api/story/mentor-tip?lesson_id=LESSON_ID" \
  -H "Authorization: Bearer $TOKEN"
```

---

### 8. Sandbox Endpoints (Requires Auth) ⚠️ MOST IMPORTANT

#### Create a Sandbox

```bash
curl -X POST http://localhost:8000/api/sandbox/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "lesson_id": "LESSON_ID"
  }'
```

Expected Response:
```json
{
  "sandbox_id": "abc123...",
  "initialized": true,
  "message": "Sandbox created successfully"
}
```

**Save the sandbox_id** for executing commands!

#### Execute Command in Sandbox

```bash
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "pwd"
  }'
```

Expected Response:
```json
{
  "output": "/tmp/gitquest_sandboxes/abc123...",
  "success": true,
  "execution_time_ms": 15.2
}
```

**Test Git Commands**:

```bash
# Test git --version
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "git --version"}'

# Test ls
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "ls"}'

# Test git status
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "git status"}'

# Test git init
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/execute \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"command": "git init"}'
```

#### Get Sandbox Status

```bash
curl http://localhost:8000/api/sandbox/SANDBOX_ID/status \
  -H "Authorization: Bearer $TOKEN"
```

#### Cleanup Sandbox

```bash
curl -X POST http://localhost:8000/api/sandbox/SANDBOX_ID/cleanup \
  -H "Authorization: Bearer $TOKEN"
```

---

## Quick Test Script

Save this as `test_api.sh`:

```bash
#!/bin/bash

BASE_URL="http://localhost:8000"

echo "🔍 1. Health Check"
curl -s $BASE_URL/health | jq

echo -e "\n🔍 2. Sandbox Health Check"
curl -s $BASE_URL/api/sandbox/health | jq

echo -e "\n🔐 3. Register User"
REGISTER_RESPONSE=$(curl -s -X POST $BASE_URL/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser_'$(date +%s)'",
    "email": "test'$(date +%s)'@example.com",
    "password": "Test123!@#"
  }')

echo $REGISTER_RESPONSE | jq

TOKEN=$(echo $REGISTER_RESPONSE | jq -r '.access_token')
echo "Token: $TOKEN"

echo -e "\n👤 4. Get My Profile"
curl -s $BASE_URL/api/players/me \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n📚 5. Get All Lessons"
LESSONS=$(curl -s $BASE_URL/api/lessons)
echo $LESSONS | jq '.[0]'

LESSON_ID=$(echo $LESSONS | jq -r '.[0].id')
echo "First lesson ID: $LESSON_ID"

echo -e "\n🏗️ 6. Create Sandbox"
SANDBOX_RESPONSE=$(curl -s -X POST $BASE_URL/api/sandbox/create \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"lesson_id\": \"$LESSON_ID\"}")

echo $SANDBOX_RESPONSE | jq

SANDBOX_ID=$(echo $SANDBOX_RESPONSE | jq -r '.sandbox_id')
echo "Sandbox ID: $SANDBOX_ID"

if [ "$SANDBOX_ID" != "null" ]; then
  echo -e "\n🚀 7. Execute: pwd"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "pwd"}' | jq

  echo -e "\n🚀 8. Execute: git --version"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git --version"}' | jq

  echo -e "\n🚀 9. Execute: ls"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "ls"}' | jq

  echo -e "\n🚀 10. Execute: git status"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git status"}' | jq

  echo -e "\n🧹 11. Cleanup Sandbox"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/cleanup \
    -H "Authorization: Bearer $TOKEN" | jq
else
  echo "❌ Failed to create sandbox"
fi

echo -e "\n✅ Testing Complete!"
```

Make it executable and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Common Issues & Troubleshooting

### 1. 401 Unauthorized
- Token missing or expired
- Use the `Authorization: Bearer $TOKEN` header
- Re-login to get a new token

### 2. 404 Not Found
- Check the endpoint URL
- Verify the ID exists (lesson_id, challenge_id, etc.)

### 3. 500 Internal Server Error
- Check backend logs
- Database might not be running
- Missing dependencies (pip install GitPython)

### 4. Sandbox Health Shows "unhealthy"
- Install GitPython: `pip install GitPython`
- Check temp directory permissions
- Check backend logs for specific error

### 5. Commands Not Executing
- Verify sandbox was created successfully
- Check sandbox_id is valid
- Ensure token is correct
- Check backend logs for command execution errors

---

## Expected Logs (Backend)

When testing sandbox, you should see:

```
INFO: Creating sandbox for player: abc123, lesson: lesson_id, challenge: None
INFO: Sandbox created successfully: def456
INFO: Executing command: pwd in sandbox: def456
INFO: Command executed - Success: True, Stdout length: 35, Stderr length: 0
```

If you see errors, they'll point to the exact issue!
