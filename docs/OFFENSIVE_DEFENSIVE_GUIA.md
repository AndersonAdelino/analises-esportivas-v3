# 📊 Guia do Modelo Offensive-Defensive

## O que é o Modelo Offensive-Defensive?

O modelo Offensive-Defensive (também conhecido como Modelo de Maher, 1982) é uma abordagem estatística para predição de resultados de futebol que modela separadamente as capacidades ofensivas e defensivas dos times.

### Principais Características

1. **Baseado em Poisson**: Modela gols como distribuições de Poisson independentes
2. **Força Ofensiva (α)**: Capacidade de cada time marcar gols
3. **Força Defensiva (β)**: Capacidade de cada time evitar gols
4. **Home Advantage (γ)**: Vantagem de jogar em casa
5. **Simplicidade**: Menos parâmetros que Dixon-Coles

## 🎯 Como Funciona

### Fórmula Básica

**Gols esperados do time da casa:**
```
λ_casa = exp(γ + α_casa - β_visitante)
```

**Gols esperados do time visitante:**
```
λ_visitante = exp(α_visitante - β_casa)
```

### Parâmetros

- **α (alpha)**: Força de ataque do time
  - Valor positivo = ataque forte
  - Valor negativo = ataque fraco
  
- **β (beta)**: Força de defesa do time  
  - Valor negativo = defesa boa (sofre poucos gols)
  - Valor positivo = defesa ruim (sofre muitos gols)
  
- **γ (gamma)**: Home advantage (vantagem de jogar em casa)
  - Típico: 0.2 a 0.4

## 🚀 Como Usar

### 1. Script Básico

```bash
python offensive_defensive.py
```

**Saída:**
- Forças de ataque/defesa de cada time
- Home advantage calibrado
- Exemplos de predições

### 2. Predições para Próximas Partidas

```bash
python prever_com_offensive_defensive.py
```

Busca próximas partidas da API e gera predições automaticamente.

### 3. Comparação com Dixon-Coles

```bash
python comparar_modelos.py
```

Compara os dois modelos lado a lado para ver diferenças.

### 4. Uso Programático

```python
from offensive_defensive import OffensiveDefensiveModel, load_match_data

# Carrega dados
df = load_match_data()

# Treina modelo
model = OffensiveDefensiveModel(xi=0.003)
model.fit(df, time_decay=True)

# Fazer predição
pred = model.predict_match('Arsenal FC', 'Liverpool FC')

# Acessar resultados
print(f"Vitória Casa: {pred['prob_home_win']*100:.1f}%")
print(f"Over 2.5: {pred['prob_over_2_5']*100:.1f}%")
```

## 📊 Interpretando Resultados

### Forças dos Times (Exemplo)

```
Time                    Ataque    Defesa    Força Total
Liverpool FC             0.521    -0.074     0.596
AFC Bournemouth          0.340    -0.123     0.463
Arsenal FC               0.288     1.140    -0.853
```

**Interpretação:**

**Liverpool FC:**
- Ataque: 0.521 (muito bom)
- Defesa: -0.074 (boa, sofre poucos gols)
- Força Total: 0.596 (time forte)

**Arsenal FC:**
- Ataque: 0.288 (razoável)
- Defesa: 1.140 (RUIM, sofre muitos gols)
- Força Total: -0.853 (time fraco no geral)

### Predições

**Arsenal vs Manchester City:**
```
Gols Esperados:
  Arsenal: 1.06
  Man City: 0.56

Probabilidades:
  Vitória Arsenal: 47.3%
  Empate: 33.4%
  Vitória Man City: 19.3%

Over 2.5: 22.2%
BTTS: 28.1%

Placar mais provável: 1-0 (20.95%)
```

## 🆚 Offensive-Defensive vs Dixon-Coles

### Semelhanças

✅ Ambos baseados em Poisson
✅ Modelam ataque e defesa separadamente
✅ Consideram home advantage
✅ Usam otimização matemática

### Diferenças

| Aspecto | Offensive-Defensive | Dixon-Coles |
|---------|-------------------|-------------|
| **Complexidade** | Média | Alta |
| **Parâmetro Rho** | ❌ Não | ✅ Sim |
| **Independência** | Assume gols independentes | Correlação para placares baixos |
| **Velocidade** | Rápido | Mais lento |
| **Interpretabilidade** | Fácil | Média |
| **Precisão Empates 0-0** | Pode subestimar | Melhor calibrado |

### Quando Usar Cada Um?

**Use Offensive-Defensive quando:**
- ⚡ Precisa de predições rápidas
- 📚 Tem poucos dados históricos
- 🎓 Quer algo fácil de explicar
- 🔄 Está fazendo análises exploratórias

**Use Dixon-Coles quando:**
- 🎯 Precisa de máxima precisão
- 💰 Está apostando profissionalmente
- 📊 Tem muitos dados disponíveis
- 🔬 Foco em placares exatos (especialmente baixos)

### Diferenças nas Predições

**Exemplo Real - Arsenal vs Man City:**

```
Métrica              Off-Defensive    Dixon-Coles    Diferença
Vitória Casa         47.3%            45.5%          1.8 pp
Empate               33.4%            37.4%          4.0 pp
Vitória Fora         19.3%            17.1%          2.2 pp
Over 2.5             22.2%            21.1%          1.1 pp
```

**Conclusão:** Modelos muito concordantes (diferenças < 5pp)

## 💡 Dicas de Uso

### 1. Combinando os Dois Modelos

```python
# Treina ambos
model_od = OffensiveDefensiveModel(xi=0.003)
model_od.fit(df)

model_dc = DixonColesModel(xi=0.003)
model_dc.fit(df)

# Compara predições
pred_od = model_od.predict_match('Arsenal FC', 'Liverpool FC')
pred_dc = model_dc.predict_match('Arsenal FC', 'Liverpool FC')

# Se concordam -> maior confiança
# Se discordam -> mais cautela
```

