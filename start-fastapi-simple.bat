@echo off
cd /d e:\erick\Documents\Personal\UTadeo\IEEE\Proyectos\Ticket
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8010 --reload
