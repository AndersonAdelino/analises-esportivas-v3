@echo off
chcp 65001 > nul
echo ========================================
echo 💰 MODO ECONÔMICO - THE ODDS API
echo ========================================
echo.
echo Este modo economiza até 83%% das requisições!
echo.
echo Configuração:
echo   - Casa única: Pinnacle
echo   - Região: Europa (eu)
echo   - Mercado: 1X2 (h2h)
echo   - Cache: 12 horas
echo.
pause
echo.

python odds_economico.py

echo.
echo ========================================
echo ✅ TESTE CONCLUÍDO
echo ========================================
echo.
echo Para alterar a configuração, edite: config_economia.py
echo.
pause

