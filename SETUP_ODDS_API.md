# 🚀 Setup The Odds API - Guia Rápido

## 📝 Configuração em 5 Minutos

### Passo 1: Criar Conta Gratuita

1. Acesse: https://the-odds-api.com/
2. Clique em **"Sign Up"**
3. Preencha email e senha
4. Confirme o email
5. ✅ Conta criada!

**Plano Gratuito:**
- 🎁 500 requisições/mês
- ✅ Todas as ligas
- ✅ Sem cartão de crédito

---

### Passo 2: Pegar API Key

1. Acesse: https://the-odds-api.com/account/
2. Faça login
3. Copie sua **API Key** (algo como: `abc123def456...`)

---

### Passo 3: Configurar no Projeto

**Opção A: Usando arquivo .env (Recomendado)**

1. Abra o arquivo `.env` (ou crie a partir do `env_example.txt`)
2. Adicione sua key:
```env
ODDS_API_KEY=sua_key_aqui
```
3. Salve o arquivo

**Opção B: Editando diretamente (Temporário para teste)**

1. Abra `test_odds_api.py`
2. Linha 23, substitua:
```python
API_KEY = 'SUA_API_KEY_AQUI'  # ← Cole sua key aqui
```

---

### Passo 4: Testar Conexão

Execute o teste:
```bash
python test_odds_api.py
```

Ou use o .bat (Windows):
```
TESTAR_ODDS_API.bat
```

**O que será testado:**
- ✅ Conexão com API
- ✅ Ligas disponíveis
- ✅ Odds do Brasileirão
- ✅ Odds da Premier League
- ✅ Comparação de casas
- ✅ Quota de uso

---

## 🎯 Como Usar Diariamente

### Opção 1: Coletar Todas as Ligas

**Windows:**
```
COLETAR_ODDS_DIARIAS.bat
```

**Linux/Mac:**
```bash
python coletar_odds_diarias.py
```

Isso vai:
- Buscar odds de todas as ligas configuradas
- Salvar em `data/odds_daily/`
- Usar cache para economizar requisições
- Mostrar resumo no console

---

### Opção 2: Coletar Liga Específica

**Python:**
```python
from odds_api_client import OddsAPIClient

client = OddsAPIClient()

# Brasileirão
odds = client.get_odds_by_league_code('BSA')

# Premier League
odds = client.get_odds_by_league_code('PL')

# Ver melhores odds de uma partida
for match in odds:
    best = client.get_best_odds(match)
    print(f"{match['home_team']} vs {match['away_team']}")
    print(f"Casa: {best['home']['value']:.2f}")
    print(f"Empate: {best['draw']['value']:.2f}")
    print(f"Fora: {best['away']['value']:.2f}")
```

---

### Opção 3: Buscar Odds com Cache

O sistema tem cache inteligente que economiza requisições:

```python
from odds_api_client import OddsAPIClient

client = OddsAPIClient()

# Busca com cache de 6 horas
odds = client.get_odds_with_cache(
    'soccer_brazil_campeonato',
    max_cache_age_hours=6
)
```

**Como funciona:**
- Se há dados recentes no cache (< 6h) → Usa cache (0 requisições)
- Se não há cache ou está velho → Busca da API (1 requisição)
- Dados salvos em `data/odds_cache/`

---

## 📊 Integração com Modelos

### Comparar Odds com Suas Predições

```python
from odds_api_client import OddsAPIClient

client = OddsAPIClient()

# Busca odds da partida
match_odds = client.get_match_odds(
    home_team="Palmeiras",
    away_team="Flamengo",
    sport_key="soccer_brazil_campeonato"
)

# Suas probabilidades do modelo
home_prob = 0.45  # 45%
draw_prob = 0.25  # 25%
away_prob = 0.30  # 30%

# Compara e encontra value bets
analysis = client.compare_with_predictions(
    match_odds,
    home_prob,
    draw_prob,
    away_prob,
    min_value=1.05  # Mínimo 5% de value
)

# Mostra value bets encontrados
for vb in analysis['value_bets']:
    print(f"💰 VALUE BET: {vb['outcome']}")
    print(f"   Odd Mercado: {vb['market_odd']:.2f}")
    print(f"   Odd Modelo: {vb['model_odd']:.2f}")
    print(f"   Value: {(vb['value']-1)*100:.1f}%")
    print(f"   Casa: {vb['bookmaker']}")
```

---

## 💡 Dicas de Economia

