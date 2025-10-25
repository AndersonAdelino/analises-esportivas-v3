@echo off
chcp 65001 > nul
echo.
echo ================================================================================
echo    TESTE DO SISTEMA DE GERENCIAMENTO DE BANCA
echo ================================================================================
echo.
echo Este script irá testar todas as funcionalidades do sistema:
echo   - Configurar banca inicial
echo   - Registrar apostas
echo   - Finalizar apostas
echo   - Mostrar estatísticas
echo   - Evolução da banca
echo.
pause
echo.
echo Executando teste...
echo.
python test_bankroll_system.py
echo.
echo ================================================================================
echo                           TESTE CONCLUÍDO!
echo ================================================================================
echo.
echo Para usar o sistema completo:
echo    streamlit run app_betting.py
echo.
pause

