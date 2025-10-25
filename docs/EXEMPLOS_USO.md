# 📚 Exemplos de Uso - Análises Esportivas

Guia prático com exemplos reais de como usar o sistema.

## 🚀 Início Rápido

### 1. Coletar Dados (Primeira vez)

```bash
# Passo 1: Dados gerais da Premier League
python get_historical_data.py

# Passo 2: Dados detalhados por time
python get_team_matches.py
```

**Resultado:**
- 81 partidas da Premier League (temporada atual)
- 180 partidas individuais dos times (todas competições)
- Dados salvos em `data/`

### 2. Análises Básicas

```bash
# Análise geral
python analise_basica.py

# Análise por time
python analise_por_time.py
```

### 3. Predições com Dixon-Coles

```bash
# Ver exemplos prontos
python dixon_coles.py

# Interface interativa (recomendado!)
python predicao_interativa.py
```

## 🔮 Exemplos de Predições

### Exemplo 1: Arsenal vs Liverpool

```
Vitória Arsenal: 66.7%
Empate: 24.6%
Vitória Liverpool: 8.7%

Over 2.5: 39.9%
Under 2.5: 60.1%

Ambos Marcam: 28.6%

Placares mais prováveis:
1. 0-0: 22.39%
2. 1-0: 19.71%
3. 1-1: 13.29%
```

**Interpretação:**
- Arsenal é favorito forte (66.7%)
- Jogo deve ter poucos gols (Under 2.5 com 60.1%)
- Provável que apenas um time marque (71.4%)

### Exemplo 2: Liverpool vs Chelsea

```
Vitória Liverpool: 50.4%
Empate: 23.7%
Vitória Chelsea: 25.9%

Over 2.5: 69.1%
Under 2.5: 30.9%

Ambos Marcam: 68.9%

Placares mais prováveis:
1. 1-1: 10.04%
2. 2-1: 9.11%
3. 2-2: 6.73%
```

**Interpretação:**
- Jogo equilibrado, Liverpool leve favorito
- Muito provável ter +3 gols (69.1%)
- Ambos times devem marcar (68.9%)

## 💡 Casos de Uso Práticos

### Caso 1: Análise Pré-Jogo Completa

```python
from dixon_coles import DixonColesModel, load_match_data, print_prediction

# Treina modelo
df = load_match_data()
model = DixonColesModel(xi=0.003)
model.fit(df)

# Jogo que você quer analisar
pred = model.predict_match('Manchester City FC', 'Chelsea FC')
print_prediction(pred)

# Ver forças dos times
strengths = model.get_team_strengths()
print(strengths[strengths['Time'].isin(['Manchester City FC', 'Chelsea FC'])])
```

### Caso 2: Encontrar Value Bets

```python
# Odds da casa de apostas
odds_casa = 2.10  # Arsenal
odds_empate = 3.50
odds_fora = 3.80  # Liverpool

# Predição do modelo
pred = model.predict_match('Arsenal FC', 'Liverpool FC')

# Probabilidades implícitas nas odds
prob_impl_casa = 1 / odds_casa  # 47.6%
prob_impl_fora = 1 / odds_fora  # 26.3%

# Comparar com modelo
print(f"Modelo - Vitória Casa: {pred['prob_home_win']*100:.1f}%")
print(f"Bookmaker - Vitória Casa: {prob_impl_casa*100:.1f}%")

# Value bet se modelo > bookmaker + margem
if pred['prob_home_win'] > prob_impl_casa * 1.1:
    print("✅ VALUE BET encontrado na vitória do Arsenal!")
```

### Caso 3: Gerar Relatório de Rodada

```python
import pandas as pd

# Jogos da próxima rodada
jogos = [
    ('Arsenal FC', 'Chelsea FC'),
    ('Liverpool FC', 'Manchester City FC'),
    ('Manchester United FC', 'Tottenham Hotspur FC'),
    ('Newcastle United FC', 'Aston Villa FC'),
    ('Brighton & Hove Albion FC', 'West Ham United FC'),
]

resultados = []

for casa, fora in jogos:
    pred = model.predict_match(casa, fora)
    
    resultados.append({
        'Jogo': f"{casa} vs {fora}",
        'Resultado_Provavel': 'Casa' if pred['prob_home_win'] > 0.5 
                             else ('Fora' if pred['prob_away_win'] > 0.35 else 'Empate'),
        'Prob_%': max(pred['prob_home_win'], pred['prob_draw'], pred['prob_away_win']) * 100,
        'Over_2.5_%': pred['prob_over_2_5'] * 100,
        'BTTS_%': pred['prob_btts_yes'] * 100,
        'Placar': f"{pred['top_scores'][0][0][0]}-{pred['top_scores'][0][0][1]}"
    })

df_relatorio = pd.DataFrame(resultados)
print(df_relatorio.to_string(index=False))

# Salvar
df_relatorio.to_csv('relatorio_rodada.csv', index=False)
```

