#!/usr/bin/env bash
"""
Run vision-integrated drone mission on the GCP VM.
"""

set -euo pipefail

# Load environment
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

: "${GCP_PROJECT:?Set GCP_PROJECT}"
: "${GCP_ZONE:?Set GCP_ZONE}" 
: "${GPU_VM_NAME:?Set GPU_VM_NAME}"

# Parse arguments
VISION_ENABLED=${1:-0}
OUTPUT_DIR=${2:-""}

if [ "$VISION_ENABLED" = "1" ]; then
    echo "🎯 Running mission with VISION ENABLED"
    if [ -z "$OUTPUT_DIR" ]; then
        OUTPUT_DIR="~/runs/$(date +%F_%H%M%S)"
    fi
    echo "   Frames will be saved to: $OUTPUT_DIR"
else
    echo "🚁 Running mission with vision DISABLED"
fi

echo "   Target VM: ${GPU_VM_NAME}"
echo ""

# Run mission on VM
gcloud compute ssh ${GPU_VM_NAME} --zone=${GCP_ZONE} --command "
    export AIRSIM_HOST=127.0.0.1
    export AIRSIM_PORT=41451
    export VISION=${VISION_ENABLED}
    export OUTPUT_DIR='${OUTPUT_DIR}'
    
    echo '🚁 Starting drone mission...'
    cd ~
    python3 src/main.py
"

echo ""
echo "✅ Mission completed!"

if [ "$VISION_ENABLED" = "1" ] && [ -n "$OUTPUT_DIR" ]; then
    echo ""
    echo "📸 To download captured frames:"
    echo "   gcloud compute scp --recurse ${GPU_VM_NAME}:${OUTPUT_DIR} ./downloaded_frames/ --zone=${GCP_ZONE}"
fi
