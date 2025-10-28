@echo off
echo Teste Matematico - Validacao Completa
echo ======================================
echo.
python test_final_matematico.py > resultado_matematico.txt 2>&1
type resultado_matematico.txt
echo.
echo Resultado salvo em resultado_matematico.txt