### Caso 4: Comparar Força de Times

```python
# Ver os 5 melhores ataques
strengths = model.get_team_strengths()
top_ataques = strengths.nlargest(5, 'Ataque')

print("🎯 Top 5 Ataques:")
for idx, row in top_ataques.iterrows():
    print(f"{row['Time']}: {row['Ataque']:.3f}")

# Ver as 5 melhores defesas
top_defesas = strengths.nsmallest(5, 'Defesa')

print("\n🛡️ Top 5 Defesas:")
for idx, row in top_defesas.iterrows():
    print(f"{row['Time']}: {row['Defesa']:.3f}")
```

### Caso 5: Simular Múltiplos Resultados

```python
import numpy as np

# Simular 10.000 vezes o resultado de Arsenal vs Liverpool
n_simulacoes = 10000
resultados = {'Casa': 0, 'Empate': 0, 'Fora': 0}

pred = model.predict_match('Arsenal FC', 'Liverpool FC')

for _ in range(n_simulacoes):
    resultado = np.random.choice(
        ['Casa', 'Empate', 'Fora'],
        p=[pred['prob_home_win'], pred['prob_draw'], pred['prob_away_win']]
    )
    resultados[resultado] += 1

print("Simulação de 10.000 jogos:")
for key, valor in resultados.items():
    print(f"{key}: {valor} vezes ({valor/n_simulacoes*100:.1f}%)")
```

## 📊 Fluxo de Trabalho Recomendado

### Para Análise Semanal

```bash
# Segunda-feira: Atualizar dados
python get_team_matches.py

# Terça/Quarta: Análises
python analise_por_time.py

# Quinta/Sexta: Predições para rodada
python gerar_predicoes_lote.py  # Opção 2 (partidas específicas)

# Sábado: Refinamento
python predicao_interativa.py  # Análise jogo a jogo
```

### Para Análise de um Jogo Específico

1. **Verificar dados recentes:**
   ```bash
   python analise_por_time.py
   ```

2. **Ver predição:**
   ```bash
   python predicao_interativa.py
   ```

3. **Conferir forças:**
   - Ver ranking de ataque/defesa
   - Comparar forma recente (últimos 5 jogos)

4. **Decidir:**
   - Comparar com odds do mercado
   - Verificar value bets
   - Considerar contexto (lesões, motivação, etc.)

## 🎓 Dicas Profissionais

### 1. Gestão de Banca

Nunca aposte baseado apenas no modelo:
- Use 1-2% da banca por aposta
- Combine modelo com análise qualitativa
- Registre todas as apostas para análise

### 2. Quando Confiar no Modelo

✅ **Alta confiança:**
- Times com muitos jogos na base
- Diferença clara de probabilidades (>60%)
- Value bet significativo (>15%)

⚠️ **Baixa confiança:**
- Times com poucos dados
- Probabilidades muito próximas (33-33-33)
- Mudanças recentes no time

### 3. Combinando Mercados

**Exemplo de estratégia:**
```
Se Over 2.5 > 65% E BTTS > 65%:
  → Apostar em Over 2.5 (mais seguro)
  → Considerar parlay: Over 1.5 + BTTS

Se Vitória Casa > 70% E Under 2.5 > 60%:
  → Apostar em Vitória Casa
  → Considerar handicap -1
```

### 4. Monitoramento

Mantenha um log de predições:
```python
# Salvar predições com timestamp
import json
from datetime import datetime

pred = model.predict_match('Arsenal FC', 'Liverpool FC')
pred['timestamp'] = datetime.now().isoformat()
pred['odds_casa'] = 2.10  # Adicione odds do mercado

with open('log_predicoes.json', 'a') as f:
    json.dump(pred, f)
    f.write('\n')
```

## 🔍 Troubleshooting Comum

### "Nenhum arquivo encontrado"
```bash
# Solução: Coletar dados primeiro
python get_team_matches.py
```

### "Time não encontrado no modelo"
```python
# Listar times disponíveis
model.teams  # ou
python predicao_interativa.py  # Opção 3
```

### "Probabilidades estranhas"
```python
# Verificar dados de entrada
df = load_match_data()
print(df.info())
print(df[['time_casa', 'time_visitante', 'gols_casa', 'gols_visitante']].head())
```

### "Otimização não convergiu"
```python
# Aumentar iterações
model = DixonColesModel(xi=0.003)
# Edite dixon_coles.py, linha com 'maxiter': 100 → 200
```

## 📖 Recursos Adicionais

- [Guia Completo Dixon-Coles](DIXON_COLES_GUIA.md)
- [README Principal](README.md)
- [Football-Data API Docs](https://www.football-data.org/documentation/quickstart)

---

**Desenvolvido para Análises Esportivas v3**

