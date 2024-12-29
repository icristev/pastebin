#!/bin/bash

API_URL="http://127.0.0.1:8000/api/create"
CONTENT_TYPE="Content-Type: application/json"

for i in $(seq 1 20000); do
  echo "Отправка запроса №$i..."
  curl -X POST "$API_URL" \
       -H "$CONTENT_TYPE" \
       -d "{
            \"content\": \"Текст $i\",
            \"expires_in\": 3600
           }"
  echo ""
done
