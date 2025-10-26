@echo off
chcp 65001 > nul
echo ========================================
echo 🔑 CRIAR ARQUIVO .ENV COM API KEY
echo ========================================
echo.

echo Criando arquivo .env...
echo.

(
echo # Football Data API Key
echo # Obtenha sua chave gratuita em: https://www.football-data.org/client/register
echo FOOTBALL_DATA_API_KEY=your_api_key_here
echo.
echo # The Odds API Key ^(para buscar odds do mercado^)
echo # Obtenha sua chave gratuita em: https://the-odds-api.com/
echo # Plano gratuito: 500 requisições/mês
echo ODDS_API_KEY=ae43b69e9ef7398ca4325da3891bc54b
) > .env

echo ✅ Arquivo .env criado com sucesso!
echo.
echo 📋 Conteúdo:
echo    - ODDS_API_KEY=ae43b69e9ef7398ca4325da3891bc54b
echo.
echo ========================================
echo ✅ CONFIGURAÇÃO CONCLUÍDA!
echo ========================================
echo.
echo Próximos passos:
echo   1. Execute: TESTAR_ODDS_API.bat
echo   2. Execute: COLETAR_ODDS_DIARIAS.bat
echo.
pause

