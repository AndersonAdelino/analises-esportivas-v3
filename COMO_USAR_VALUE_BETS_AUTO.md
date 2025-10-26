# 💰 Value Bets Automáticos - Guia Completo

## 🎯 O Que É

Sistema automático que **busca odds da Bet365** e **compara com seus modelos preditivos** para encontrar value bets automaticamente.

### Funcionalidades

✅ **Busca automática de odds** da Bet365  
✅ **Análise automática** com modelos preditivos  
✅ **Detecção de value bets** em 3 mercados:
   - 1X2 (Casa/Empate/Fora)
   - Over/Under 2.5 gols
   - BTTS (Ambos marcam)

✅ **Ordenação inteligente** por EV ou Probabilidade  
✅ **Interface web** completa no Streamlit  
✅ **Economia de requisições** (usa cache)  

---

## 🚀 Como Usar

### Passo 1: Configurar API Key

Se ainda não fez, configure sua API Key da The Odds API:

```bash
# Executar uma vez
.\CRIAR_ENV_COM_API_KEY.bat
```

Ou manualmente no arquivo `.env`:
```env
ODDS_API_KEY=ae43b69e9ef7398ca4325da3891bc54b
```

---

### Passo 2: Abrir o Streamlit

```bash
streamlit run app_betting.py
```

Ou use o executável:
```bash
INICIAR_SERVIDOR.bat
```

---

### Passo 3: Acessar a Aba "Value Bets Automáticos"

1. No Streamlit, clique na aba **"💰 Value Bets Automáticos"**
2. Na barra lateral, selecione as ligas que quer analisar
3. Configure os filtros (value mínimo, EV mínimo)
4. Escolha a ordenação (EV ou Probabilidade)
5. Clique em **"🔄 Atualizar Dados"**

---

## 📊 Interface

### Visualizações Disponíveis

#### 1. Lista Completa
- Todos os value bets encontrados
- Ordenados por EV ou Probabilidade
- Com todas as informações (Odd, Prob, Value, EV, Kelly)
- Download em CSV

#### 2. Top 10
- Os 10 melhores value bets
- Visual expandido
- Barra de progresso Kelly Criterion
- Informações detalhadas

#### 3. Estatísticas
- Gráficos de distribuição
- Análise por mercado
- Análise por liga
- Resumo consolidado

---

## ⚙️ Configurações

### Filtros Disponíveis

**Mercados:**
- 1X2 (Casa/Empate/Fora)
- Over/Under 2.5 gols
- BTTS (Ambos marcam)

**Value Mínimo:**
- 0% a 50%
- Padrão: 5% (mostra apenas value > 5%)

**EV Mínimo:**
- -10% a 50%
- Padrão: 0% (mostra apenas EV positivo)

**Ordenação:**
- EV (Maior/Menor)
- Probabilidade (Maior/Menor)
- Value (Maior/Menor)

---

## 💡 Como Funciona

### 1. Busca de Odds
```python
# Busca odds da Bet365 via API
odds = buscar_odds_bet365('Brasileirão')
```

### 2. Cálculo de Probabilidades
```python
# Usa seus modelos preditivos
modelo = EnsembleModel()
probs = modelo.predict(home_team, away_team)
```

### 3. Identificação de Value
```python
# Compara odds do mercado com modelo
odd_mercado = 2.10
prob_modelo = 0.55  # 55%
odd_modelo = 1 / prob_modelo = 1.82

value = odd_mercado / odd_modelo
value = 2.10 / 1.82 = 1.15  # 15% de value!
```

### 4. Cálculo de EV
```python
EV = (odd_mercado × prob_modelo) - 1
EV = (2.10 × 0.55) - 1 = 0.155
EV = +15.5%  # ✅ Value bet!
```

---

## 📈 Interpretando os Resultados

### Colunas da Tabela

| Coluna | Significado | Bom Valor |
|--------|-------------|-----------|
| **Odd** | Odd da Bet365 | Depende |
| **Prob.** | Probabilidade do modelo | > 50% |
| **Value** | Percentual de value | > 5% |
| **EV** | Expected Value | > 0% |
| **Kelly** | Fração da banca a apostar | 0-20% |

### Exemplo Prático

```
Partida: Flamengo vs Botafogo
Mercado: 1X2
Tipo: Casa (Flamengo)
Odd: 1.85
Prob.: 60.5%
Value: +12.1%
EV: +11.9%
Kelly: 15.3%
```

**Interpretação:**
- ✅ **Value de 12.1%** → Boa oportunidade
- ✅ **EV positivo** → Lucrativo no longo prazo
- ✅ **Kelly 15.3%** → Aposte 15.3% da banca
- 💡 **Probabilidade alta (60.5%)** → Aposta mais segura

---

## 💰 Estratégias Recomendadas

