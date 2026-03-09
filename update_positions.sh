#!/bin/bash
# Quick script to update positions from CSV and restart BLOOMY

set -e

echo "📊 Actualizando posiciones desde CSV..."
python3 scripts/generate_positions.py

echo ""
echo "🔄 Reiniciando BLOOMY..."
launchctl kickstart -k gui/$(id -u)/com.jballesteros.bloomy

echo ""
echo "✅ Listo! Dashboard actualizado: http://127.0.0.1:8050"
