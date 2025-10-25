# 🔮 Guia do Modelo Dixon-Coles

## O que é o Modelo Dixon-Coles?

O modelo Dixon-Coles é um modelo estatístico avançado para predição de resultados de futebol, publicado em 1997 por Mark J. Dixon e Stuart G. Coles. É amplamente utilizado por profissionais de apostas esportivas e analistas.

### Principais Características

1. **Baseado em Poisson**: Modela gols como distribuições de Poisson independentes
2. **Correção Rho**: Ajusta probabilidades para placares baixos (0-0, 1-0, 0-1, 1-1)
3. **Força de Ataque/Defesa**: Cada time tem parâmetros de ataque e defesa
4. **Home Advantage**: Considera a vantagem de jogar em casa
5. **Decaimento Temporal**: Dá mais peso a partidas recentes (opcional)

## 📊 Como Funciona

### Parâmetros do Modelo

- **α (alpha)**: Força de ataque do time
- **β (beta)**: Força de defesa do time
- **γ (gamma)**: Vantagem de jogar em casa
- **ρ (rho)**: Parâmetro de correlação para placares baixos

### Fórmula Básica

Gols esperados para o time da casa:
```
λ_casa = exp(γ + α_casa - β_visitante)
```

Gols esperados para o time visitante:
```
λ_visitante = exp(α_visitante - β_casa)
```

## 🚀 Como Usar

### 1. Script Básico (dixon_coles.py)

Execute o script principal para treinar o modelo e ver exemplos:

```bash
python dixon_coles.py
```

**Saída:**
- Força de ataque/defesa de cada time
- Exemplos de predições (Arsenal vs City, Liverpool vs Chelsea, etc.)
- Home advantage e rho calculados

### 2. Script Interativo (predicao_interativa.py)

Interface interativa para fazer predições customizadas:

```bash
python predicao_interativa.py
```

**Funcionalidades:**
- Escolher times de uma lista
- Ver predições detalhadas
- Salvar predições em arquivo .txt
- Consultar forças dos times

**Menu:**
1. Fazer predição
2. Ver forças dos times
3. Listar times disponíveis
4. Sair

### 3. Gerador de Predições em Lote (gerar_predicoes_lote.py)

Gera múltiplas predições e salva em CSV:

```bash
python gerar_predicoes_lote.py
```

**Opções:**
1. **Top 10 times (todos vs todos)**: Gera ~90 predições dos melhores times
2. **Partidas específicas**: Predições para lista customizada de jogos

**Arquivo gerado:** `data/predicoes_dixon_coles_YYYYMMDD_HHMMSS.csv`

### 4. Uso Programático

```python
from dixon_coles import DixonColesModel, load_match_data

# Carrega dados
df = load_match_data()

# Treina modelo
model = DixonColesModel(xi=0.003)  # xi = decaimento temporal
model.fit(df, time_decay=True)

# Fazer predição
prediction = model.predict_match('Arsenal FC', 'Liverpool FC')

# Acessar resultados
print(f"Vitória Casa: {prediction['prob_home_win']*100:.1f}%")
print(f"Empate: {prediction['prob_draw']*100:.1f}%")
print(f"Vitória Fora: {prediction['prob_away_win']*100:.1f}%")
print(f"Over 2.5: {prediction['prob_over_2_5']*100:.1f}%")
print(f"BTTS: {prediction['prob_btts_yes']*100:.1f}%")

# Top 5 placares
for (home_g, away_g), prob in prediction['top_scores'][:5]:
    print(f"{home_g}-{away_g}: {prob*100:.2f}%")
```

## 📈 Interpretando os Resultados

### 1. Forças dos Times

**Ataque positivo = melhor ataque**
- Liverpool: 0.515 (excelente)
- Arsenal: 0.278 (bom)
- Wolves: -0.554 (fraco)

**Defesa negativa = melhor defesa**
- AFC Bournemouth: -0.095 (boa)
- Arsenal: 1.183 (ruim - sofre muitos gols)

**Força Total = Ataque - Defesa**
- Quanto maior, melhor o time em geral

### 2. Home Advantage (γ)

Valor típico: **0.2 a 0.4**

No nosso modelo: **0.272**
- Significa ~31% mais gols esperados jogando em casa

### 3. Rho (ρ) - Correlação

- **ρ < 0**: Menos empates 0-0 e 1-1 que o esperado (comum)
- **ρ > 0**: Mais empates baixos
- **ρ = 0**: Gols são independentes (Poisson puro)

No nosso modelo: **-0.150**
- Indica menos placares baixos que o modelo Poisson puro preveria

### 4. Probabilidades

**1X2 (Resultado):**
- Vitória Casa: 45.5%
- Empate: 37.4%
- Vitória Fora: 17.1%

**Over/Under 2.5 Gols:**
- Over: 69.1% (provável jogo com muitos gols)
- Under: 30.9%

**Both Teams To Score (BTTS):**
- Sim: 68.9% (ambos devem marcar)
- Não: 31.1%

**Placares Exatos:**
- 1-1: 10.04% (mais provável)
- 2-1: 9.11%
- 2-2: 6.73%

## 🎯 Dicas de Uso

### 1. Quando o Modelo é Mais Confiável

✅ **Bom para:**
- Times com muitos jogos na base de dados
- Ligas com padrões consistentes
- Jogos entre times da mesma liga

❌ **Menos confiável para:**
- Times com poucos jogos
- Mudanças recentes (novo técnico, lesões)
- Jogos internacionais
- Copas (formato diferente)

### 2. Ajustando o Decaimento Temporal (xi)

