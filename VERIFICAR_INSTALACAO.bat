@echo off
chcp 65001 > nul
cls
echo ================================================================================
echo       VERIFICACAO DE INSTALACAO
echo ================================================================================
echo.

echo [1/5] Verificando Python...
python --version
if errorlevel 1 (
    echo [X] Python NAO encontrado!
) else (
    echo [OK] Python instalado
)

echo.
echo [2/5] Verificando pip...
python -m pip --version
if errorlevel 1 (
    echo [X] pip NAO encontrado!
) else (
    echo [OK] pip instalado
)

echo.
echo [3/5] Verificando dependencias...
echo.
python -c "import requests; print('  [OK] requests')" 2>nul || echo   [X] requests NAO instalado
python -c "import pandas; print('  [OK] pandas')" 2>nul || echo   [X] pandas NAO instalado
python -c "import numpy; print('  [OK] numpy')" 2>nul || echo   [X] numpy NAO instalado
python -c "import scipy; print('  [OK] scipy')" 2>nul || echo   [X] scipy NAO instalado
python -c "import streamlit; print('  [OK] streamlit')" 2>nul || echo   [X] streamlit NAO instalado

echo.
echo [4/5] Verificando arquivos de dados...
if exist "data\all_teams_matches_*.csv" (
    echo [OK] Dados coletados encontrados
) else (
    echo [X] Dados NAO encontrados
    echo     Execute: python get_team_matches.py
)

echo.
echo [5/5] Verificando API Key...
if exist ".env" (
    echo [OK] Arquivo .env encontrado
) else (
    echo [X] Arquivo .env NAO encontrado
    echo     Crie o arquivo .env com sua API Key
)

echo.
echo ================================================================================
echo  VERIFICACAO CONCLUIDA
echo ================================================================================
echo.
echo  Se tudo estiver [OK], execute: INICIAR_SERVIDOR.bat
echo.
pause

