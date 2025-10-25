@echo off
echo ============================================
echo  Executando Testes Automatizados
echo ============================================
echo.

echo Executando todos os testes...
pytest -v --tb=short

echo.
echo ============================================
echo  Testes Concluidos!
echo ============================================
echo.
echo Para ver cobertura detalhada:
echo   pytest --cov=. --cov-report=html
echo   (Abra htmlcov/index.html no navegador)
echo.
pause

