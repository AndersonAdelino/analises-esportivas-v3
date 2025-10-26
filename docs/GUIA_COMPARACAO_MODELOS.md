# 🔍 Guia de Comparação Detalhada de Modelos

## 📋 Visão Geral

A funcionalidade de **Comparação Detalhada de Modelos** permite visualizar e analisar como cada um dos 3 modelos preditivos (Dixon-Coles, Offensive-Defensive e Heurísticas) chegou às suas conclusões, incluindo:

- Comparação de probabilidades entre modelos
- Visualização de placares mais prováveis
- Análise de convergência e consenso
- Métricas de confiança nas predições

## 🚀 Como Acessar

1. Execute o aplicativo: `streamlit run app_betting.py`
2. Vá para a aba **"🎯 Análise de Apostas"**
3. Selecione uma partida e clique em **"ANALISAR"**
4. Role até a seção **"🔍 Comparação Detalhada dos Modelos"**

## 📊 Funcionalidades

### 1. Tab "Probabilidades"

#### Gráficos de Barras Comparativas

Compare as probabilidades previstas por cada modelo para:
- **Resultado 1X2** (Vitória Casa, Empate, Vitória Fora)
- **Over/Under 2.5 Gols**
- **BTTS** (Both Teams To Score - Ambos Marcam)

**Como interpretar:**
- Barras de **mesma altura** = modelos concordam
- Barras **muito diferentes** = modelos divergem (maior incerteza)
- Barra **vermelha** = probabilidade do Ensemble (combinação)

#### Gráfico Radar (Spider)

Visualização multidimensional comparando os 4 "modelos" (3 individuais + Ensemble) em 6 dimensões:
1. Vitória Casa
2. Empate
3. Vitória Fora
4. Over 2.5
5. Under 2.5
6. BTTS

**Como interpretar:**
- Formas **sobrepostas** = alto consenso
- Formas **dispersas** = modelos divergem
- Ensemble (vermelho) combina todos

### 2. Tab "Placares"

#### Heatmaps (Mapas de Calor)

Visualize a distribuição de probabilidades para diferentes placares em cada modelo:

- **Dixon-Coles**: Modelo estatístico com correção rho
- **Offensive-Defensive**: Modelo baseado em forças
- **Ensemble**: Combinação ponderada

**Como interpretar:**
- **Verde intenso** = alta probabilidade
- **Vermelho** = baixa probabilidade
- **Eixo Y** (vertical) = Gols da Casa (0-5)
- **Eixo X** (horizontal) = Gols Fora (0-5)
- Passe o mouse sobre as células para ver probabilidades exatas

#### Top 10 Placares Mais Prováveis

Tabela comparativa mostrando:
- Os 10 placares mais prováveis segundo o Ensemble
- Probabilidades de cada modelo para esses placares
- Identificação de consenso

**Uso para apostas:**
- Placares com **alta probabilidade no Ensemble** são boas opções
- Placares com **consenso entre modelos** têm maior confiança
- Use para mercados de **placar exato** ou **margens de vitória**

### 3. Tab "Convergência"

#### Métricas de Divergência e Consenso

**Divergência KL (Kullback-Leibler):**
- Mede diferença matemática entre distribuições de probabilidade
- **< 0.1** = Baixa (modelos muito concordantes) ✅
- **0.1-0.3** = Moderada (alguma divergência) ⚠️
- **> 0.3** = Alta (modelos discordam) ❌

**Nível de Consenso:**
- Percentual de concordância entre modelos
- **≥ 85%** = Muito Alto (forte concordância) 🟢
- **70-85%** = Alto (boa concordância) 🟡
- **50-70%** = Moderado (concordância parcial) 🟠
- **< 50%** = Baixo (modelos divergem) 🔴

**Confiança na Predição:**
- Baseado no nível de consenso
- **Alta** = Pode apostar com mais confiança
- **Boa** = Predição razoável, cautela moderada
- **Baixa** = Evitar aposta ou usar stakes mínimos

