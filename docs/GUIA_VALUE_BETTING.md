# 📚 Guia Completo: Value Betting System

## 🎯 Visão Geral

Sistema completo de **Value Betting** que combina:
- **3 Modelos Preditivos** com pesos ajustáveis
- **Expected Value (EV)** - Identificação de apostas com valor
- **Kelly Criterion** - Gestão de banca otimizada
- **Interface Web** - Análise interativa com Streamlit

---

## 🏗️ Arquitetura do Sistema

### 1. Ensemble de Modelos (`ensemble.py`)

Combina predições dos 3 modelos com pesos configuráveis:

```python
Pesos Padrão:
- Dixon-Coles: 55%
- Offensive-Defensive: 30%
- Heurísticas: 15%
```

**Por que esses pesos?**
- **Dixon-Coles** tem maior peso por ser estatisticamente mais robusto
- **Offensive-Defensive** complementa com análise de forças
- **Heurísticas** capturam padrões e momentum recente

**Como funciona:**
1. Cada modelo gera probabilidades independentes
2. Probabilidades são combinadas usando média ponderada
3. Resultado: probabilidade ensemble para cada mercado

---

### 2. Ferramentas de Apostas (`betting_tools.py`)

#### Expected Value (EV)

**Fórmula:**
```
EV = (Probabilidade de Ganhar × Lucro) - (Probabilidade de Perder × Stake)
```

**Interpretação:**
- **EV > 0**: Value bet (apostar!)
- **EV = 0**: Break-even (evitar)
- **EV < 0**: Aposta desfavorável (não apostar)

**Exemplo:**
```python
Prob. Real: 60%
Odds: 2.00 (implica 50%)
Edge: +10%

EV = (0.60 × R$ 1.00) - (0.40 × R$ 1.00) = +R$ 0.20 (por R$ 1)
EV% = +20%
```

---

#### Kelly Criterion

**Fórmula:**
```
Kelly% = (prob_win × odds - 1) / (odds - 1)
```

**Fração de Kelly:**
- **Full Kelly (1.0)**: Máximo crescimento, alta volatilidade
- **Half Kelly (0.5)**: Moderado, recomendado para médio prazo
- **Quarter Kelly (0.25)**: Conservador, recomendado para longo prazo ✅

**Por que usar fração?**
- Protege contra erros de estimativa
- Reduz volatilidade
- Mais seguro para apostadores reais

**Exemplo:**
```python
Prob. Win: 60%
Odds: 2.00
Kelly Full: 20% da banca
Kelly Quarter (0.25): 5% da banca ← Recomendado
```

---

### 3. Interface Web (`app_betting.py`)

Interface desenvolvida em **Streamlit** com:
- ✅ Seleção de partidas (busca API)
- ✅ Input de odds (casa, empate, fora, over/under, btts)
- ✅ Configuração de banca e Kelly fraction
- ✅ Análise automática de value bets
- ✅ Recomendações de stake

---

## 🚀 Como Usar

### Instalação

```bash
# 1. Instalar Streamlit (se ainda não tiver)
pip install streamlit

# Ou atualizar requirements.txt
pip install -r requirements.txt
```

### Executar a Interface Web

```bash
streamlit run app_betting.py
```

**O navegador abrirá automaticamente!** 🌐

---

## 📖 Passo a Passo na Interface

### 1. Aguarde o carregamento dos modelos
- Os 3 modelos serão treinados automaticamente
- Leva ~5-10 segundos

### 2. Selecione uma partida
- Lista mostra próximas partidas da Premier League
- Formato: "Time Casa vs Time Fora - Data"

### 3. Insira as Odds
- **Resultado (1X2)**:
  - Vitória Casa
  - Empate
  - Vitória Fora
- **Over/Under 2.5 Gols**:
  - Over 2.5
  - Under 2.5
- **Both Teams to Score (BTTS)**:
  - BTTS Sim
  - BTTS Não

**💡 Dica:** Use odds de casas confiáveis (Bet365, Betfair, etc.)

### 4. Configure a Banca
- **Banca Total**: Seu capital disponível para apostas
- **Kelly Fraction**: Recomendado 0.25 (conservador)

### 5. Clique em "ANALISAR"
- Sistema calcula probabilidades do ensemble
- Identifica value bets em todos os mercados
- Mostra recomendações de stake

### 6. Interprete os Resultados

