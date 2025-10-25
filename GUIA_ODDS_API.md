# 🎯 Guia Completo: The Odds API

## 📝 Passo a Passo para Começar

### 1. Criar Conta (GRÁTIS)

**Link:** https://the-odds-api.com/

1. Clique em **"Sign Up"**
2. Preencha:
   - Email
   - Password
   - Nome
3. Confirme o email
4. ✅ Conta criada!

**Plano Gratuito:**
- 🎁 500 requisições/mês
- ✅ Todas as ligas
- ✅ Todos os mercados
- ✅ Múltiplas casas de apostas
- ✅ Sem cartão de crédito

---

### 2. Pegar Sua API Key

**Link:** https://the-odds-api.com/account/

1. Faça login
2. Vá em **"API Keys"**
3. Copie sua key (parecido com: `abc123def456...`)
4. ⚠️ **NÃO COMPARTILHE** sua key!

---

### 3. Testar a API

**Execute o script de teste:**

```bash
# 1. Edite o arquivo
# Abra: test_odds_api.py
# Linha 19: Cole sua API Key

# 2. Execute
python test_odds_api.py
```

**O que o teste faz:**
- ✅ Testa conexão
- ✅ Lista todas as ligas disponíveis
- ✅ Busca odds do Brasileirão
- ✅ Busca odds da Premier League
- ✅ Compara odds entre casas
- ✅ Mostra quota de uso

---

## 📊 O Que a API Retorna

### Exemplo de Resposta (1X2):

```json
{
  "id": "abc123",
  "sport_key": "soccer_brazil_campeonato",
  "commence_time": "2025-10-26T20:00:00Z",
  "home_team": "Palmeiras",
  "away_team": "Flamengo",
  "bookmakers": [
    {
      "key": "bet365",
      "title": "Bet365",
      "markets": [
        {
          "key": "h2h",
          "outcomes": [
            {"name": "Palmeiras", "price": 2.10},
            {"name": "Draw", "price": 3.40},
            {"name": "Flamengo", "price": 3.80}
          ]
        }
      ]
    },
    {
      "key": "betano",
      "title": "Betano",
      "markets": [
        {
          "key": "h2h",
          "outcomes": [
            {"name": "Palmeiras", "price": 2.15},
            {"name": "Draw", "price": 3.35},
            {"name": "Flamengo", "price": 3.75}
          ]
        }
      ]
    }
  ]
}
```

---

## 🏆 Ligas Disponíveis

### Brasil:
- ✅ **Brasileirão Série A** (`soccer_brazil_campeonato`)
- ⚠️ Série B, Copa do Brasil (depende da época)

### Europa:
- ✅ **Premier League** (`soccer_epl`)
- ✅ **La Liga** (`soccer_spain_la_liga`)
- ✅ **Serie A** (`soccer_italy_serie_a`)
- ✅ **Bundesliga** (`soccer_germany_bundesliga`)
- ✅ **Ligue 1** (`soccer_france_ligue_one`)
- ✅ **Champions League** (`soccer_uefa_champs_league`)

### América:
- ✅ **MLS** (`soccer_usa_mls`)
- ✅ **Liga MX** (`soccer_mexico_ligamx`)
- ✅ **Copa Libertadores** (`soccer_conmebol_copa_libertadores`)

**Total:** 40+ ligas de futebol!

---

## 💰 Mercados Disponíveis

### 1. `h2h` (Head to Head / 1X2)
```python
{
  "key": "h2h",
  "outcomes": [
    {"name": "Home", "price": 2.10},  # Vitória Casa
    {"name": "Draw", "price": 3.40},  # Empate
    {"name": "Away", "price": 3.80}   # Vitória Fora
  ]
}
```

### 2. `totals` (Over/Under)
```python
{
  "key": "totals",
  "outcomes": [
    {"name": "Over", "price": 1.85, "point": 2.5},
    {"name": "Under", "price": 2.00, "point": 2.5}
  ]
}
```

### 3. `btts` (Both Teams to Score)
```python
{
  "key": "btts",
  "outcomes": [
    {"name": "Yes", "price": 1.70},
    {"name": "No", "price": 2.10}
  ]
}
```

### 4. Outros (Premium):
- `spreads` (Handicap Asiático)
- `player_points` (Apostas em Jogadores)
- `outrights` (Vencedor do Campeonato)

---

## 📈 Preços

### Plano Gratuito (Free)
```
💰 R$ 0/mês
📊 500 requisições/mês
✅ Todas as ligas
✅ Todos os mercados básicos
✅ Múltiplas casas
```

**Cálculo:**
- 500 req/mês ÷ 30 dias = ~16 req/dia
- 1 análise completa = 1 requisição
- **Ideal para:** Teste e uso pessoal leve

---

### Plano Starter
```
💰 $25/mês (~R$ 125)
📊 5.000 requisições/mês
✅ Tudo do Free
✅ Suporte prioritário
```

**Cálculo:**
- 5.000 req/mês ÷ 30 dias = ~166 req/dia
- **Ideal para:** Uso diário moderado

---

### Plano Plus
```
💰 $75/mês (~R$ 375)
📊 30.000 requisições/mês
✅ Tudo do Starter
✅ Dados históricos
```

**Ideal para:** Uso intensivo ou profissional

---

## 🔌 Como Integrar no Seu Sistema

### Cenário 1: Buscar Odds de Uma Partida