### 1. Conservadora
```
Value Mínimo: 10%
EV Mínimo: 5%
Kelly Fraction: 0.25
```
**Resultado:** Poucos value bets, mas muito seguros

### 2. Balanceada (Recomendada)
```
Value Mínimo: 5%
EV Mínimo: 0%
Kelly Fraction: 0.50
```
**Resultado:** Bom equilíbrio entre quantidade e qualidade

### 3. Agressiva
```
Value Mínimo: 3%
EV Mínimo: -2%
Kelly Fraction: 1.00
```
**Resultado:** Muitos value bets, maior risco

---

## ⚠️ Avisos Importantes

### Limitações

❌ **BTTS não disponível** no plano gratuito da API  
❌ **Modelos são probabilísticos** (não garantem lucro)  
❌ **Odds podem mudar** rapidamente  
❌ **Cache de 12h** (odds podem estar desatualizadas)  

### Recomendações

✅ Use como **ferramenta de análise**, não decisão final  
✅ **Confirme as odds** antes de apostar  
✅ **Aposte com responsabilidade**  
✅ **Gerencie sua banca** com Kelly Criterion  
✅ **Documente seus resultados**  

---

## 🔧 Configuração Avançada

### Alterar Casa de Apostas

Edite `config_economia.py`:

```python
# Trocar de Bet365 para outra casa
CASA_PREFERIDA = 'pinnacle'  # Ou outra disponível
```

**Casas disponíveis:**
- `bet365` (Bet365)
- `pinnacle` (Pinnacle)
- `betfair_ex_eu` (Betfair)
- `onexbet` (1xBet)

### Alterar Tempo de Cache

```python
# Em config_economia.py
CACHE_HORAS = 6  # 6 horas (mais atualizado, gasta mais requisições)
CACHE_HORAS = 24  # 24 horas (mais econômico)
```

### Incluir Mais Ligas

```python
# Em config.py, adicione novas ligas
LEAGUES = {
    'La Liga': {
        'code': 'LaLiga',
        'id': 2014,
        # ...
    }
}
```

---

## 📊 Economia de Requisições

### Custo por Análise

```
1 liga × 1 região × 2 mercados = 2 requisições

Brasileirão + Premier League = 4 requisições
```

### Com Cache de 12h

```
Manhã (09:00): 4 requisições
Tarde (15:00): 0 requisições (usa cache)
Noite (21:00): 4 requisições

Total/dia: 8 requisições
Total/mês: ~240 requisições

Sobra: 260 requisições
```

---

## 📁 Arquivos Relacionados

```
analises_esportivas_v3/
├── value_betting_auto.py          # Motor de value betting
├── config_economia.py              # Configurações
├── paginas/
│   └── value_bets_auto.py         # Interface Streamlit
├── COMO_USAR_VALUE_BETS_AUTO.md   # Este arquivo
└── app_betting.py                  # App principal (com nova aba)
```

---

## 🐛 Troubleshooting

### ❌ Erro: "ODDS_API_KEY não configurada"

**Solução:**
```bash
.\CRIAR_ENV_COM_API_KEY.bat
```

### ❌ Erro: "Nenhum value bet encontrado"

**Causas:**
- Não há jogos agendados
- Odds muito ajustadas
- Filtros muito restritivos

**Solução:**
- Reduzir value mínimo
- Selecionar mais ligas
- Aguardar novos jogos

### ❌ Erro: "Bet365 não disponível"

**Solução:**
A Bet365 pode não ter odds em determinados momentos. Tente:
```python
# Em config_economia.py
CASA_PREFERIDA = 'pinnacle'  # Ou outra
```

---

## 🎯 Exemplo de Uso Completo

### 1. Configurar
```bash
.\CRIAR_ENV_COM_API_KEY.bat
```

### 2. Iniciar Streamlit
```bash
streamlit run app_betting.py
```

### 3. Analisar
1. Aba "💰 Value Bets Automáticos"
2. Selecionar ligas: Brasileirão + Premier League
3. Value Mínimo: 5%
4. Ordenar por: EV (Maior)
5. Clicar "Atualizar"

### 4. Apostar
1. Ver Top 10
2. Escolher value bet com EV > 10%
3. Conferir odd na Bet365
4. Calcular stake com Kelly
5. Fazer aposta
6. Registrar resultado

---

## 📈 Resultados Esperados

### Com Uso Disciplinado

```
Value médio: 5-15%
EV médio: 3-10%
Taxa de acerto: 50-60%
ROI esperado: +5% a +15%
```

**Longo prazo:** Lucro consistente se:
- Seguir Kelly Criterion
- Apostar apenas value > 5%
- Gerenciar banca corretamente
- Documentar tudo

---

## 💚 Pronto para Usar!

Execute agora:

```bash
streamlit run app_betting.py
```

E acesse a aba **"💰 Value Bets Automáticos"**!

---

**Boa sorte e boas apostas! 🍀**