**Probabilidades do Ensemble:**
- Mostra % de chance segundo os modelos combinados

**Value Bets Identificados:**
- Expandir cada mercado para ver detalhes
- **Odds & Probabilidades**: Comparação modelo vs casa
- **Expected Value**: EV%, ROI, Edge
- **Kelly Criterion**: % recomendado da banca
- **Stake**: Quanto apostar em R$

**Tabela Resumo:**
- Visão geral de todos os mercados
- ✅ = Value bet
- ❌ = Sem value

---

## 💡 Casos de Uso

### Caso 1: Value Bet Claro

```
Arsenal vs Liverpool
Odds Casa: 2.50
Prob. Ensemble: 50%
Prob. Implícita: 40%

Edge: +10%
EV%: +25%
Kelly (0.25): 3.1%

>>> APOSTAR R$ 31 (3.1% de R$ 1000)
```

### Caso 2: Sem Value

```
Manchester City vs Brighton
Odds Casa: 1.30
Prob. Ensemble: 70%
Prob. Implícita: 77%

Edge: -7%
EV%: -9%

>>> NÃO APOSTAR
```

### Caso 3: Value em Mercado Alternativo

```
Chelsea vs Newcastle
1X2: Sem value
Over 2.5: 2.10 (Ensemble: 55%, Casa: 48%)

Edge: +7%
EV%: +15%
Kelly (0.25): 1.9%

>>> APOSTAR R$ 19 em Over 2.5
```

---

## 📊 Interpretação de Métricas

### Edge (Vantagem)

| Edge | Significado | Ação |
|------|-------------|------|
| > +5% | Vantagem forte | ✅ Considerar apostar |
| +2% a +5% | Vantagem moderada | ⚠️ Avaliar |
| 0% a +2% | Vantagem fraca | ❌ Evitar |
| < 0% | Desvantagem | ❌ Não apostar |

### EV% (Expected Value %)

| EV% | Qualidade | Recomendação |
|-----|-----------|--------------|
| > +15% | Excelente | ✅✅ Forte aposta |
| +10% a +15% | Muito boa | ✅ Boa aposta |
| +5% a +10% | Boa | ✅ Apostar |
| +2% a +5% | Marginal | ⚠️ Cauteloso |
| < +2% | Fraco | ❌ Evitar |

### Kelly Adjusted (%)

| Kelly% | Stake | Perfil |
|--------|-------|--------|
| > 5% | Alto | Agressivo |
| 2% - 5% | Moderado | Balanceado |
| 1% - 2% | Baixo | Conservador |
| < 1% | Mínimo | Muito cauteloso |

---

## ⚙️ Configurações Avançadas

### Ajustar Pesos do Ensemble

Edite `ensemble.py`:

```python
weights = {
    'dixon_coles': 0.60,          # 60%
    'offensive_defensive': 0.25,   # 25%
    'heuristicas': 0.15           # 15%
}

ensemble = EnsembleModel(weights=weights)
```

### Ajustar Kelly Fraction

Na interface:
- **0.10**: Ultra-conservador (crescimento muito lento)
- **0.25**: Conservador (recomendado) ✅
- **0.50**: Moderado (mais agressivo)
- **1.00**: Full Kelly (volatilidade alta)

### Uso Programático

```python
from ensemble import EnsembleModel
from betting_tools import analyze_bet

# Treina ensemble
ensemble = EnsembleModel()
ensemble.fit()

# Predição
pred = ensemble.predict_match('Arsenal FC', 'Liverpool FC')
prob_casa = pred['ensemble']['prob_casa']

# Análise de aposta
analysis = analyze_bet(
    prob_win=prob_casa,
    odds_decimal=2.50,
    bankroll=1000,
    kelly_fraction=0.25
)

print(f"EV%: {analysis['ev']['ev_percent']:.2f}%")
print(f"Apostar: R$ {analysis['stake_recommended']:.2f}")
```

---

## 🎓 Conceitos Importantes

### 1. Probabilidade Implícita

Probabilidade que as odds da casa sugerem:
```
Prob. Implícita = 1 / Odds
```

Exemplo:
- Odds 2.00 → 50%
- Odds 3.00 → 33.3%
- Odds 1.50 → 66.7%

### 2. Margem da Casa (Overround)

Casas de apostas ajustam odds para garantir lucro:
```
Margem = (1/Odds_Casa + 1/Odds_Empate + 1/Odds_Fora) - 1
```

