# 🚀 Deploy no Streamlit Cloud - Guia Completo

## 📋 Pré-requisitos

Antes de começar, você precisa:

1. ✅ **Conta no GitHub** (gratuita)
2. ✅ **Repositório Git** com o projeto
3. ✅ **API Key do Football-Data.org** ([Obtenha aqui](https://www.football-data.org/client/register))
4. ✅ **Conta no Streamlit Cloud** (gratuita - [share.streamlit.io](https://share.streamlit.io))

---

## 🎯 Passo 1: Preparar o Repositório

### 1.1 Inicializar Git (se ainda não fez)

```bash
cd C:\Users\Anderson\Documents\analises_esportivas_v3
git init
```

### 1.2 Criar/Atualizar .gitignore

O arquivo `.gitignore` já está configurado! Ele garante que:
- ❌ `.env` não será commitado (segurança!)
- ❌ `__pycache__` não será incluído
- ❌ Arquivos de dados CSV/JSON não vão pro GitHub

### 1.3 Fazer primeiro commit

```bash
git add .
git commit -m "Projeto de análise de apostas esportivas com Bingo"
```

### 1.4 Criar repositório no GitHub

1. Acesse [github.com](https://github.com) e faça login
2. Clique no **"+"** no canto superior direito
3. Selecione **"New repository"**
4. Preencha:
   - **Repository name**: `analises-esportivas-v3`
   - **Description**: "Sistema de análise de apostas esportivas com modelos preditivos e apostas múltiplas"
   - **Visibility**: Public (necessário para Streamlit Cloud gratuito)
5. **NÃO** marque "Initialize with README" (já temos)
6. Clique em **"Create repository"**

### 1.5 Enviar código para o GitHub

```bash
git remote add origin https://github.com/SEU_USUARIO/analises-esportivas-v3.git
git branch -M main
git push -u origin main
```

> **Nota:** Substitua `SEU_USUARIO` pelo seu username do GitHub

---

## 🌟 Passo 2: Deploy no Streamlit Cloud

### 2.1 Criar conta no Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **"Sign up"**
3. Conecte com sua conta do **GitHub**
4. Autorize o Streamlit a acessar seus repositórios

### 2.2 Criar novo App

1. No painel do Streamlit Cloud, clique em **"New app"**
2. Preencha os campos:

   **Repository:**
   - Selecione seu repositório: `SEU_USUARIO/analises-esportivas-v3`

   **Branch:**
   - `main`

   **Main file path:**
   - `app_betting.py`

   **App URL (opcional):**
   - Personalize a URL: `seu-nome-analises-esportivas`
   - URL final será: `seu-nome-analises-esportivas.streamlit.app`

3. Clique em **"Deploy!"**

### 2.3 Configurar Secrets (API Key)

**⚠️ IMPORTANTE:** O app vai falhar na primeira vez porque precisa da API Key!

1. No painel do app, clique em **"Settings"** (⚙️)
2. Vá em **"Secrets"**
3. Cole o seguinte conteúdo:

```toml
# Secrets do Streamlit Cloud
FOOTBALL_DATA_API_KEY = "SUA_CHAVE_API_AQUI"
```

4. Substitua `SUA_CHAVE_API_AQUI` pela sua chave real
5. Clique em **"Save"**
6. O app será **automaticamente redeploy**

### 2.4 Aguardar Deploy

- ⏳ Primeira vez: **2-5 minutos**
- 🔄 Deploys seguintes: **30-60 segundos**
- 📺 Acompanhe o log em tempo real na interface

---

## ✅ Passo 3: Verificar Deploy

### 3.1 Acessar o App

Quando o deploy terminar:
1. Clique no link do app: `https://seu-nome-analises-esportivas.streamlit.app`
2. O app deve abrir normalmente!

### 3.2 Testar Funcionalidades

Teste cada aba:
- ✅ **Análise de Apostas** - Deve carregar próximas partidas
- ✅ **Análise de Times** - Deve buscar histórico dos times
- ✅ **Bingo** - Deve funcionar após fazer análises

### 3.3 Verificar Logs

Se algo não funcionar:
1. Volte ao painel do Streamlit Cloud
2. Clique no app
3. Veja os **logs** na parte inferior
4. Procure por erros em vermelho

---

## 🔧 Configurações Avançadas

### Alterar Configurações do App

No Streamlit Cloud, vá em **Settings**:

**General:**
- App URL: Mude a URL se quiser
- Python version: 3.9+ (padrão)

**Secrets:**
- Configure variáveis de ambiente sensíveis
- `FOOTBALL_DATA_API_KEY` = sua chave

**Advanced settings:**
- Sempre use as versões mais recentes das dependências

---

## 🔄 Atualizações Automáticas

### Como funciona:

1. Você faz alterações no código localmente
2. Commita e faz push para o GitHub:
   ```bash
   git add .
   git commit -m "Descrição da mudança"
   git push
   ```
3. **Streamlit Cloud detecta automaticamente**
4. **Faz redeploy em ~30 segundos**
5. App é atualizado automaticamente! 🎉

### Forçar Reboot:

Se o app travar:
1. No painel, clique nos **"..."** do app
2. Selecione **"Reboot"**
3. Aguarde reiniciar

---

## 📊 Monitoramento

### Analytics

No painel do Streamlit Cloud, você pode ver:
- 📈 **Número de visitantes**
- ⏱️ **Tempo de atividade (uptime)**
- 💾 **Uso de recursos**
- 🔄 **Histórico de deploys**

### Logs em Tempo Real

- Clique no app no painel
- Veja logs ao vivo na parte inferior
- Útil para debugar problemas

---

## ⚠️ Limitações do Plano Gratuito

### Recursos do Plano Free:

- ✅ **1 app privado** OU **apps públicos ilimitados**
- ✅ **1 GB de RAM** por app
- ✅ **1 CPU** por app
- ✅ **Dormência** após inatividade (acorda ao acessar)
- ✅ **SSL/HTTPS** automático
- ✅ **Deploy ilimitados**

### Dormência (Sleep):

- App **dorme** após **7 dias** sem acessos
- **Acorda automaticamente** quando alguém acessa
- Tempo de wake-up: **~10 segundos**

### Para evitar dormência:

Use um serviço de ping (opcional):
- [UptimeRobot](https://uptimerobot.com) - Ping gratuito a cada 5 minutos
- [Cron-job.org](https://cron-job.org) - Agendamento de requisições

---

## 🆙 Upgrade para Plano Pago (Opcional)

Se precisar de mais recursos:

**Streamlit Cloud Pro:**
- 💰 **$20/mês** por app
- 🚀 **4 GB RAM**
- ⚡ **Sem dormência**
- 🔒 **Apps privados ilimitados**
- 📊 **Prioridade no suporte**

---

## 🐛 Troubleshooting

### Erro: "No module named 'X'"

**Causa:** Dependência faltando em `requirements.txt`

**Solução:**
1. Adicione a dependência em `requirements.txt`
2. Commit e push
3. Redeploy automático

### Erro: "API Key not found"

**Causa:** Secret não configurado

**Solução:**
1. Vá em Settings > Secrets
2. Adicione `FOOTBALL_DATA_API_KEY = "sua_chave"`
3. Save

### Erro: "HTTPError 429 - Too Many Requests"

**Causa:** Limite da API gratuita (10 req/min)

**Solução:**
- Aguarde 1 minuto
- Ou faça upgrade da API no Football-Data.org

### App muito lento

**Causa:** Modelos sendo treinados toda vez

**Solução:**
- O sistema já usa `@st.cache_resource` para treinar apenas 1x
- Se persistir, considere upgrade do plano

### App não atualiza

**Solução:**
1. Limpe o cache do navegador (Ctrl+F5)
2. No Streamlit Cloud, force Reboot
3. Verifique se o push foi para a branch `main`

---

## 📱 Compartilhar o App

### URL do seu app:

```
https://seu-nome-analises-esportivas.streamlit.app
```

### Como compartilhar:

1. ✅ Envie o link direto
2. ✅ Adicione no README do GitHub
3. ✅ Incorpore em um site (iframe)
4. ✅ Compartilhe nas redes sociais

### Personalizar URL:

1. Settings > General > App URL
2. Mude para algo memorável
3. Save

---

## 🔐 Segurança

### Boas Práticas:

- ✅ **Nunca commite** `.env` ou API keys
- ✅ **Use Secrets** do Streamlit para chaves
- ✅ **Mantenha repositório público** (para plano free)
- ✅ **Secrets não aparecem** nos logs públicos
- ✅ **Revise código** antes de fazer público

### Se expor acidentalmente uma key:

1. **Revogue imediatamente** no Football-Data.org
2. **Gere nova key**
3. **Atualize no Streamlit Secrets**

---

## 📚 Recursos Úteis

### Documentação:

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Deploy Tutorial](https://docs.streamlit.io/streamlit-community-cloud/get-started)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

### Comunidade:

- [Streamlit Forum](https://discuss.streamlit.io)
- [Streamlit Discord](https://discord.gg/streamlit)

---

## ✨ Resumo - Deploy em 5 Minutos

```bash
# 1. Criar repositório no GitHub (via web)

# 2. Push do código
git init
git add .
git commit -m "Deploy inicial"
git remote add origin https://github.com/SEU_USUARIO/analises-esportivas-v3.git
git push -u origin main

# 3. Deploy no Streamlit Cloud (via web)
# - Acesse: share.streamlit.io
# - New app
# - Selecione repositório
# - Main file: app_betting.py
# - Deploy!

# 4. Configurar API Key (via web)
# - Settings > Secrets
# - FOOTBALL_DATA_API_KEY = "sua_chave"
# - Save

# 5. Pronto! 🎉
# App estará em: https://seu-app.streamlit.app
```

---

## 🎉 Parabéns!

Seu app está **no ar** e acessível para qualquer pessoa! 🚀

**Próximos passos:**
- ✅ Teste todas as funcionalidades
- ✅ Compartilhe com amigos
- ✅ Continue desenvolvendo
- ✅ Monitore o uso

---

**Desenvolvido para o projeto Análises Esportivas v3**
*Guia atualizado: Outubro 2025*