```python
def get_match_odds(home_team, away_team):
    """
    Busca odds de uma partida específica
    """
    from odds_api_client import OddsAPIClient
    
    client = OddsAPIClient('sua_api_key')
    
    # Busca odds
    matches = client.get_odds('soccer_brazil_campeonato')
    
    # Encontra partida
    for match in matches:
        if (match['home_team'] == home_team and 
            match['away_team'] == away_team):
            
            # Extrai melhores odds
            best_odds = client.get_best_odds(match)
            
            return {
                'casa': best_odds['home'],
                'empate': best_odds['draw'],
                'fora': best_odds['away'],
                'over_2_5': best_odds['over_2_5'],
                'under_2_5': best_odds['under_2_5'],
                'btts_yes': best_odds['btts_yes'],
                'btts_no': best_odds['btts_no']
            }
    
    return None
```

---

### Cenário 2: Integrar no Streamlit

**Adicionar botão de buscar odds:**

```python
# No app_betting.py

if st.button("🔍 Buscar Odds Automaticamente"):
    with st.spinner("Buscando odds do mercado..."):
        odds = get_match_odds(
            selected_match['home_team'],
            selected_match['away_team']
        )
        
        if odds:
            st.success("✅ Odds encontradas!")
            
            # Preenche os campos automaticamente
            st.session_state['odds_casa'] = odds['casa']
            st.session_state['odds_empate'] = odds['empate']
            st.session_state['odds_fora'] = odds['fora']
            # etc...
        else:
            st.warning("⚠️ Odds não disponíveis para esta partida")
```

---

### Cenário 3: Comparar Múltiplas Casas

```python
def compare_bookmakers(match_odds):
    """
    Compara odds de diferentes casas e retorna a melhor
    """
    best = {
        'casa': {'value': 0, 'bookmaker': ''},
        'empate': {'value': 0, 'bookmaker': ''},
        'fora': {'value': 0, 'bookmaker': ''}
    }
    
    for bookmaker in match_odds['bookmakers']:
        for outcome in bookmaker['markets'][0]['outcomes']:
            name = outcome['name']
            odd = outcome['price']
            
            if name == match_odds['home_team']:
                if odd > best['casa']['value']:
                    best['casa'] = {
                        'value': odd,
                        'bookmaker': bookmaker['title']
                    }
            # ... etc
    
    return best
```

---

## 🎯 Fluxo de Uso Recomendado

### Opção A: Automático (Requer API)

```
1. Usuário seleciona partida no Streamlit
2. Sistema busca odds automaticamente (The Odds API)
3. Sistema compara com modelo (Ensemble)
4. Identifica value bets
5. Recomenda apostas
```

**Vantagens:**
- ✅ Rápido e automático
- ✅ Sempre atualizado
- ✅ Compara múltiplas casas
- ✅ Profissional

**Desvantagens:**
- ❌ Custo (após 500 req/mês grátis)
- ❌ Depende de internet

---

### Opção B: Híbrido (Melhor Custo-Benefício)

```
1. Usuário seleciona partida no Streamlit
2. Sistema oferece:
   - Botão "Buscar Odds" (usa API)
   - OU campos manuais (digita)
3. Sistema compara e analisa
4. Recomenda apostas
```

**Vantagens:**
- ✅ Flexível
- ✅ Economiza requisições
- ✅ Funciona sem internet
- ✅ Usuário escolhe

---

### Opção C: Manual (Sem Custo)

```
1. Usuário abre FlashScore/Betano
2. Vê as odds
3. Digita manualmente no Streamlit
4. Sistema analisa
5. Recomenda apostas
```

**Vantagens:**
- ✅ 100% grátis
- ✅ Sem limites
- ✅ Simples

**Desvantagens:**
- ❌ Manual
- ❌ Mais lento

---

## 💡 Recomendação

### Para Começar (Agora):
👉 Use o **Plano Gratuito** (500 req/mês)
- Teste por 1-2 meses
- Veja se vale a pena
- 16 análises por dia é suficiente para maioria

### Se Gostar (Depois):
👉 Upgrade para **Starter** ($25/mês)
- 166 análises por dia
- Suporte prioritário
- Uso profissional

### Para Economizar:
👉 Use **Modo Híbrido**
- Busca automática só quando necessário
- Manual para apostas planejadas
- Melhor custo-benefício

---

## 🚀 Próximos Passos

1. **Execute o teste:**
   ```bash
   python test_odds_api.py
   ```

2. **Veja os resultados:**
   - Conexão funcionou?
   - Ligas disponíveis?
   - Odds apareceram?

3. **Decida:**
   - ✅ Gostou? → Integramos no Streamlit
   - ❌ Não gostou? → Continuamos manual
   - 🤔 Dúvidas? → Me pergunte!

---

## ❓ FAQ

**P: Precisa cartão para testar?**
R: Não! 500 req/mês 100% grátis sem cartão.

**P: As odds são em tempo real?**
R: Sim! Atualizadas a cada 5-10 minutos.

**P: Posso ver odds de várias casas?**
R: Sim! bet365, Betano, Pinnacle, etc.

**P: E se eu gastar as 500 requisições?**
R: Volta a funcionar no mês seguinte. Ou faz upgrade.

**P: Vale a pena pagar?**
R: Se você aposta regularmente e economiza tempo, sim!

**P: Posso cancelar quando quiser?**
R: Sim! Sem contrato, cancela quando quiser.

---

**Execute o teste e me diga o que achou!** 🚀

