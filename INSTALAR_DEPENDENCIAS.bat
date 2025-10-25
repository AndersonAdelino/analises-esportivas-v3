@echo off
chcp 65001 > nul
cls
echo ================================================================================
echo       INSTALACAO DE DEPENDENCIAS
echo ================================================================================
echo.
echo  Instalando todas as dependencias necessarias...
echo.
echo ================================================================================
echo.

python -m pip install --upgrade pip

echo.
echo Instalando pacotes...
echo.

python -m pip install -r requirements.txt

echo.
echo.
echo ================================================================================
echo  INSTALACAO CONCLUIDA
echo ================================================================================
echo.
echo  Proximos passos:
echo  1. Configure sua API Key no arquivo .env
echo  2. Execute: COLETAR_DADOS.bat
echo  3. Execute: INICIAR_SERVIDOR.bat
echo.
pause