Exemplo:
```
Odds: 2.00 / 3.50 / 3.80
Margem: (0.50 + 0.286 + 0.263) - 1 = 4.9%
```

A casa sempre ganha 4.9% independente do resultado!

### 3. Value Betting vs Arbitragem

| Aspecto | Value Betting | Arbitragem |
|---------|---------------|------------|
| Risco | Sim (apostas individuais) | Não (cobertura total) |
| Lucro | Longo prazo (variância) | Garantido (imediato) |
| Vantagem | Modelo melhor que casa | Diferença entre casas |
| Dificuldade | Modelagem precisa | Encontrar oportunidades |

**Value betting requer:**
- Modelo de probabilidades preciso
- Gestão de banca (Kelly)
- Disciplina (apostar apenas value bets)
- Paciência (resultados no longo prazo)

---

## ⚠️ Avisos Importantes

### 1. Gestão de Banca
- **NUNCA** aposte mais que 5% em uma única aposta
- Use Kelly Quarter (0.25) para segurança
- Mantenha registro de todas as apostas

### 2. Variância
- Value bets podem perder (normal!)
- Lucro vem no longo prazo (100+ apostas)
- Expectativa positiva ≠ Garantia de vitória

### 3. Odds Reais
- Use odds reais de casas confiáveis
- Odds mudam constantemente
- Compare múltiplas casas

### 4. Limitações do Modelo
- Modelos não são perfeitos
- Eventos imprevisíveis acontecem
- Use como ferramenta, não certeza absoluta

### 5. Jogo Responsável
- **Aposte apenas o que pode perder**
- Não persiga perdas
- Faça pausas regulares
- Se sentir problema, procure ajuda

---

## 📈 Rastreamento de Performance

### Métricas para Acompanhar

```python
# Criar planilha com:
- Data
- Partida
- Mercado apostado
- Odds
- Prob. Modelo
- Stake (R$)
- Resultado (Ganhou/Perdeu)
- Lucro/Perda (R$)
- ROI Acumulado (%)
- Banca Atual (R$)
```

### Análise de Resultados

Após 50+ apostas:
```python
ROI% = (Lucro Total / Total Apostado) × 100

Ideal: ROI > +5% (longo prazo)
Bom: ROI > +10%
Excelente: ROI > +15%
```

### Brier Score

Mede qualidade das probabilidades:
```python
Brier Score = (1/N) × Σ(prob_pred - resultado)²

Ideal: < 0.20
Bom: 0.20 - 0.25
Ruim: > 0.25
```

---

## 🛠️ Troubleshooting

### Problema: "Nenhum Value Bet Encontrado"
**Solução:** Normal! Nem toda partida tem value. Espere outras oportunidades.

### Problema: "Kelly% muito alto (> 10%)"
**Solução:** Pode indicar odds muito favoráveis OU erro do modelo. Use cautela.

### Problema: "Modelos divergem muito"
**Solução:** Incerteza alta. Reduzir stake ou evitar aposta.

### Problema: "Sequência de perdas"
**Solução:** Variância normal. Revise gestão de banca e continue se EV positivo.

---

## 📚 Recursos Adicionais

### Livros Recomendados
- "Trading Bases" - Joe Peta
- "The Signal and the Noise" - Nate Silver
- "Fortune's Formula" - William Poundstone (Kelly Criterion)

### Papers Acadêmicos
- Dixon & Coles (1997) - Modelo original
- Karlis & Ntzoufras (2003) - Modelos de Poisson
- Kelly (1956) - Information Theory and Gambling

### Ferramentas Online
- Oddschecker - Comparação de odds
- Betfair Exchange - Odds do mercado
- Soccerway - Estatísticas de futebol

---

## ✅ Checklist do Apostador Disciplinado

Antes de cada aposta:
- [ ] EV positivo confirmado?
- [ ] Edge > +3%?
- [ ] Kelly < 5% da banca?
- [ ] Odds verificadas em múltiplas casas?
- [ ] Banca ainda permite a aposta?
- [ ] Registro na planilha pronto?
- [ ] Emocionalmente estável (sem tilt)?

---

**Desenvolvido para apostadores inteligentes! 🧠⚽💰**

*Lembre-se: Value betting é maratona, não sprint.*

*Última atualização: Outubro 2024*

