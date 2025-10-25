# 📊 Guia de Validação e Backtesting

## 🎯 Visão Geral

Sistema completo de **validação** e **backtesting** dos modelos preditivos, com métricas estatísticas e simulação de estratégias de apostas.

## 🚀 Como Usar

### Instalação

Todas as dependências já estão em `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Validação Rápida

```bash
python validation.py
```

Isso irá:
1. Validar Dixon-Coles (3 splits)
2. Validar Offensive-Defensive (3 splits)
3. Exibir métricas comparativas
4. Salvar resultados em `data/validation/`

---

## 📈 Métricas Calculadas

### 1. Brier Score

**O que é:** Mede a acurácia das probabilidades preditas.

**Fórmula:**
```
Brier Score = (1/N) × Σ(prob_predita - resultado_real)²
```

**Interpretação:**
- **0.00 - 0.15:** Excelente
- **0.15 - 0.20:** Muito bom
- **0.20 - 0.25:** Bom
- **> 0.25:** Precisa melhorar

**Exemplo:**
```
Brier Score: 0.182 ± 0.012
(Menor é melhor. Ideal: < 0.20)
```

### 2. Log Loss

**O que é:** Penaliza predições muito confiantes e erradas.

**Interpretação:**
- **< 0.60:** Excelente
- **0.60 - 0.80:** Muito bom
- **0.80 - 1.00:** Bom
- **> 1.00:** Precisa melhorar

**Exemplo:**
```
Log Loss: 0.876 ± 0.045
(Menor é melhor. Ideal: < 1.0)
```

### 3. ROI (Return on Investment)

**O que é:** Retorno financeiro simulado usando Kelly Criterion.

**Fórmula:**
```
ROI% = (Lucro Total / Total Apostado) × 100
```

**Interpretação:**
- **> +10%:** Excelente
- **+5% a +10%:** Muito bom
- **+2% a +5%:** Bom
- **0% a +2%:** Break-even
- **< 0%:** Negativo (ajustar estratégia)

**Exemplo:**
```
ROI Simulado: +8.45% ± 3.21%
Min: +2.10% | Max: +15.32%
(Positivo indica lucro)
```

### 4. Win Rate

**O que é:** Percentual de apostas ganhas.

**Interpretação:**
- Com value betting, **45-55%** de acerto pode ser lucrativo se EV for positivo
- Win rate alto sem ROI positivo = Sem value betting adequado
- Win rate baixo com ROI positivo = Apostas em underdogs valiosos

**Exemplo:**
```
Win Rate: 52.3% ± 4.1%
(% de apostas ganhas)
```

---

## 🔬 Cross-Validation Temporal

### Como Funciona

O sistema usa **validação temporal** (não aleatória) para respeitar a ordem cronológica:

```
Dados ordenados por data:
[========================================]
 
Split 1:
[====treino====][teste1]
 
Split 2:
[======treino======][teste2]
 
Split 3:
[========treino========][teste3]
```

**Por que temporal?**
- Evita "olhar para o futuro"
- Simula uso real do modelo
- Mais realista que k-fold aleatório

### Número de Splits

```python
validator = ModelValidator(model, df, "Dixon-Coles")
results = validator.cross_validate(n_splits=5)
```

**Recomendações:**
- **3 splits:** Rápido, para testes
- **5 splits:** Balanceado (padrão)
- **10 splits:** Mais robusto, mas lento

---

## 💰 Simulação de Apostas

### Estratégia Implementada

O sistema simula apostas usando **Kelly Criterion**:

```python
# Para cada partida no período de teste:
1. Calcula probabilidade (modelo)
2. Simula odds da casa (fair odds - margem)
3. Calcula Kelly%: (p × odds - 1) / (odds - 1)
4. Aplica fração de Kelly (padrão: 0.25)
5. Aposta se Kelly > 1% da banca
6. Atualiza banca com resultado real
```

### Parâmetros Configuráveis

```python
betting_results = validator.simulate_betting(
    test_df=test_data,
    predictions=predictions,
    initial_bankroll=1000.0,      # Banca inicial
    kelly_fraction=0.25,           # Conservador
    bookmaker_margin=0.05          # Margem da casa (5%)
)
```

### Resultados da Simulação

```python
{
    'initial_bankroll': 1000.0,
    'final_bankroll': 1084.5,
    'total_staked': 450.0,
    'total_profit': 84.5,
    'roi_percent': 18.78,
    'bets_made': 12,
    'bets_won': 7,
    'win_rate': 58.33,
    'bet_history': [...]  # Detalhes de cada aposta
}
```

---

## 📊 Uso Programático

### Validar um Modelo

```python
from validation import ModelValidator
from dixon_coles import DixonColesModel, load_match_data