#### Desvio Padrão por Mercado

Mostra a variabilidade das predições de cada modelo para:
- Vitória Casa
- Empate
- Vitória Fora

**Interpretação:**
- Desvio baixo (< 0.05) = modelos concordam
- Desvio alto (> 0.15) = alta incerteza

#### Recomendações Baseadas em Consenso

O sistema fornece recomendações automáticas:

**Alto Consenso (≥ 80%):**
```
✅ Os modelos concordam fortemente.
   Você pode apostar com mais confiança.
```

**Consenso Moderado (60-80%):**
```
ℹ️ Os modelos concordam parcialmente.
   Considere reduzir o stake em 25-50%.
```

**Baixo Consenso (< 60%):**
```
⚠️ Os modelos divergem significativamente.
   Recomenda-se não apostar ou usar stakes mínimos.
```

## 💡 Estratégias de Uso

### Estratégia 1: Consenso Forte

**Quando usar:**
- Consenso ≥ 85%
- Divergência KL < 0.1
- Value bet identificado

**Ação:**
- Seguir recomendação de stake do Kelly Criterion
- Alta confiança na predição

### Estratégia 2: Divergência entre Modelos

**Quando usar:**
- Consenso < 60%
- Divergência KL > 0.3
- Modelos apontam resultados diferentes

**Ação:**
- **Não apostar** ou
- Reduzir stake para 25% do recomendado
- Investigar motivo da divergência

### Estratégia 3: Placares Específicos

**Quando usar:**
- Apostas em placar exato
- Odds altas disponíveis

**Ação:**
1. Ver **Top 10 Placares** na tab "Placares"
2. Identificar placares com **consenso** entre modelos
3. Comparar probabilidade do Ensemble com odds da casa
4. Apostar se EV positivo e consenso alto

### Estratégia 4: Arbitragem de Modelos

**Quando usar:**
- Um modelo aponta forte value bet
- Outro modelo discorda
- Ensemble no meio termo

**Ação:**
1. Analisar **por que** os modelos divergem
2. Ver **heatmaps** para entender distribuição
3. Considerar características da partida (casa/fora, forma recente)
4. Decidir baseado em qual modelo é mais confiável para o caso

## 📖 Casos de Uso Práticos

### Caso 1: Alta Confiança

**Cenário:**
- Arsenal vs Brighton
- Consenso: 88%
- Divergência KL: 0.08
- Ensemble: Casa 65%
- Odds Casa: 1.80 (implied 55.5%)

**Análise:**
- ✅ Alto consenso
- ✅ Todos os modelos apontam vitória da casa
- ✅ EV positivo (~17%)

**Decisão:** Apostar com stake recomendado pelo Kelly

### Caso 2: Modelos Divergem

**Cenário:**
- Man United vs Liverpool
- Consenso: 45%
- Divergência KL: 0.42
- Dixon-Coles: Casa 35%, Fora 45%
- Heurísticas: Casa 70%, Fora 15%
- Ensemble: Casa 48%, Fora 32%

**Análise:**
- ❌ Baixo consenso
- ❌ Modelos estatísticos vs heurísticas divergem muito
- ⚠️ Alta incerteza

**Decisão:** Evitar aposta ou stake mínimo

### Caso 3: Placar Exato

**Cenário:**
- Chelsea vs Newcastle
- Top 3 placares no Ensemble: 2-0 (12%), 1-0 (11%), 2-1 (10%)
- Odds 2-0: 9.00 (implied 11.1%)
- Consenso nos modelos para 2-0: DC=13%, OD=11%, H=N/A

**Análise:**
- ✅ Ensemble: 12% vs Casa: 11.1%
- ✅ Modelos estatísticos concordam
- ✅ Leve value bet

**Decisão:** Apostar pequena quantia em placar exato 2-0

## 🎯 Melhores Práticas

### 1. Sempre Verifique o Consenso

Antes de apostar, sempre olhe:
1. Nível de Consenso na tab "Convergência"
2. Se < 70%, considere reduzir stake ou evitar

