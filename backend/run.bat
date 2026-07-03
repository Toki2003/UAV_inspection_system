@echo off
setlocal

if not exist .venv (
  python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8080
