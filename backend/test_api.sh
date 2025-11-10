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

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo "❌ Failed to get authentication token. Stopping."
  exit 1
fi

echo -e "\n👤 4. Get My Profile"
curl -s $BASE_URL/api/players/me \
  -H "Authorization: Bearer $TOKEN" | jq

echo -e "\n📚 5. Get All Lessons"
LESSONS=$(curl -s $BASE_URL/api/lessons)
echo $LESSONS | jq '.[0]'

LESSON_ID=$(echo $LESSONS | jq -r '.[0].id')
echo "First lesson ID: $LESSON_ID"

if [ "$LESSON_ID" == "null" ] || [ -z "$LESSON_ID" ]; then
  echo "⚠️  No lessons found. Continuing with sandbox test without lesson_id..."
  LESSON_ID=""
fi

echo -e "\n🏗️ 6. Create Sandbox"
if [ -z "$LESSON_ID" ]; then
  SANDBOX_RESPONSE=$(curl -s -X POST $BASE_URL/api/sandbox/create \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{}')
else
  SANDBOX_RESPONSE=$(curl -s -X POST $BASE_URL/api/sandbox/create \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"lesson_id\": \"$LESSON_ID\"}")
fi

echo $SANDBOX_RESPONSE | jq

SANDBOX_ID=$(echo $SANDBOX_RESPONSE | jq -r '.sandbox_id')
echo "Sandbox ID: $SANDBOX_ID"

if [ "$SANDBOX_ID" != "null" ] && [ ! -z "$SANDBOX_ID" ]; then
  echo -e "\n✅ Sandbox created successfully! Testing commands...\n"

  echo "🚀 7. Execute: pwd"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "pwd"}' | jq

  echo -e "\n🚀 8. Execute: git --version"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git --version"}' | jq

  echo -e "\n🚀 9. Execute: ls -la"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "ls -la"}' | jq

  echo -e "\n🚀 10. Execute: git status"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git status"}' | jq

  echo -e "\n🚀 11. Execute: git init"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git init"}' | jq

  echo -e "\n🚀 12. Execute: git status (after init)"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/execute \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"command": "git status"}' | jq

  echo -e "\n📊 13. Get Sandbox Status"
  curl -s $BASE_URL/api/sandbox/$SANDBOX_ID/status \
    -H "Authorization: Bearer $TOKEN" | jq

  echo -e "\n🧹 14. Cleanup Sandbox"
  curl -s -X POST $BASE_URL/api/sandbox/$SANDBOX_ID/cleanup \
    -H "Authorization: Bearer $TOKEN" | jq
else
  echo "❌ Failed to create sandbox. Check the error message above."
  echo "Possible issues:"
  echo "  1. GitPython not installed: pip install GitPython"
  echo "  2. Backend not running or database connection failed"
  echo "  3. Check backend logs for detailed error"
fi

echo -e "\n✅ Testing Complete!"
