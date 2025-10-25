@echo off
chcp 65001 > nul
cls
echo ================================================================================
echo       COLETA DE DADOS - ESCOLHA A LIGA
echo ================================================================================
echo.
echo  Este script coleta dados de jogos das ligas suportadas
echo  Tempo estimado: 2-3 minutos por liga
echo.
echo ================================================================================
echo.
echo  Ligas disponiveis:
echo  1. Premier League (Inglaterra)
echo  2. Brasileirao Serie A (Brasil)
echo  3. Ambas as ligas
echo.
set /p choice="Escolha uma opcao (1-3): "

if "%choice%"=="3" (
    echo.
    echo Coletando TODAS as ligas...
    echo.
    python get_team_matches.py
) else if "%choice%"=="2" (
    echo.
    echo Coletando Brasileirao Serie A...
    echo.
    python get_brasileirao_data.py
) else (
    echo.
    echo Coletando Premier League...
    echo.
    python get_team_matches.py
)

echo.
echo.
echo ================================================================================
echo  COLETA CONCLUIDA
echo ================================================================================
echo.
echo  Dados salvos em: data\
echo.
echo  Proximos passos:
echo  1. Execute: INICIAR_SERVIDOR.bat
echo  2. Use a interface web para analisar apostas
echo  3. Selecione a liga no sidebar da interface
echo.
pause

