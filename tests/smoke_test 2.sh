#!/bin/bash
# ============================================================
# Smoke-тест для всех сервисов pay_servises
# Запуск: bash tests/smoke_test.sh
# ============================================================

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local name="$1"
    local expected_code="$2"
    local actual_code="$3"
    local body="$4"

    if [ "$actual_code" = "$expected_code" ]; then
        echo -e "${GREEN}✅ PASS${NC} [$actual_code] $name"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} [$actual_code] $name (expected $expected_code)"
        echo "   Response: ${body:0:200}"
        ((FAIL++))
    fi
}

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}  Smoke Test — $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# ============================================================
# AUTH SERVICE (8001)
# ============================================================
echo -e "${YELLOW}--- AUTH SERVICE ---${NC}"

# Health check
CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/docs)
check "Auth GET /docs" "200" "$CODE" ""

# Login (получаем токен админа)
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST http://localhost:8001/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"login": "admin", "password": "admin123"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Auth POST /api/v1/auth/login" "200" "$HTTP_CODE" "$BODY"

# Извлекаем access_token (если логин успешен)
TOKEN=$(echo "$BODY" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")
if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠️  Токен не получен, пропускаем авторизованные запросы${NC}"
fi


# ============================================================
# USERS SERVICE (8000)
# ============================================================
echo ""
echo -e "${YELLOW}--- USERS SERVICE ---${NC}"

CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/docs)
check "Users GET /docs" "200" "$CODE" ""

# Список пользователей (с токеном если есть)
if [ -n "$TOKEN" ]; then
    RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/accounts/users/ \
        -H "Authorization: Bearer $TOKEN")
else
    RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8000/accounts/users/)
fi
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Users GET /accounts/users/" "200" "$HTTP_CODE" "$BODY"


# ============================================================
# CONTRACTS SERVICE (8004)
# ============================================================
echo ""
echo -e "${YELLOW}--- CONTRACTS SERVICE ---${NC}"

CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8004/docs)
check "Contracts GET /docs" "200" "$CODE" ""

# --- Organisations ---
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/organisations/)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /organisations/" "200" "$HTTP_CODE" "$BODY"

# --- Services ---
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/services/)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /services/" "200" "$HTTP_CODE" "$BODY"

# --- Tariffs ---
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/tariffs/calculation-types)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /tariffs/calculation-types" "200" "$HTTP_CODE" "$BODY"

RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/tariffs/tariffs)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /tariffs/tariffs" "200" "$HTTP_CODE" "$BODY"

# --- Communications ---
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/communications/channels)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /communications/channels" "200" "$HTTP_CODE" "$BODY"

RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/communications/templates)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /communications/templates" "200" "$HTTP_CODE" "$BODY"

# --- Payments ---
RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/payments/merchants)
HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')
check "Contracts GET /payments/merchants" "200" "$HTTP_CODE" "$BODY"

# --- Contracts (раскомментировать когда CRUD будет готов) ---
# RESPONSE=$(curl -s -w "\n%{http_code}" http://localhost:8004/contracts/)
# HTTP_CODE=$(echo "$RESPONSE" | tail -1)
# BODY=$(echo "$RESPONSE" | sed '$d')
# check "Contracts GET /contracts/" "200" "$HTTP_CODE" "$BODY"


# ============================================================
# ALPHA_HOOK SERVICE (8003)
# ============================================================
echo ""
echo -e "${YELLOW}--- ALPHA_HOOK SERVICE ---${NC}"

CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/docs)
check "AlphaHook GET /docs" "200" "$CODE" ""


# ============================================================
# ИТОГ
# ============================================================
echo ""
echo -e "${YELLOW}========================================${NC}"
TOTAL=$((PASS + FAIL))
echo -e "Results: ${GREEN}$PASS passed${NC}, ${RED}$FAIL failed${NC} out of $TOTAL"
echo -e "${YELLOW}========================================${NC}"

[ "$FAIL" -eq 0 ] && exit 0 || exit 1