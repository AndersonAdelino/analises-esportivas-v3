@echo off
chcp 65001 > nul
cls
echo ================================================================================
echo       VALUE BETTING ANALYZER - INICIANDO SERVIDOR
echo ================================================================================
echo.
echo [1/3] Verificando ambiente...
python --version
if errorlevel 1 (
    echo.
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python 3.8+ primeiro.
    pause
    exit /b 1
)

echo.
echo [2/3] Verificando Streamlit...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo.
    echo [AVISO] Streamlit nao encontrado. Instalando...
    python -m pip install streamlit
)

echo.
echo [3/3] Iniciando servidor...
echo.
echo ================================================================================
echo  SERVIDOR STREAMLIT INICIANDO...
echo ================================================================================
echo.
echo  O navegador abrira automaticamente em: http://localhost:8501
echo.
echo  Aguarde o carregamento dos modelos (~10-15 segundos)
echo.
echo  Para PARAR o servidor: Feche esta janela ou pressione Ctrl+C
echo.
echo ================================================================================
echo.

python -m streamlit run app_betting.py

echo.
echo.
echo ================================================================================
echo  SERVIDOR ENCERRADO
echo ================================================================================
echo.
pause

