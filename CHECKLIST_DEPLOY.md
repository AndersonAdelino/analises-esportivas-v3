# ✅ Checklist de Deploy - Streamlit Cloud

Use este checklist para garantir que tudo está pronto antes do deploy.

## 📋 Antes do Deploy

### Arquivos e Configurações
- [ ] `requirements.txt` está completo com todas as dependências
- [ ] `.gitignore` configurado (não commitar `.env` e `secrets.toml`)
- [ ] `.streamlit/config.toml` criado
- [ ] `.streamlit/secrets.toml.example` criado como exemplo
- [ ] API Key do Football-Data.org obtida ([Registrar aqui](https://www.football-data.org/client/register))

### Código
- [ ] Código testado localmente (`streamlit run app_betting.py`)
- [ ] Todas as 3 abas funcionando:
  - [ ] Análise de Apostas
  - [ ] Análise de Times  
  - [ ] Bingo (Apostas Múltiplas)
- [ ] Modelos preditivos carregando corretamente
- [ ] Cache do Streamlit funcionando

### Git
- [ ] Repositório inicializado (`git init`)
- [ ] Primeiro commit feito
- [ ] Repositório criado no GitHub (público)
- [ ] Remote configurado (`git remote add origin ...`)
- [ ] Código enviado para GitHub (`git push`)

---

## 🚀 Durante o Deploy

### Streamlit Cloud
- [ ] Conta criada em [share.streamlit.io](https://share.streamlit.io)
- [ ] GitHub conectado
- [ ] Novo app criado
- [ ] Repositório selecionado
- [ ] Branch `main` selecionada
- [ ] Main file: `app_betting.py`
- [ ] Deploy iniciado

### Configuração de Secrets
- [ ] Settings > Secrets aberto
- [ ] `FOOTBALL_DATA_API_KEY` configurado
- [ ] Secret salvo
- [ ] App redeploy automático

---

## ✅ Após o Deploy

### Teste Básico
- [ ] App abre sem erros
- [ ] Sidebar mostra configurações
- [ ] Seletor de liga funciona (Premier League, Brasileirão)

### Teste - Análise de Apostas
- [ ] Modelos carregam (Dixon-Coles, Offensive-Defensive, Heurísticas)
- [ ] Próximas partidas aparecem
- [ ] Pode selecionar partida
- [ ] Pode inserir odds
- [ ] Análise gera resultados
- [ ] Value bets são identificados
- [ ] Salvamento no cache do Bingo funciona

### Teste - Análise de Times
- [ ] Lista de times carrega
- [ ] Pode selecionar time
- [ ] Histórico de partidas aparece
- [ ] 5 gráficos aparecem corretamente:
  - [ ] Resultados ao longo do tempo
  - [ ] Tendência de gols
  - [ ] Forma e pontos
  - [ ] Casa vs Fora
  - [ ] Distribuição de resultados
- [ ] Tabela de histórico aparece

### Teste - Bingo (Apostas Múltiplas)
- [ ] Mostra métricas do cache
- [ ] Avisa se tem menos de 3 partidas
- [ ] Pode configurar filtros
- [ ] Botão "GERAR BINGO" funciona
- [ ] Cartela é gerada corretamente
- [ ] Métricas são exibidas:
  - [ ] Odd total
  - [ ] Probabilidade
  - [ ] EV%
  - [ ] Score
  - [ ] Financeiro
- [ ] Palpites são listados
- [ ] Botão "Limpar Cache" funciona

### Performance
- [ ] App carrega em menos de 10 segundos
- [ ] Modelos treinam apenas 1x (cache funciona)
- [ ] Troca de liga funciona
- [ ] Navegação entre abas é fluida

---

## 🔄 Atualizações Futuras

### Fluxo de Atualização
- [ ] Fez alterações no código local
- [ ] Testou localmente
- [ ] Commit com mensagem descritiva
- [ ] Push para GitHub
- [ ] Aguardou redeploy automático (~30s)
- [ ] Testou app online

---

## 📊 Monitoramento

### Métricas para Acompanhar
- [ ] Número de acessos/dia
- [ ] Tempo de resposta
- [ ] Erros nos logs
- [ ] Uso de recursos (RAM/CPU)
- [ ] Feedback dos usuários

### Logs
- [ ] Sabe como acessar logs no painel
- [ ] Verificou logs após deploy
- [ ] Sem erros críticos

---

## 🐛 Troubleshooting Checklist

Se algo não funcionar, verifique:

### App não carrega
- [ ] API Key configurada nos Secrets?
- [ ] API Key válida?
- [ ] Branch correta selecionada?
- [ ] `app_betting.py` está no root?

### Erro de dependências
- [ ] `requirements.txt` tem todas as libs?
- [ ] Versões compatíveis?
- [ ] Todas as libs estão no PyPI?

### Cache não funciona
- [ ] `@st.cache_resource` presente?
- [ ] Limpou cache via interface?
- [ ] Reiniciou o app?

### API retorna erro 429
- [ ] Muitas requisições? (limite: 10/min)
- [ ] Aguarde 1 minuto
- [ ] Considere upgrade da API

### Modelos não carregam
- [ ] Dados disponíveis?
- [ ] Internet funcionando?
- [ ] Logs mostram qual erro?

---

## 🎉 Deploy Bem-Sucedido!

Se todos os itens acima estão ✅, parabéns!

Seu app está:
- ✅ Online e acessível
- ✅ Funcionando corretamente
- ✅ Pronto para uso
- ✅ Com deploy automático configurado

---

## 📱 Próximos Passos

Após deploy bem-sucedido:

1. **Compartilhe o link**
   - Envie para amigos
   - Poste nas redes sociais
   - Adicione no README do GitHub

2. **Monitore o uso**
   - Acompanhe analytics
   - Leia feedback
   - Corrija bugs rapidamente

3. **Continue desenvolvendo**
   - Adicione novas features
   - Melhore a UX
   - Otimize performance

4. **Considere Monetização** (opcional)
   - Plano premium com mais features
   - Consultoria para apostadores
   - Venda de análises

---

**Sucesso no seu projeto! 🚀**

**Desenvolvido para Análises Esportivas v3**