### 2. Ajustando Decaimento Temporal (xi)

```python
# Sem decaimento (todos os jogos iguais)
model = OffensiveDefensiveModel(xi=0.0)

# Decaimento suave (recomendado)
model = OffensiveDefensiveModel(xi=0.003)

# Decaimento forte (só jogos recentes)
model = OffensiveDefensiveModel(xi=0.01)
```

**Recomendação:** Use xi=0.003 para ligas estáveis

### 3. Identificando Value Bets

```python
pred = model.predict_match('Arsenal FC', 'Liverpool FC')

# Odds da casa de apostas
odds_casa = 2.20  # Arsenal

# Probabilidade implícita
prob_impl = 1 / odds_casa  # 45.5%

# Probabilidade do modelo
prob_modelo = pred['prob_home_win']  # 47.3%

# Value = prob_modelo / prob_impl
value = prob_modelo / prob_impl  # 1.04 (4% de value)

if value > 1.10:  # 10% de margem
    print("VALUE BET encontrado!")
```

### 4. Análise de Sensibilidade

Teste como mudanças na força afetam predições:

```python
# Time original
pred1 = model.predict_match('Arsenal FC', 'Chelsea FC')

# Simula melhora no ataque do Arsenal
model.attack['Arsenal FC'] += 0.1
pred2 = model.predict_match('Arsenal FC', 'Chelsea FC')

print(f"Aumento de vitória: {(pred2['prob_home_win'] - pred1['prob_home_win'])*100:.1f}%")
```

## 📈 Vantagens e Limitações

### ✅ Vantagens

1. **Simplicidade**: Fácil de entender e implementar
2. **Velocidade**: Treina muito rápido
3. **Interpretabilidade**: Parâmetros têm significado claro
4. **Robustez**: Menos propenso a overfitting
5. **Eficiência**: Bom custo-benefício (precisão vs complexidade)

### ⚠️ Limitações

1. **Independência**: Assume que gols são independentes
2. **Empates 0-0**: Pode subestimar (não tem correção rho)
3. **Eventos Raros**: Menos preciso para placares incomuns
4. **Contexto**: Não considera motivação, lesões, etc.

## 🔍 Validação do Modelo

### Métricas Recomendadas

```python
# Brier Score (quanto menor, melhor)
def brier_score(predictions, outcomes):
    return np.mean((predictions - outcomes)**2)

# Log Loss
from sklearn.metrics import log_loss
score = log_loss(y_true, y_pred)

# ROI Simulado
# (simula apostas e calcula retorno)
```

### Cross-Validation

```python
# Separa treino/teste por tempo
df_treino = df[df['data'] < '2025-09-01']
df_teste = df[df['data'] >= '2025-09-01']

# Treina
model.fit(df_treino)

# Testa
for _, jogo in df_teste.iterrows():
    pred = model.predict_match(jogo['time_casa'], jogo['time_visitante'])
    # ... calcula métricas
```

## 📚 Referências

**Paper Original:**
Maher, M. J. (1982). *Modelling association football scores*. Statistica Neerlandica, 36(3), 109-118.

**Leituras Complementares:**
- Dixon & Coles (1997) - Extensão com parâmetro Rho
- Karlis & Ntzoufras (2003) - Modelos bivariados de Poisson
- Rue & Salvesen (2000) - Bayesian approach

## 🆘 Troubleshooting

### "Time não encontrado no modelo"
```python
# Listar times disponíveis
print(model.teams)

# Verificar nome exato
teams = [t for t in model.teams if 'Arsenal' in t]
print(teams)
```

### Probabilidades estranhas
```python
# Verificar dados de entrada
print(df[['time_casa', 'gols_casa', 'time_visitante', 'gols_visitante']].describe())

# Verificar convergência
# Se log-likelihood muito alto -> problema nos dados
```

### Modelo não converge
```python
# Aumentar iterações
# Edite offensive_defensive.py, linha com maxiter
options={'maxiter': 200}

# Ou tente outro método
method='L-BFGS-B'
```

## 🎓 Exemplos Avançados

### Ensemble (Média dos Modelos)

```python
pred_od = model_od.predict_match('Arsenal FC', 'Liverpool FC')
pred_dc = model_dc.predict_match('Arsenal FC', 'Liverpool FC')

# Média simples
prob_home_ensemble = (pred_od['prob_home_win'] + pred_dc['prob_home_win']) / 2
prob_draw_ensemble = (pred_od['prob_draw'] + pred_dc['prob_draw']) / 2
prob_away_ensemble = (pred_od['prob_away_win'] + pred_dc['prob_away_win']) / 2

print(f"Ensemble - Vitória Casa: {prob_home_ensemble*100:.1f}%")
```

### Simulação de Monte Carlo

```python
import numpy as np

# Simula 10.000 partidas
n_sims = 10000
lambda_home, lambda_away = model.predict_goals('Arsenal FC', 'Liverpool FC')

results = {'Casa': 0, 'Empate': 0, 'Fora': 0}

for _ in range(n_sims):
    gols_casa = np.random.poisson(lambda_home)
    gols_fora = np.random.poisson(lambda_away)
    
    if gols_casa > gols_fora:
        results['Casa'] += 1
    elif gols_casa < gols_fora:
        results['Fora'] += 1
    else:
        results['Empate'] += 1

for key, valor in results.items():
    print(f"{key}: {valor/n_sims*100:.1f}%")
```

---

**Desenvolvido para o projeto de Análises Esportivas**
Última atualização: Outubro 2025

