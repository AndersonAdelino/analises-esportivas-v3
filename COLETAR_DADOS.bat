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
echo  3. La Liga (Espanha)
echo  4. Serie A (Italia)
echo  5. Primeira Liga (Portugal)
echo  6. Todas as ligas
echo.
set /p choice="Escolha uma opcao (1-6): "

if "%choice%"=="6" (
    echo.
    echo Coletando TODAS as ligas...
    echo.
    echo Escolha opcao 6 no menu do Python
    python get_team_matches.py
) else if "%choice%"=="5" (
    echo.
    echo Coletando Primeira Liga (Portugal)...
    echo.
    echo Escolha opcao 5 no menu do Python
    python get_team_matches.py
) else if "%choice%"=="4" (
    echo.
    echo Coletando Serie A (Italia)...
    echo.
    echo Escolha opcao 4 no menu do Python
    python get_team_matches.py
) else if "%choice%"=="3" (
    echo.
    echo Coletando La Liga (Espanha)...
    echo.
    echo Escolha opcao 3 no menu do Python
    python get_team_matches.py
) else if "%choice%"=="2" (
    echo.
    echo Coletando Brasileirao Serie A...
    echo.
    echo Escolha opcao 2 no menu do Python
    python get_team_matches.py
) else (
    echo.
    echo Coletando Premier League...
    echo.
    echo Escolha opcao 1 no menu do Python
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

