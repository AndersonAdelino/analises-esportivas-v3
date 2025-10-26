# 🌍 Regiões The Odds API - Explicação

## ⚠️ IMPORTANTE: Brasil (br) NÃO é uma região válida!

A The Odds API **NÃO** tem região `br` (Brasil) como opção.

---

## ✅ Regiões Válidas

As regiões representam **onde as casas de apostas operam**, não os campeonatos:

| Região | Código | Casas de Apostas |
|--------|--------|------------------|
| 🇺🇸 Estados Unidos | `us` | FanDuel, DraftKings, BetMGM, Caesars, etc |
| 🇬🇧 Reino Unido | `uk` | Bet365, William Hill, Ladbrokes, etc |
| 🇪🇺 Europa | `eu` | Betano, Betclic, Unibet, etc |
| 🇦🇺 Austrália | `au` | Sportsbet, TAB, etc |

---

## 🤔 Por Que Não Tem Brasil?

A API foca em mercados regulamentados com muitas casas de apostas:
- Casas brasileiras não estão na API (ainda)
- Mas você pode usar casas **europeias** que operam no Brasil

---

## 🎯 Como Usar para Brasileirão

### ✅ CORRETO: Use região `eu` (Europa)

```python
# Busca odds do Brasileirão de casas EUROPEIAS
odds = client.get_odds(
    'soccer_brazil_campeonato',
    regions='us,uk,eu',  # ← SEM 'br'!
    markets='h2h,totals,btts'
)
```

**Casas europeias que funcionam:**
- Bet365 (uk)
- Betano (eu)
- Betclic (eu)
- Pinnacle (us)
- Unibet (eu)

---

### ❌ ERRADO: Tentar usar `br`

```python
# ❌ ERRO: Região inválida!
odds = client.get_odds(
    'soccer_brazil_campeonato',
    regions='br,us,uk,eu',  # ← 'br' vai dar erro!
    markets='h2h'
)
```

**Resultado:**
```
❌ ERRO: 422
{"message":"One or more regions invalid","error_code":"INVALID_REGION"}
```

---

## 📊 Quais Casas Aparecem

Depende da região e do campeonato:

### Brasileirão (`soccer_brazil_campeonato`)

**Região `eu` (Mais comum):**
- ✅ Bet365
- ✅ Betano
- ✅ Betclic
- ✅ Unibet
- ✅ Pinnacle

**Região `us`:**
- ✅ DraftKings (se tiver)
- ✅ FanDuel (se tiver)

**Região `uk`:**
- ✅ Bet365
- ✅ William Hill
- ✅ Ladbrokes

### Premier League (`soccer_epl`)

**Região `uk` (Mais comum):**
- ✅ Bet365
- ✅ William Hill
- ✅ Ladbrokes
- ✅ Paddy Power
- ✅ Sky Bet

**Região `us`:**
- ✅ FanDuel
- ✅ DraftKings
- ✅ BetMGM
- ✅ Caesars

---

## 💡 Recomendações

### Para Brasileirão
```python
regions='eu'  # Melhor cobertura de casas europeias
```

### Para Premier League
```python
regions='uk,eu'  # Casas UK + EU
```

### Para Todas as Ligas (Padrão)
```python
regions='us,uk,eu'  # Máxima cobertura global
```

### Economizar Requisições
```python
regions='eu'  # Só Europa (menos casas = menos custo)
```

---

## 📈 Custo por Região

O custo da API depende do número de regiões:

```
Custo = [mercados] x [regiões]

Exemplos:
- 1 mercado, 1 região = 1 requisição
- 1 mercado, 3 regiões = 3 requisições
- 3 mercados, 3 regiões = 9 requisições
```

**Dica:** Use só as regiões que você precisa!

---

## 🎯 Configuração Recomendada

### Para Brasileiros

```python
from odds_api_client import OddsAPIClient

client = OddsAPIClient()

# Brasileirão: Use casas europeias
odds_brasileirao = client.get_odds(
    'soccer_brazil_campeonato',
    regions='eu',      # Betano, Bet365, etc
    markets='h2h'      # 1X2
)

# Premier League: Use UK + Europa
odds_premier = client.get_odds(
    'soccer_epl',
    regions='uk,eu',   # Mais casas
    markets='h2h'
)

# Champions League: Todas as regiões
odds_champions = client.get_odds(
    'soccer_uefa_champs_league',
    regions='us,uk,eu',  # Cobertura máxima
    markets='h2h'
)
```

---

## ❓ FAQ

**P: Por que não tem casas brasileiras?**  
R: A API foca em mercados regulamentados. Brasil está crescendo, pode ser adicionado no futuro.

**P: Posso apostar nas casas que aparecem?**  
R: Sim! Muitas casas europeias (Bet365, Betano) operam no Brasil.

**P: Qual região tem mais casas?**  
R: Depende da liga:
   - Premier League → `uk`
   - Brasileirão → `eu`
   - MLS → `us`

**P: Como economizar requisições?**  
R: Use só 1 região (ex: `regions='eu'`) em vez de 3.

**P: As odds são iguais em todas as regiões?**  
R: Não! Cada casa tem suas próprias odds. Por isso é bom comparar várias regiões.

---

## ✅ Resumo

### ✅ Faça
- Use `us`, `uk`, `eu`, `au`
- Para Brasileirão: `regions='eu'`
- Compare múltiplas casas

### ❌ Não Faça
- Não use `br` (não existe!)
- Não use todas as regiões se não precisa (gasta mais requisições)

---

## 🔗 Links Úteis

- **Documentação Oficial:** https://the-odds-api.com/liveapi/guides/v4/
- **Regiões e Casas:** https://the-odds-api.com/sports-odds-data/bookmaker-apis.html
- **Códigos de Erro:** https://the-odds-api.com/liveapi/guides/v4/api-error-codes.html

---

**🎯 Agora você sabe como usar regiões corretamente!**

Execute novamente: `TESTAR_ODDS_API.bat` ✅