### 2. Use Heatmaps para Entender Distribuição

- Não confie apenas em probabilidades médias
- Veja a **distribuição completa** nos heatmaps
- Identifique padrões (ex: jogo defensivo = placares baixos verdes)

### 3. Compare Placares com Odds

- Vá na tab "Placares"
- Veja Top 10 Placares
- Compare com odds de placar exato disponíveis
- Apostas em placares específicos podem ter alto EV

### 4. Entenda Por Que Modelos Divergem

Possíveis motivos:
- **Forma recente** (Heurísticas captura, estatísticos não)
- **Qualidade dos adversários** (Estatísticos ponderam melhor)
- **Vantagem de jogar em casa** (Modelos ponderam diferente)
- **Dados limitados** (Heurísticas precisa de histórico direto)

### 5. Ajuste Stakes Baseado em Consenso

| Consenso | Multiplicador de Stake |
|----------|----------------------|
| ≥ 85% | 1.0x (stake cheio) |
| 70-85% | 0.75x (reduzir 25%) |
| 60-70% | 0.5x (reduzir 50%) |
| < 60% | 0.25x ou evitar |

## 🔬 Métricas Técnicas

### Divergência KL (Kullback-Leibler)

**Fórmula:**
```
KL(P||Q) = Σ P(i) * log(P(i) / Q(i))
```

Onde:
- P = Distribuição do modelo 1
- Q = Distribuição do modelo 2

**Propriedades:**
- Sempre ≥ 0
- = 0 apenas se P = Q
- Assimétrica: KL(P||Q) ≠ KL(Q||P)

### Consenso

**Fórmula:**
```
Consenso = (1 - σ/μ) × 100%
```

Onde:
- σ = Desvio padrão das probabilidades
- μ = Média das probabilidades

**Interpretação:**
- 100% = todos modelos idênticos
- 0% = máxima dispersão

## ❓ FAQ

### P: Por que os heatmaps não mostram Heurísticas?

**R:** O modelo de Heurísticas não gera matrizes de probabilidade de placares específicos. Ele fornece apenas predições categóricas (Vitória Casa, Empate, Vitória Fora) baseadas em padrões e regras.

### P: Qual modelo devo confiar mais?

**R:** Depende:
- **Dixon-Coles**: Melhor para predições gerais e placares
- **Offensive-Defensive**: Bom para análise de forças
- **Heurísticas**: Captura forma recente e momentum
- **Ensemble**: Combina vantagens de todos (RECOMENDADO)

### P: O que fazer quando há baixo consenso?

**R:** Opções:
1. **Evitar aposta** (mais seguro)
2. **Reduzir stake** para 25% ou menos
3. **Investigar motivo** da divergência
4. **Aguardar outra partida** com maior consenso

### P: Como usar placares para apostas?

**R:**
1. Vá na tab "Placares"
2. Identifique placares com alta probabilidade
3. Verifique consenso entre modelos
4. Compare com odds de **Placar Exato** ou **Margens de Vitória**
5. Aposte se houver value bet

### P: Posso confiar 100% no consenso?

**R:** Não. Consenso alto indica que os modelos concordam, mas:
- Todos os modelos podem estar errados simultaneamente
- Eventos imprevisíveis acontecem (lesões, expulsões, etc.)
- Sempre use gestão de banca responsável
- Consenso é um **indicador**, não garantia

## 🎓 Conclusão

A Comparação Detalhada de Modelos é uma ferramenta poderosa para:
- ✅ Aumentar confiança em predições com alto consenso
- ✅ Identificar apostas arriscadas (baixo consenso)
- ✅ Encontrar value bets em placares específicos
- ✅ Entender como cada modelo analisa a partida
- ✅ Tomar decisões mais informadas e racionais

**Lembre-se:** Sempre combine análise dos modelos com gestão de banca responsável e conhecimento do esporte!

---

**Desenvolvido para o projeto Value Betting Analyzer**  
*Última atualização: Outubro 2025*

