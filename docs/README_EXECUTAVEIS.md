# 🚀 Guia Rápido - Executáveis Windows

## 📋 Arquivos Disponíveis

### 🎯 Principal
**`INICIAR_SERVIDOR.bat`** - Inicia o servidor Streamlit
- Verifica instalação
- Inicia interface web
- Abre navegador automaticamente

### ⚡ Alternativo
**`INICIAR_SERVIDOR_SIMPLES.bat`** - Versão simplificada
- Inicia direto sem verificações
- Mais rápido

---

## 🔧 Utilitários

**`VERIFICAR_INSTALACAO.bat`** - Verifica se tudo está OK
- Checa Python
- Checa dependências
- Checa dados
- Checa API Key

**`INSTALAR_DEPENDENCIAS.bat`** - Instala todas as dependências
- Atualiza pip
- Instala requirements.txt

**`COLETAR_DADOS.bat`** - Coleta dados da Premier League
- Busca últimas 20 partidas de cada time
- Salva em data/

---

## 🚀 Primeiro Uso (Setup Completo)

### 1️⃣ Instalar Dependências
```
Duplo clique: INSTALAR_DEPENDENCIAS.bat
Aguarde instalação (~2-3 minutos)
```

### 2️⃣ Configurar API Key
```
Crie arquivo .env com:
FOOTBALL_DATA_API_KEY=sua_chave_aqui
```

### 3️⃣ Coletar Dados
```
Duplo clique: COLETAR_DADOS.bat
Aguarde coleta (~2-3 minutos)
```

### 4️⃣ Iniciar Servidor
```
Duplo clique: INICIAR_SERVIDOR.bat
Aguarde abertura do navegador
```

---

## 🎯 Uso Diário (Após Setup)

### Para usar o sistema:
```
1. Duplo clique: INICIAR_SERVIDOR.bat
2. Aguarde navegador abrir (~10 seg)
3. Use a interface!
4. Feche a janela quando terminar
```

---

## 🔄 Atualizar Dados (Semanal)

### Após rodada da Premier League:
```
1. Duplo clique: COLETAR_DADOS.bat
2. Aguarde coleta
3. Duplo clique: INICIAR_SERVIDOR.bat
4. Modelos treinarão com dados novos!
```

---

## 🛠️ Troubleshooting

### Erro: "Python não encontrado"
**Solução:** Instale Python 3.8+ de https://python.org

### Erro: "streamlit não encontrado"
**Solução:** Execute `INSTALAR_DEPENDENCIAS.bat`

### Erro: "Nenhum arquivo encontrado"
**Solução:** Execute `COLETAR_DADOS.bat`

### Erro: "API Key inválida"
**Solução:** Verifique arquivo `.env` com sua chave

---

## ⚙️ Verificar Tudo

Antes de usar, verifique:
```
Duplo clique: VERIFICAR_INSTALACAO.bat

Deve mostrar tudo [OK]
```

---

## 🖥️ O Que Acontece ao Clicar

### `INICIAR_SERVIDOR.bat`
```
1. Verifica Python instalado
2. Verifica Streamlit instalado
3. Inicia servidor Streamlit
4. Abre http://localhost:8501
5. Carrega modelos (~10 seg)
6. Interface pronta!
```

### Para Parar
- Feche a janela preta (terminal)
- Ou pressione `Ctrl + C` na janela

---

## 📝 Notas Importantes

### Arquivos .bat
- ✅ Seguros de executar
- ✅ Apenas iniciam scripts Python
- ✅ Podem ser editados em Bloco de Notas
- ✅ Específicos para Windows

### Primeira Execução
- ⏱️ Modelos levam ~10-15 segundos para treinar
- 🔄 Cache é usado nas próximas vezes (mais rápido)
- 💾 Dados permanecem salvos

### Performance
- 🚀 Segunda execução é mais rápida
- 💻 Usa ~500MB de RAM
- 🌐 Navegador fica leve

---

## 🎓 Dicas

### Para Criar Atalho na Área de Trabalho
1. Botão direito em `INICIAR_SERVIDOR.bat`
2. "Enviar para" → "Área de trabalho (criar atalho)"
3. Renomeie para "Value Betting"
4. Duplo clique quando quiser usar!

### Para Auto-Abrir ao Iniciar Windows
1. Pressione `Win + R`
2. Digite: `shell:startup`
3. Cole atalho de `INICIAR_SERVIDOR.bat` na pasta
4. ⚠️ Servidor iniciará automaticamente ao ligar PC

---

## ✅ Checklist de Uso

Antes de fazer análises:
- [ ] Python instalado
- [ ] Dependências instaladas (`INSTALAR_DEPENDENCIAS.bat`)
- [ ] API Key configurada (`.env`)
- [ ] Dados coletados (`COLETAR_DADOS.bat`)
- [ ] Servidor iniciado (`INICIAR_SERVIDOR.bat`)
- [ ] Navegador aberto em localhost:8501
- [ ] Interface carregada

---

## 🆘 Ajuda

Se precisar de ajuda:
1. Execute `VERIFICAR_INSTALACAO.bat`
2. Veja o que está [X] (não OK)
3. Siga as instruções mostradas
4. Consulte `GUIA_VALUE_BETTING.md`

---

**Criado para facilitar sua vida! 🎯**

*Última atualização: Outubro 2024*

