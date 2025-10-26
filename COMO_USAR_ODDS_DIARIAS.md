# 🎯 Como Ter Acesso às Odds Diariamente

## 📋 O Que Foi Implementado

Seu projeto agora tem um **sistema completo de coleta e análise de odds** usando [The Odds API](https://the-odds-api.com/).

### ✅ Arquivos Criados

1. **`odds_api_client.py`** - Cliente para The Odds API
2. **`coletar_odds_diarias.py`** - Script de coleta diária
3. **`exemplo_integracao_odds.py`** - Exemplos de uso
4. **`SETUP_ODDS_API.md`** - Guia de configuração
5. **Arquivos .bat** - Executáveis Windows

### ✅ Funcionalidades

- ✅ Buscar odds de múltiplas ligas
- ✅ Comparar odds entre casas
- ✅ Identificar melhores odds
- ✅ Cache inteligente (economiza requisições)
- ✅ Comparar odds com modelos preditivos
- ✅ Detectar value bets automaticamente
- ✅ Salvar histórico de odds

---

## 🚀 Começar Agora (3 Passos)

### Passo 1: Criar Conta e Pegar API Key

1. Acesse: https://the-odds-api.com/
2. Crie conta gratuita (sem cartão)
3. Pegue sua API Key em: https://the-odds-api.com/account/

**Plano Gratuito:**
- 🎁 500 requisições/mês (~16/dia)
- ✅ Todas as ligas
- ✅ Todas as casas de apostas

---

### Passo 2: Configurar API Key

**Edite o arquivo `.env`** e adicione:

```env
ODDS_API_KEY=sua_key_aqui
```

> Se não existe `.env`, copie de `env_example.txt`

---

### Passo 3: Testar

**Windows:**
```
TESTAR_ODDS_API.bat
```

**Linux/Mac:**
```bash
python test_odds_api.py
```

Se funcionar, você verá:
- ✅ Conexão OK
- ✅ Ligas disponíveis
- ✅ Odds das partidas
- ✅ Quota restante

---

## 📊 Uso Diário

### Opção 1: Coleta Automatizada

Execute todos os dias pela manhã:

**Windows:**
```
COLETAR_ODDS_DIARIAS.bat
```

**Linux/Mac:**
```bash
python coletar_odds_diarias.py
```

Isso vai:
1. Buscar odds de todas as ligas configuradas
2. Salvar em `data/odds_daily/`
3. Usar cache para economizar requisições
4. Mostrar resumo no console

---

### Opção 2: Busca Programática

```python
from odds_api_client import OddsAPIClient

# Cria cliente
client = OddsAPIClient()

# Busca odds do Brasileirão (com cache)
odds = client.get_odds_with_cache(
    'soccer_brazil_campeonato',
    max_cache_age_hours=6
)

# Mostra partidas
for match in odds:
    print(f"{match['home_team']} vs {match['away_team']}")
    
    # Extrai melhores odds
    best = client.get_best_odds(match)
    print(f"  Casa: {best['home']['value']:.2f}")
    print(f"  Empate: {best['draw']['value']:.2f}")
    print(f"  Fora: {best['away']['value']:.2f}")
```

---

### Opção 3: Integração com Modelos

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

# Mostra value bets
for vb in analysis['value_bets']:
    print(f"💰 VALUE BET: {vb['outcome']}")
    print(f"   Value: {(vb['value']-1)*100:.1f}%")
    print(f"   Casa: {vb['bookmaker']}")
```

Veja mais exemplos em `exemplo_integracao_odds.py`

---

## 💡 Sistema de Cache Inteligente

O sistema tem cache automático que **economiza requisições**:

### Como Funciona

```python
# Primeira vez: busca da API (1 requisição)
odds = client.get_odds_with_cache('soccer_brazil_campeonato')

# Segunda vez: usa cache (0 requisições)
odds = client.get_odds_with_cache('soccer_brazil_campeonato')
```

### Cache Directory

```
data/
├── odds_cache/           # Cache por liga
│   ├── soccer_brazil_campeonato_20251026_090000.json
│   └── soccer_epl_20251026_090500.json
│
└── odds_daily/           # Resumos diários
    └── resumo_20251026_090000.json
```

### Configurar Tempo de Cache

```python
# Cache de 6 horas (padrão)
odds = client.get_odds_with_cache(
    'soccer_brazil_campeonato',
    max_cache_age_hours=6
)

# Cache de 24 horas (economiza mais)
odds = client.get_odds_with_cache(
    'soccer_brazil_campeonato',
    max_cache_age_hours=24
)

# Cache de 1 hora (mais atualizado)
odds = client.get_odds_with_cache(
    'soccer_brazil_campeonato',
    max_cache_age_hours=1
)
```

---

## 📈 Estratégias de Uso

### Estratégia 1: Análise Diária (Mais Econômica)

```
09:00 - Coleta todas as ligas (2-3 requisições)
        ↓
Durante o dia - Usa cache (0 requisições)
        ↓
Análises ilimitadas sem gastar quota!
```

**Requisições/dia:** 2-3  
**Requisições/mês:** ~90  
**Sobra:** 410 requisições

---

### Estratégia 2: Análise Pre-Game (Balanceada)

```
2h antes do jogo - Busca odds atualizadas
        ↓
Faz análise com modelos
        ↓
Identifica value bets
        ↓
Faz apostas
```

**Requisições/dia:** ~5-10  
**Requisições/mês:** ~300  
**Sobra:** 200 requisições

---

### Estratégia 3: Monitoramento Contínuo (Intensiva)

```
A cada 2 horas - Atualiza odds
        ↓
Detecta mudanças
        ↓
Alerta de value bets
```

**Requisições/dia:** ~12-15  
**Requisições/mês:** ~450  
**Requer:** Plano pago ou cache agressivo

---

## 🏆 Ligas Disponíveis

### Brasil
- ✅ **Brasileirão Série A** (`BSA`)

### Europa
- ✅ **Premier League** (`PL`)
- ✅ **La Liga** (`LaLiga`)
- ✅ **Serie A** (`SerieA`)
- ✅ **Bundesliga** (`Bundesliga`)
- ✅ **Ligue 1** (`Ligue1`)

### Internacional
- ✅ **Champions League** (`Champions`)

**Total:** 40+ ligas de futebol disponíveis!

Para adicionar mais ligas, edite `odds_api_client.py`:

```python
LEAGUE_MAPPING = {
    'BSA': 'soccer_brazil_campeonato',
    'PL': 'soccer_epl',
    'MeuCampeonato': 'soccer_...',  # Adicione aqui
}
```

Veja todas as ligas disponíveis: https://the-odds-api.com/sports-odds-data/soccer.html

---

## 📊 Mercados Disponíveis

### 1. H2H (1X2)
- Vitória Casa
- Empate
- Vitória Fora

### 2. Totals (Over/Under)
- Over 2.5 gols
- Under 2.5 gols

### 3. BTTS (Both Teams To Score)
- Ambos marcam: Sim
- Ambos marcam: Não

### 4. Outros (Premium)
- Handicap Asiático
- Apostas em jogadores
- Vencedor do campeonato

---

## 🔧 Troubleshooting

### ❌ Erro: API Key inválida

**Solução:**
1. Verifique se copiou a key completa
2. Não deve ter espaços
3. Confirme em: https://the-odds-api.com/account/

---

### ❌ Erro: Nenhuma partida disponível

**Causas:**
- Liga fora de temporada
- Sem jogos agendados
- Tente outra liga (ex: Premier League sempre tem jogos)

---

### ❌ Quota esgotada

**Soluções:**
1. Use cache mais agressivo (24h)
2. Aguarde reset mensal
3. Considere upgrade:
   - **Starter:** $25/mês = 5.000 req/mês
   - **Plus:** $75/mês = 30.000 req/mês

---

## 📁 Estrutura do Projeto

```
analises_esportivas_v3/
├── odds_api_client.py              # Cliente The Odds API
├── coletar_odds_diarias.py         # Coleta diária
├── exemplo_integracao_odds.py      # Exemplos de uso
│
├── SETUP_ODDS_API.md              # Guia de configuração
├── COMO_USAR_ODDS_DIARIAS.md      # Este arquivo
├── GUIA_ODDS_API.md               # Guia detalhado
│
├── COLETAR_ODDS_DIARIAS.bat       # Executável Windows
├── TESTAR_ODDS_API.bat            # Teste Windows
├── EXEMPLO_INTEGRACAO_ODDS.bat    # Exemplos Windows
│
├── data/
│   ├── odds_cache/                # Cache de odds
│   └── odds_daily/                # Resumos diários
│
└── .env                           # Configuração (ODDS_API_KEY)
```

---

## 🎯 Fluxo Completo Recomendado

### Setup Inicial (Uma Vez)

```
1. Criar conta → https://the-odds-api.com/
2. Pegar API Key
3. Configurar .env
4. Testar conexão (TESTAR_ODDS_API.bat)
```

---

### Rotina Diária

```
09:00 - Executar COLETAR_ODDS_DIARIAS.bat
         ↓
09:05 - Analisar partidas com modelos
         ↓
15:00 - Revisar análises (usa cache)
         ↓
18:00 - Fazer apostas antes dos jogos
```

---

### Análise de Partida

```python
from odds_api_client import OddsAPIClient

# 1. Buscar odds
client = OddsAPIClient()
odds = client.get_odds_with_cache('soccer_brazil_campeonato')

# 2. Selecionar partida
match = odds[0]  # ou buscar específica

# 3. Extrair melhores odds
best = client.get_best_odds(match)

# 4. Rodar seus modelos
# (Ensemble, Dixon-Coles, etc)
home_prob, draw_prob, away_prob = seu_modelo.predict(...)

# 5. Comparar e encontrar value
analysis = client.compare_with_predictions(
    match, home_prob, draw_prob, away_prob
)

# 6. Se encontrou value → APOSTAR!
if analysis['value_bets']:
    print("💰 VALUE BET ENCONTRADO!")
```

---

## 📚 Documentação Adicional

### Documentação do Projeto
- [`SETUP_ODDS_API.md`](SETUP_ODDS_API.md) - Setup passo a passo
- [`GUIA_ODDS_API.md`](GUIA_ODDS_API.md) - Guia completo
- [`exemplo_integracao_odds.py`](exemplo_integracao_odds.py) - Exemplos práticos

### Documentação Externa
- [The Odds API Docs](https://the-odds-api.com/liveapi/guides/v4/)
- [Sports Available](https://the-odds-api.com/sports-odds-data/soccer.html)
- [Code Examples](https://github.com/the-odds-api/samples-python)

---

## ❓ FAQ

**P: Preciso cartão para começar?**  
R: Não! 500 requisições/mês 100% grátis.

**P: As odds são em tempo real?**  
R: Sim! Atualizadas a cada 5-10 minutos.

**P: Posso ver odds de várias casas?**  
R: Sim! O sistema compara todas e retorna as melhores.

**P: O cache é confiável?**  
R: Sim! Odds não mudam muito em horas. Cache de 6h é seguro.

**P: Quanto custa uma requisição?**  
R: Depende dos mercados. Normalmente 1 requisição = 1 liga com mercado h2h.

**P: Vale a pena pagar?**  
R: Se você aposta regularmente, sim! Automatiza busca de odds e economiza tempo.

**P: Posso integrar com meu bot de apostas?**  
R: Sim! A API é profissional e confiável para produção.

---

## 🎉 Pronto!

Você agora tem um **sistema completo de coleta e análise de odds**!

### Próximos Passos

1. ✅ Configure sua API Key
2. ✅ Execute o teste
3. ✅ Faça sua primeira coleta
4. ✅ Integre com seus modelos
5. ✅ Automatize a rotina diária

---

**💚 Boas apostas e bons lucros! 💚**

---

## 📞 Suporte

Dúvidas sobre:
- **The Odds API:** https://the-odds-api.com/
- **Documentação:** Leia os guias na pasta `docs/`
- **Código:** Veja os exemplos em `exemplo_integracao_odds.py`

