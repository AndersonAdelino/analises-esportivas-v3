@echo off
chcp 65001 > nul
cls
echo Iniciando Value Betting Analyzer...
echo.
python -m streamlit run app_betting.py
pause

