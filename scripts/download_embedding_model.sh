#!/usr/bin/env bash
set -euo pipefail

# Download local SentenceTransformer model directory so the backend can run offline.
# Target example:
#   models/paraphrase-multilingual-MiniLM-L12-v2

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST_DIR="${DEST_DIR:-$ROOT_DIR/models/paraphrase-multilingual-MiniLM-L12-v2}"
REPO_ID="${REPO_ID:-sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2}"

mkdir -p "$ROOT_DIR/models"

echo "==== Download embedding model ===="
echo "Repo : $REPO_ID"
echo "Dest : $DEST_DIR"

cd "$ROOT_DIR/backend"
if [[ ! -d ".venv" ]]; then
  echo "backend/.venv 不存在，请先运行 ./scripts/setup.sh"
  exit 1
fi

source ".venv/bin/activate"

# Put HF cache into project folder for easier cleanup.
export HF_HOME="$ROOT_DIR/.hf_cache"

# Ensure huggingface_hub exists in venv
python - <<'PY'
import importlib, sys
try:
    importlib.import_module("huggingface_hub")
except Exception:
    sys.exit(1)
sys.exit(0)
PY
if [[ $? -ne 0 ]]; then
  pip install -U huggingface_hub
fi

python - <<'PY'
from huggingface_hub import snapshot_download
import os

repo_id = os.environ["REPO_ID"]
local_dir = os.environ["DEST_DIR"]

path = snapshot_download(
  repo_id=repo_id,
  local_dir=local_dir,
  local_dir_use_symlinks=False,
  resume_download=True,
)
print("Downloaded to:", path)
PY

echo "Done. Next: set EMBEDDING_MODEL_PATH in backend/.env"

