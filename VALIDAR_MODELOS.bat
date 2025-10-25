@echo off
echo ============================================
echo  Validando Modelos Preditivos
echo ============================================
echo.

echo Iniciando validacao e backtesting...
echo (Isso pode demorar alguns minutos)
echo.

python validation.py

echo.
echo ============================================
echo  Validacao Concluida!
echo ============================================
echo.
echo Resultados salvos em: data/validation/
echo.
pause