### 1. Use Cache Sempre Que Possível

```python
# ✅ BOM - Usa cache de 6 horas
odds = client.get_odds_with_cache('soccer_brazil_campeonato')

# ❌ RUIM - Sempre busca da API
odds = client.get_odds('soccer_brazil_campeonato')
```

### 2. Colete em Horários Estratégicos

**Melhor horário:** Manhã cedo (antes dos jogos)
- Odds já estão disponíveis
- Uma coleta serve para o dia todo
- Cache evita novas requisições

**Exemplo de rotina diária:**
```
09:00 - Coleta todas as ligas (1-3 requisições)
15:00 - Análises (usa cache - 0 requisições)
20:00 - Análises (usa cache - 0 requisições)
```

### 3. Monitore Sua Quota

```python
client = OddsAPIClient()
odds = client.get_odds('soccer_brazil_campeonato')

# Mensagem automática mostrará:
# 📊 Quota API: 10 usadas | 490 restantes | 1 último custo
```

---

## 📁 Estrutura de Dados

### Cache Local
```
data/
├── odds_cache/           # Cache de odds por liga
│   ├── soccer_brazil_campeonato_20251026_090000.json
│   └── soccer_epl_20251026_090500.json
│
└── odds_daily/           # Resumos diários consolidados
    ├── resumo_20251026_090000.json
    └── resumo_20251025_090000.json
```

### Formato do Resumo Diário

```json
{
  "timestamp": "2025-10-26T09:00:00",
  "total_partidas": 12,
  "ligas": {
    "BSA": {
      "nome": "Brasileirão Série A",
      "num_partidas": 5,
      "partidas": [
        {
          "home_team": "Palmeiras",
          "away_team": "Flamengo",
          "commence_time": "2025-10-26T20:00:00Z",
          "odds_casa": 2.10,
          "odds_empate": 3.40,
          "odds_fora": 3.80,
          "num_bookmakers": 8
        }
      ]
    }
  }
}
```

---

## 🔧 Solução de Problemas

### Erro: API Key inválida

**Problema:**
```
❌ Erro: API Key inválida
```

**Solução:**
1. Verifique se copiou a key completa
2. Não deve ter espaços antes/depois
3. Confira em: https://the-odds-api.com/account/

---

### Erro: Nenhuma partida disponível

**Problema:**
```
⚠️ Nenhuma partida disponível no momento
```

**Causas:**
- Liga fora de temporada
- Sem jogos agendados para próximos dias
- Tente outra liga

---

### Erro: Quota esgotada

**Problema:**
```
📊 Quota API: 500 usadas | 0 restantes
```

**Soluções:**
1. Use mais cache (`max_cache_age_hours=24`)
2. Aguarde reset mensal
3. Considere upgrade do plano

---

## 📈 Planos The Odds API

### Gratuito (Free)
```
💰 R$ 0/mês
📊 500 requisições/mês (~16/dia)
✅ Todas as ligas e mercados
```

### Starter
```
💰 $25/mês (~R$ 125)
📊 5.000 requisições/mês (~166/dia)
✅ Suporte prioritário
```

### Plus
```
💰 $75/mês (~R$ 375)
📊 30.000 requisições/mês (~1000/dia)
✅ Dados históricos
```

---

## 🎯 Próximos Passos

1. ✅ Configure sua API Key
2. ✅ Execute o teste
3. ✅ Faça sua primeira coleta
4. ✅ Integre com seus modelos
5. ✅ Configure rotina diária

---

## 📚 Documentação Adicional

- [The Odds API Docs](https://the-odds-api.com/liveapi/guides/v4/)
- [Guia The Odds API (Português)](GUIA_ODDS_API.md)
- [Code Examples](https://github.com/the-odds-api/samples-python)

---

## ❓ Dúvidas Frequentes

**P: Preciso cartão para testar?**
R: Não! 500 requisições/mês 100% grátis.

**P: Quanto custa uma requisição?**
R: Depende dos mercados. 1 liga com mercado h2h = 1 requisição.

**P: O cache é confiável?**
R: Sim! Odds não mudam muito em poucas horas. Cache de 6h é seguro.

**P: Posso usar em produção?**
R: Sim! A API é profissional e confiável.

**P: E se eu quiser mais ligas?**
R: Adicione em `config.py` no dicionário `LEAGUES`.

---

**✅ Tudo pronto! Comece a coletar odds diariamente!** 🚀

