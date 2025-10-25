@echo off
echo ========================================
echo Testando Nova Funcionalidade
echo ========================================
echo.
echo Este script vai:
echo 1. Instalar/Atualizar dependencias
echo 2. Iniciar o servidor Streamlit
echo.
echo ========================================
echo.

echo [1/2] Instalando dependencias...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt

echo.
echo [2/2] Iniciando servidor Streamlit...
echo.
echo ========================================
echo Interface disponivel em:
echo http://localhost:8501
echo ========================================
echo.
echo Dicas:
echo - Clique na aba "Analise de Times"
echo - Selecione um time para ver o historico
echo - Explore os graficos interativos
echo.
echo Pressione Ctrl+C para encerrar o servidor
echo ========================================
echo.

streamlit run app_betting.py

