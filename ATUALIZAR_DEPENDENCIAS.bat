@echo off
echo ========================================
echo Atualizando Dependencias do Projeto
echo ========================================
echo.

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ========================================
echo Dependencias atualizadas com sucesso!
echo ========================================
echo.
pause

