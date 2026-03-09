#!/bin/bash
# BLOOMY - Status checker

echo "🥑 BLOOMY Dashboard Status"
echo "=========================="

# Check launchd service
SERVICE_STATUS=$(launchctl list | grep bloomy)
if [ -n "$SERVICE_STATUS" ]; then
    PID=$(echo "$SERVICE_STATUS" | awk '{print $1}')
    echo "✅ Servicio activo (PID: $PID)"
else
    echo "❌ Servicio NO está corriendo"
    exit 1
fi

# Check HTTP endpoint
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8050)
if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Dashboard respondiendo en http://127.0.0.1:8050"
else
    echo "❌ Dashboard NO responde (HTTP: $HTTP_CODE)"
    exit 1
fi

# Check logs
if [ -f ~/Library/Logs/bloomy.log ]; then
    LAST_LOG=$(tail -1 ~/Library/Logs/bloomy.log)
    echo "📋 Último log: $LAST_LOG"
else
    echo "⚠️  Log file no encontrado"
fi

echo ""
echo "🎯 Todo operativo - Dashboard online"
