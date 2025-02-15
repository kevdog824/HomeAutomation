.venv\scripts\python -m uvicorn mkhome:app^
 --reload^
 --reload-include "*.yaml"^
 --host 0.0.0.0^
 --port 8582^
 --log-config config/logging.yaml^
 --log-level info
 