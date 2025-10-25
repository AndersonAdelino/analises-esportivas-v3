@echo off
echo ============================================
echo  Instalando Dependencias de Teste
echo ============================================
echo.

echo Atualizando pip...
python -m pip install --upgrade pip

echo.
echo Instalando dependencias de teste...
pip install pytest pytest-cov pytest-mock

echo.
echo ============================================
echo  Instalacao Concluida!
echo ============================================
echo.
echo Para executar os testes, use:
echo   pytest
echo   pytest -v (verbose)
echo   pytest --cov (com cobertura)
echo.
pause

