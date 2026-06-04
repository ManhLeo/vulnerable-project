@echo off
cd /d D:\TN\Vulnerable Project\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
