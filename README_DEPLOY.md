# 🚀 Deploy Rápido - Resumo

## Deploy em 3 Passos Simples

### ✅ Passo 1: GitHub (2 min)
```bash
# Inicializar e fazer push
git init
git add .
git commit -m "Deploy inicial - Sistema de apostas esportivas"
git remote add origin https://github.com/SEU_USUARIO/analises-esportivas-v3.git
git push -u origin main
```

### ✅ Passo 2: Streamlit Cloud (2 min)
1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Faça login com GitHub
3. Clique **"New app"**
4. Configure:
   - **Repository**: `SEU_USUARIO/analises-esportivas-v3`
   - **Branch**: `main`
   - **Main file**: `app_betting.py`
5. Clique **"Deploy!"**

### ✅ Passo 3: Configurar API Key (1 min)
1. No app deployado, clique **"Settings"** ⚙️
2. Vá em **"Secrets"**
3. Cole:
```toml
FOOTBALL_DATA_API_KEY = "SUA_CHAVE_API_AQUI"
```
4. **Save**

## 🎉 Pronto!

Seu app estará online em:
```
https://seu-app-name.streamlit.app
```

---

## 📖 Documentação Completa

Para guia detalhado com troubleshooting e configurações avançadas:
👉 **[DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md)**

---

## ⚡ Atualização Automática

Após o deploy inicial, qualquer mudança é automática:

```bash
# Fez alterações no código?
git add .
git commit -m "Nova feature"
git push

# Deploy automático em ~30 segundos! 🚀
```

---

## 📊 Funcionalidades Disponíveis Online

Após deploy, o app terá:

- ✅ **Análise de Apostas** com 3 modelos preditivos
- ✅ **Análise de Times** com gráficos interativos
- ✅ **Bingo (Apostas Múltiplas)** - NOVO!
- ✅ **Value Betting** com EV e Kelly Criterion
- ✅ **Suporte a múltiplas ligas** (Premier League + Brasileirão)
- ✅ **Interface responsiva** e profissional

---

## 🆓 100% Gratuito

O Streamlit Cloud oferece:
- ✅ Apps públicos ilimitados
- ✅ 1 GB RAM por app
- ✅ Deploy automático
- ✅ HTTPS gratuito
- ✅ Sem limite de acessos

---

## 🐛 Problemas?

### App não carrega
→ Verifique se configurou a API Key nos Secrets

### Erro de dependências
→ Verifique `requirements.txt`

### App dormindo
→ Normal após 7 dias sem uso. Acorda automaticamente ao acessar.

---

**Dúvidas? Consulte o guia completo!**

**Desenvolvido para Análises Esportivas v3**

