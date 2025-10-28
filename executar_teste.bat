@echo off
echo Executando teste de validacao...
python -u test_validacao_final.py > resultado_teste.txt 2>&1
type resultado_teste.txt
echo.
echo Teste concluido. Resultado salvo em resultado_teste.txt

