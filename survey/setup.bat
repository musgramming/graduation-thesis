@echo off

python -m venv .venv_survey

call .\.venv_survey\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

jupyter lab