# Carrega dados
df = load_match_data()

# Cria e treina modelo
model = DixonColesModel(xi=0.003)

# Valida
validator = ModelValidator(model, df, "Dixon-Coles")
results = validator.cross_validate(n_splits=5, save_results=True)

# Exibe
validator.print_results(results)
```

### Comparar Modelos

```python
from validation import compare_models
from dixon_coles import DixonColesModel, load_match_data
from offensive_defensive import OffensiveDefensiveModel

df = load_match_data()

models = {
    'Dixon-Coles': (DixonColesModel(xi=0.003), DixonColesModel),
    'Offensive-Defensive': (OffensiveDefensiveModel(xi=0.003), OffensiveDefensiveModel)
}

comparison = compare_models(models, df, n_splits=5)
```

### Acessar Resultados Salvos

```python
import json

# Carrega resultados
with open('data/validation/dixon_coles_validation.json', 'r') as f:
    results = json.load(f)

# Acessa métricas
print(f"Brier Score: {results['brier_score']['mean']:.4f}")
print(f"ROI: {results['roi_percent']['mean']:.2f}%")

# Acessa resultados de cada fold
for i, fold in enumerate(results['fold_results'], 1):
    print(f"Fold {i}: ROI = {fold['roi_percent']:.2f}%")
```

---

## 🎯 Interpretando Resultados

### Exemplo de Saída

```
============================================================
📊 RESULTADOS DA VALIDAÇÃO - Dixon-Coles
============================================================

🎯 Brier Score: 0.1823 ± 0.0124
   (Menor é melhor. Ideal: < 0.20)

📉 Log Loss: 0.8765 ± 0.0453
   (Menor é melhor. Ideal: < 1.0)

💰 ROI Simulado: +8.45% ± 3.21%
   Min: +2.10% | Max: +15.32%
   (Positivo indica lucro)

🎲 Win Rate: 52.3% ± 4.1%
   (% de apostas ganhas)

============================================================
```

### O Que Isso Significa?

✅ **Brier Score = 0.182**
- Modelo tem probabilidades bem calibradas
- Abaixo de 0.20 = Muito bom!

✅ **Log Loss = 0.876**
- Modelo não faz predições overconfident incorretas
- Abaixo de 1.0 = Bom!

✅ **ROI = +8.45%**
- Estratégia simulada é lucrativa
- A cada R$ 100 apostados, lucra ~R$ 8.50
- **IMPORTANTE:** Isso é em simulação, não garantia

✅ **Win Rate = 52.3%**
- Acerta pouco mais da metade das apostas
- Com ROI positivo, indica apostas valiosas

⚠️ **Desvio Padrão**
- ± 3.21% no ROI indica variância
- Alguns períodos melhor/pior que outros
- Normal em apostas

---

## 📁 Arquivos Gerados

### Estrutura

```
data/validation/
├── dixon_coles_validation.json
├── offensive_defensive_validation.json
├── heuristicas_validation.json
├── ensemble_validation.json
└── model_comparison.json
```

### Conteúdo dos Arquivos

```json
{
  "model_name": "Dixon-Coles",
  "n_splits": 5,
  "brier_score": {
    "mean": 0.1823,
    "std": 0.0124,
    "min": 0.1654,
    "max": 0.2001
  },
  "log_loss": {
    "mean": 0.8765,
    "std": 0.0453,
    "min": 0.8234,
    "max": 0.9456
  },
  "roi_percent": {
    "mean": 8.45,
    "std": 3.21,
    "min": 2.10,
    "max": 15.32
  },
  "win_rate": {
    "mean": 52.3,
    "std": 4.1
  },
  "fold_results": [...],
  "timestamp": "2025-10-25T14:30:00"
}
```

---

## 🏆 Ranking de Modelos

### Por ROI

```
📈 Por ROI:
  1. Dixon-Coles: +8.45%
  2. Ensemble: +7.23%
  3. Offensive-Defensive: +5.67%
  4. Heurísticas: +3.21%