- **xi = 0**: Todos os jogos têm peso igual
- **xi = 0.001 a 0.005**: Decaimento suave (recomendado)
- **xi > 0.01**: Muito foco em jogos recentes

**Fórmula do peso:**
```
peso = exp(-xi * dias_desde_jogo / 365.25)
```

### 3. Interpretando Odds

Converta probabilidades em odds:
```
Odds = 1 / Probabilidade
```

Exemplo:
- Prob Vitória Casa: 45.5%
- Odds justas: 1 / 0.455 = 2.20

Se as odds da casa de apostas são 2.50, há **value** (aposta tem valor esperado positivo).

### 4. Combinando Predições

**Estratégias:**

1. **Over/Under + BTTS**
   - Over 2.5: 69.1% + BTTS Sim: 68.9%
   - Se ambos altos → Jogo aberto esperado

2. **1X2 + Handicap**
   - Vitória Casa: 66.7% (forte favorito)
   - Considerar Handicap -1 ou -1.5

3. **Placares Exatos**
   - Top 3 somam ~25% de probabilidade
   - Útil para apostas de placar correto

## 📊 Validação do Modelo

### Métricas Comuns

1. **Brier Score**: Mede acurácia das probabilidades
2. **Log Loss**: Penaliza predições muito confiantes e erradas
3. **ROI**: Retorno sobre investimento simulando apostas

### Como Validar

```python
# Separar dados em treino/teste
df_treino = df[df['data'] < '2025-09-01']
df_teste = df[df['data'] >= '2025-09-01']

# Treinar apenas com dados de treino
model.fit(df_treino)

# Testar em dados futuros
# ... calcular métricas
```

## 🔧 Personalizações Avançadas

### 1. Filtrar por Competição

```python
df_ucl = df[df['competicao'] == 'UEFA Champions League']
model_ucl = DixonColesModel(xi=0.003)
model_ucl.fit(df_ucl)
```

### 2. Adicionar Mais Features

Você pode estender o modelo para incluir:
- Forma recente do time
- Lesões/suspensões
- Motivação (posição na tabela)
- Condições climáticas

### 3. Ensemble de Modelos

Combine Dixon-Coles com outros modelos:
- Elo Rating
- Poisson simples
- Machine Learning (XGBoost, etc.)

## 📚 Referências

**Paper Original:**
Dixon, M. J., & Coles, S. G. (1997). *Modelling Association Football Scores and Inefficiencies in the Football Betting Market*. Journal of the Royal Statistical Society: Series C (Applied Statistics), 46(2), 265-280.

**Leituras Recomendadas:**
- *The Numbers Game* - Chris Anderson & David Sally
- *Soccermatics* - David Sumpter
- *Football Analytics with Python & R* - Eric Eager

## ⚠️ Avisos Importantes

1. **Não é infalível**: Futebol tem aleatoriedade inerente
2. **Gestão de banca**: Nunca aposte mais do que pode perder
3. **Responsabilidade**: Use para fins educacionais/analíticos
4. **Atualize o modelo**: Retreine periodicamente com novos dados

## 🆘 Solução de Problemas

### Erro: "Time não encontrado no modelo"

**Causa:** Time não está na base de dados de treino

**Solução:** Verifique o nome exato usando `listar_times()` ou adicione dados do time

### Warning: "Otimização não convergiu"

**Causa:** Poucos dados ou parâmetros iniciais ruins

**Solução:**
- Aumente o número de partidas
- Ajuste `maxiter` no código
- Verifique qualidade dos dados

### Probabilidades estranhas (>100% ou negativas)

**Causa:** Bug na normalização ou dados corrompidos

**Solução:**
- Verifique se os gols são inteiros não-negativos
- Recalcule a matriz de probabilidades

## 💡 Exemplos Práticos

### Encontrar Value Bets

```python
prediction = model.predict_match('Arsenal FC', 'Liverpool FC')

# Odds da casa de apostas (exemplo)
odds_casa = 2.10
odds_empate = 3.50
odds_fora = 3.80

# Probabilidades implícitas das odds
prob_impl_casa = 1 / odds_casa  # 47.6%
prob_impl_fora = 1 / odds_fora  # 26.3%

# Comparar com modelo
prob_modelo_casa = prediction['prob_home_win']  # 66.7%
prob_modelo_fora = prediction['prob_away_win']  # 8.7%

# Value = prob_modelo / prob_impl
value_casa = prob_modelo_casa / prob_impl_casa  # 1.40 (40% value!)
value_fora = prob_modelo_fora / prob_impl_fora  # 0.33 (sem value)

if value_casa > 1.1:  # 10% de margem
    print("BET: Arsenal para vencer!")
```

### Simular Temporada

```python
# Para cada jogo da rodada
jogos = [
    ('Arsenal FC', 'Chelsea FC'),
    ('Liverpool FC', 'Man City'),
    # ...
]

pontos = {time: 0 for time in model.teams}

for casa, fora in jogos:
    pred = model.predict_match(casa, fora)
    
    # Simular resultado baseado nas probabilidades
    resultado = np.random.choice(
        ['H', 'D', 'A'],
        p=[pred['prob_home_win'], pred['prob_draw'], pred['prob_away_win']]
    )
    
    if resultado == 'H':
        pontos[casa] += 3
    elif resultado == 'D':
        pontos[casa] += 1
        pontos[fora] += 1
    else:
        pontos[fora] += 3

# Ver tabela projetada
tabela = sorted(pontos.items(), key=lambda x: x[1], reverse=True)
for pos, (time, pts) in enumerate(tabela, 1):
    print(f"{pos}. {time}: {pts} pontos")
```

---

**Criado para o projeto de Análises Esportivas**
Última atualização: Outubro 2025

