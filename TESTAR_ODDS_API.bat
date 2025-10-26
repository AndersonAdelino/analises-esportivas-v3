@echo off
chcp 65001 > nul
echo ========================================
echo 🧪 TESTAR THE ODDS API
echo ========================================
echo.
echo Certifique-se de ter configurado sua API Key em:
echo   - Arquivo .env (ODDS_API_KEY=sua_key)
echo   - OU no arquivo test_odds_api.py (linha 23)
echo.
pause
echo.

python test_odds_api.py

echo.
echo ========================================
echo ✅ TESTE CONCLUÍDO
echo ========================================
echo.
pause

