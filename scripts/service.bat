cd C:\Users\kjero\Programming\HomeAutomation
.venv\scripts\python -m uvicorn mkhome:app^
 --host 0.0.0.0^
 --port 8582^
 --log-config config/logging.yaml^
 --log-level info
 