```

### Por Brier Score

```
🎯 Por Brier Score (menor é melhor):
  1. Dixon-Coles: 0.1823
  2. Offensive-Defensive: 0.1956
  3. Ensemble: 0.2012
  4. Heurísticas: 0.2234
```

### Como Escolher?

- **ROI:** Melhor para lucro financeiro
- **Brier Score:** Melhor para probabilidades precisas
- **Ensemble:** Geralmente melhor balanceado

---

## 🔧 Customização

### Ajustar Margem da Casa

```python
# Casa mais generosa (margem menor)
betting_results = validator.simulate_betting(
    test_df=test_data,
    predictions=predictions,
    bookmaker_margin=0.03  # 3%
)

# Casa mais gananciosa (margem maior)
betting_results = validator.simulate_betting(
    test_df=test_data,
    predictions=predictions,
    bookmaker_margin=0.08  # 8%
)
```

### Ajustar Kelly Fraction

```python
# Mais conservador
betting_results = validator.simulate_betting(
    kelly_fraction=0.10  # 10% do Kelly
)

# Mais agressivo (cuidado!)
betting_results = validator.simulate_betting(
    kelly_fraction=0.50  # 50% do Kelly
)
```

### Validar Apenas Período Específico

```python
# Filtra dados por data
df_2024 = df[df['data'] >= '2024-01-01']

validator = ModelValidator(model, df_2024, "Dixon-Coles 2024")
results = validator.cross_validate(n_splits=3)
```

---

## 📚 Boas Práticas

### 1. Valide Regularmente

```bash
# Toda semana após coletar novos dados
python get_team_matches.py  # Atualiza dados
python validation.py         # Re-valida modelos
```

### 2. Compare Períodos

```python
# Valida primeiro semestre
validator_h1 = ModelValidator(model, df_primeiro_semestre, "DC H1")
results_h1 = validator_h1.cross_validate()

# Valida segundo semestre
validator_h2 = ModelValidator(model, df_segundo_semestre, "DC H2")
results_h2 = validator_h2.cross_validate()

# Compara
print(f"ROI H1: {results_h1['roi_percent']['mean']:.2f}%")
print(f"ROI H2: {results_h2['roi_percent']['mean']:.2f}%")
```

### 3. Teste Diferentes Parâmetros

```python
# Teste diferentes xis (decaimento temporal)
for xi in [0.001, 0.003, 0.005, 0.010]:
    model = DixonColesModel(xi=xi)
    validator = ModelValidator(model, df, f"DC xi={xi}")
    results = validator.cross_validate(n_splits=3)
    print(f"xi={xi}: ROI={results['roi_percent']['mean']:.2f}%")
```

### 4. Guarde Histórico

```bash
# Crie backups mensais
cp data/validation/dixon_coles_validation.json \
   data/validation/backups/dixon_coles_2025_10.json
```

---

## ⚠️ Avisos Importantes

### 1. Simulação ≠ Realidade

Os resultados são **simulações**:
- Odds simuladas podem diferir das reais
- Não considera limitações de stake
- Não considera odds em movimento
- Liquidez pode ser um problema

### 2. Overfitting

Se ROI da validação >> ROI real:
- Modelo pode estar overfitted
- Aumente dados de treinamento
- Reduza complexidade do modelo
- Use regularização

### 3. Variância

ROI tem alta variância:
- 100 apostas não são suficientes
- Resultados em 1000+ apostas são mais confiáveis
- Desvio padrão indica incerteza

### 4. Contexto Muda

Modelos degradam com tempo:
- Retreine regularmente
- Monitore performance real
- Ajuste estratégia conforme necessário

---

## 🎓 Conclusão

Validação adequada:
- ✅ Identifica modelos realmente bons
- ✅ Previne overfitting
- ✅ Estima performance realista
- ✅ Permite comparação justa

**Sempre valide antes de apostar dinheiro real!**

---

## 📖 Referências

### Papers Acadêmicos
- Constantinou & Fenton (2012) - "Solving the problem of inadequate scoring rules"
- Hubáček et al. (2019) - "Exploiting Sports-Betting Market Using Machine Learning"

### Livros
- "Thinking in Bets" - Annie Duke
- "The Signal and the Noise" - Nate Silver

---

**Desenvolvido para o projeto de Análises Esportivas v3**

*Última atualização: Outubro 2025*

