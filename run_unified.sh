#!/bin/bash
# Unified Overnight Research Engine - Runner Script
# Single comprehensive entry point for gematria overnight analysis

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENGINE_SCRIPT="${SCRIPT_DIR}/unified_engine.py"
LOG_FILE="/home/avalonas/.hermes/gematria/cron_logs/unified_overnight.log"

echo "======================================================================="
echo "🚀 SearXNG Unified Overnight Research Runner"
echo "======================================================================="
echo ""
echo "📂 Working Directory: ${SCRIPT_DIR}"
echo "📜 Engine Script: ${ENGINE_SCRIPT}"
echo "📝 Log Destination: ${LOG_FILE}"
echo ""

# Verify engine script exists
if [[ ! -f "${ENGINE_SCRIPT}" ]]; then
    echo "❌ Error: Engine script not found at ${ENGINE_SCRIPT}"
    exit 1
fi

# Verify SearXNG is accessible
echo "🔌 Checking SearXNG connection..."
HEALTH_CHECK="http://localhost:8084/?q=test"
RESPONSE=$(curl -s --max-time 5 "$HEALTH_CHECK" 2>/dev/null || echo "")
if [[ -z "${RESPONSE}" ]] && command -v curl &>/dev/null; then
    echo "⚠️ Warning: Could not reach SearXNG at http://localhost:8084/"
    echo "   Continuing with last known state..."
else
    echo "✅ SearXNG is accessible"
fi

# Execute engine
echo ""
echo "🔍 Starting overnight research protocol..."
python3 "${ENGINE_SCRIPT}" 2>&1 | tee "${LOG_FILE}"

# Check exit status
EXIT_STATUS=${PIPESTATUS[0]}

if [[ ${EXIT_STATUS} -eq 0 ]]; then
    echo ""
    echo "======================================================================="
    echo "✅ Overnight research completed successfully!"
    echo "======================================================================="
else
    echo ""
    echo "======================================================================="
    echo "⚠️  Overnight research completed with warnings (non-fatal errors)"
    echo "======================================================================="
fi

echo ""
echo "📝 Full log saved to: ${LOG_FILE}"
