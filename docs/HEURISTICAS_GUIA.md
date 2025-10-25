# Guia Completo: Sistema de Heurísticas

## 📚 Índice
1. [Introdução](#introdução)
2. [O que são Heurísticas?](#o-que-são-heurísticas)
3. [Heurísticas Implementadas](#heurísticas-implementadas)
4. [Como Usar](#como-usar)
5. [Interpretação dos Resultados](#interpretação-dos-resultados)
6. [Comparação com Modelos Estatísticos](#comparação-com-modelos-estatísticos)
7. [Vantagens e Limitações](#vantagens-e-limitações)
8. [Exemplos Práticos](#exemplos-práticos)

---

## Introdução

O **Sistema de Heurísticas** é uma abordagem complementar aos modelos estatísticos (Dixon-Coles e Offensive-Defensive) que utiliza **regras práticas** e **padrões observáveis** para fazer predições sobre partidas de futebol.

Enquanto os modelos estatísticos usam matemática avançada e otimização, as heurísticas aplicam **senso comum esportivo** baseado em dados históricos.

---

## O que são Heurísticas?

**Heurísticas** são atalhos mentais ou regras práticas que simplificam decisões complexas. No contexto de futebol:

- ✅ **Simples de entender**: "Time em sequência de 5 vitórias tende a vencer"
- ✅ **Interpretáveis**: Cada fator contribui de forma transparente
- ✅ **Baseadas em experiência**: Capturam padrões que analistas experientes conhecem
- ✅ **Rápidas**: Não requerem otimização matemática complexa

### Diferença dos Modelos Estatísticos

| Característica | Heurísticas | Modelos Estatísticos |
|----------------|-------------|----------------------|
| **Complexidade** | Baixa (regras simples) | Alta (otimização matemática) |
| **Interpretabilidade** | Alta (fatores claros) | Média (parâmetros abstratos) |
| **Velocidade** | Muito rápida | Moderada (requer fitting) |
| **Precisão** | Boa para tendências | Melhor para probabilidades exatas |
| **Uso de dados recentes** | Foco em jogos mais recentes | Considera todo histórico com decay |

---

## Heurísticas Implementadas

### 1. **Forma Recente** (Peso: 0-3 pontos)

Analisa os últimos N jogos (padrão: 5) do time.

**Métricas:**
- Vitórias, empates, derrotas
- Aproveitamento de pontos (%)
- Média de gols marcados/sofridos
- Sequência atual (ex: V-V-E-D-V)
- Status de invencibilidade

**Lógica de pontuação:**
- **+3 pontos**: Aproveitamento >15% superior ao adversário
- **+1 ponto**: Aproveitamento ligeiramente superior
- **0 pontos**: Aproveitamentos similares

**Exemplo:**
```
Arsenal: 87% (4V-1E) vs Liverpool: 40% (2V-3D)
→ Arsenal recebe +3 pontos
```

---

### 2. **Performance Casa/Fora** (Peso: 0-2 pontos)

Compara desempenho específico do mandante em casa vs visitante fora.

**Métricas:**
- Aproveitamento em casa (mandante)
- Aproveitamento fora (visitante)
- Média de gols marcados/sofridos no local

**Lógica de pontuação:**
- **+2 pontos**: Mandante com >20% aproveitamento superior em casa
- **+1 ponto**: Visitante com melhor aproveitamento fora

**Exemplo:**
```
Man City em casa: 83% vs Chelsea fora: 50%
→ Man City recebe +2 pontos
```

---

### 3. **Confronto Direto** (Peso: 0-2 pontos)

Analisa histórico de confrontos entre os dois times (mínimo 3 jogos).

**Métricas:**
- Vitórias de cada time
- Empates
- Média de gols marcados
- Time favorito historicamente

**Lógica de pontuação:**
- **+2 pontos**: Time historicamente favorito
- **0 pontos**: Se menos de 3 confrontos ou equilibrado

**Exemplo:**
```
Arsenal vs Liverpool (últimos 5 jogos):
  0V-0E-5D (Liverpool domina)
→ Liverpool recebe +2 pontos
```

---

### 4. **Sequências** (Peso: 0-2 pontos)

Identifica sequências de vitórias ou derrotas.

**Métricas:**
- Sequência atual (tipo e tamanho)
- Maior sequência de vitórias consecutivas
- Jogos sem vencer
- Status invicto

**Lógica de pontuação:**
- **+2 pontos**: Time com 3+ vitórias consecutivas
- **+1 ponto**: Adversário com 3+ derrotas consecutivas
- **0 pontos**: Sem sequências significativas

**Exemplo:**
```
Man City: 5 vitórias consecutivas
→ Man City recebe +2 pontos

Chelsea: 3 derrotas consecutivas
→ Man City recebe +1 ponto adicional
```

---

### 5. **Tendência de Gols** (Para Over/Under e BTTS)

Analisa padrões de gols nos últimos N jogos.

**Métricas:**
- Média total de gols por jogo
- Frequência de Over 2.5 gols (%)
- Frequência de Over 1.5 gols (%)
- Frequência de Both Teams to Score (%)

**Lógica de predição:**

**Over/Under 2.5:**
- Gols esperados > 2.7 → **Over 2.5** (confiança 65%)
- Gols esperados < 2.2 → **Under 2.5** (confiança 65%)
- 2.2 ≤ Gols ≤ 2.7 → **Incerto** (confiança 50%)

**BTTS:**
- Frequência BTTS > 60% → **Sim** (confiança 65%)
- Frequência BTTS < 40% → **Não** (confiança 60%)
- 40% ≤ BTTS ≤ 60% → **Incerto** (confiança 50%)

---

## Como Usar

### 1. Script Principal (`heuristicas.py`)

Análise programática com exemplos:

```bash
python heuristicas.py
```

**Saída:**
- Análises de 3 partidas exemplo
- Métricas detalhadas
- Fatores considerados

---

### 2. Predição Interativa (`prever_com_heuristicas.py`)

Interface interativa para análise de qualquer partida:

```bash
python prever_com_heuristicas.py
```

**Fluxo:**
1. Lista todos os times disponíveis
2. Escolha time da casa (número ou nome)
3. Escolha time visitante
4. Exibe análise completa
5. Opção de fazer outra análise

**Exemplo de uso:**
```
Time da CASA: 1                  # Arsenal
Time VISITANTE: Liverpool        # Busca por nome

# Análise completa é exibida
```

---

### 3. Comparação Completa (`comparar_modelos_completo.py`)

Compara Dixon-Coles, Offensive-Defensive e Heurísticas:

```bash
python comparar_modelos_completo.py "Arsenal FC" "Liverpool FC"
```

**Saída:**
- Tabela comparativa 1X2
- Over/Under 2.5 de cada modelo
- BTTS de cada modelo
- Placar mais provável
- **Consenso entre modelos**

---

### 4. Uso Programático

```python
from heuristicas import HeuristicasModel, print_prediction

# Carrega modelo
model = HeuristicasModel()
model.load_data()

# Faz predição
pred = model.predict_match('Arsenal FC', 'Liverpool FC')

# Exibe resultado formatado
print_prediction(pred)

# Ou acessa dados diretamente
print(f"Resultado: {pred['resultado_previsto']}")
print(f"Confiança: {pred['confianca']}%")
print(f"Over/Under: {pred['over_under']}")
print(f"BTTS: {pred['btts']}")

# Análises específicas
forma = model.forma_recente('Arsenal FC', n_jogos=5)
print(f"Aproveitamento: {forma['aproveitamento']:.1f}%")

confronto = model.confronto_direto('Arsenal FC', 'Liverpool FC')
print(f"Favorito: {confronto['favorito']}")

sequencia = model.sequencias('Arsenal FC')
print(f"Sequência: {sequencia['sequencia_desc']}")
```

---

## Interpretação dos Resultados

### Sistema de Pontuação

Cada time acumula pontos baseado nos fatores acima:

```
Pontuação Total = Forma (0-3) + Casa/Fora (0-2) + Confronto (0-2) + Sequências (0-2)
Máximo possível: 9 pontos
```

### Resultado Previsto

| Diferença de Pontos | Resultado | Confiança |
|---------------------|-----------|-----------|
| **Casa > Fora + 2** | Vitória Casa | 70-90% (depende da margem) |
| **Fora > Casa + 2** | Vitória Fora | 70-90% |
| **Casa > Fora** (margem 1-2) | Vitória Casa | 55% |
| **Fora > Casa** (margem 1-2) | Vitória Fora | 55% |
| **Casa = Fora** | Empate | 45% |
| **Nenhum ponto** | Empate | 30% |

### Confiança

A **confiança** indica o quão forte é a predição:

- **80-90%**: Muito alta (diferença grande de pontos, múltiplos fatores favoráveis)
- **65-75%**: Alta (diferença moderada, alguns fatores favoráveis)
- **50-60%**: Moderada (diferença pequena, poucos fatores)
- **30-45%**: Baixa (times equilibrados, sem fatores claros)

---

## Comparação com Modelos Estatísticos

### Quando Usar Heurísticas?

✅ **Vantagens das Heurísticas:**
- Rápidas de calcular (sem fitting)
- Fáceis de entender e explicar
- Capturam momentum e forma recente
- Úteis para análise exploratória
- Boas para identificar favoritos claros

❌ **Limitações das Heurísticas:**
- Não fornecem probabilidades exatas
- Menos precisas que modelos para margens estreitas
- Dependem de definições arbitrárias (thresholds)
- Não consideram qualidade do adversário de forma sofisticada

### Quando Usar Modelos Estatísticos?

✅ **Vantagens dos Modelos:**
- Probabilidades calibradas matematicamente
- Consideram força dos adversários
- Melhor para apostas (value betting)
- Distribuição completa de placares

❌ **Limitações dos Modelos:**
- Requerem fitting (mais lentos)
- Menos interpretáveis
- Podem não capturar mudanças súbitas de forma

### Combinação Ideal

🎯 **Recomendação:**
Use **heurísticas para triagem** e **modelos para decisão final**:

1. **Heurísticas**: Identifique jogos com favoritos claros ou padrões fortes
2. **Modelos**: Calcule probabilidades exatas para apostas
3. **Consenso**: Dê mais peso quando todos concordam

**Exemplo de workflow:**
```python
# 1. Análise rápida com heurísticas
heur_pred = heur_model.predict_match('Arsenal FC', 'Liverpool FC')

if heur_pred['confianca'] > 70:
    print("Favorito claro identificado!")
    
    # 2. Confirmar com modelo estatístico
    dc_pred = dc_model.predict_match('Arsenal FC', 'Liverpool FC')
    
    # 3. Verificar consenso
    if heur_pred['resultado_previsto'] == 'Vitória Arsenal' and dc_pred['prob_casa'] > 0.5:
        print("CONSENSO: Aposte em Arsenal!")
```

---

## Vantagens e Limitações

### ✅ Vantagens

1. **Transparência**: Cada fator é claro
2. **Rapidez**: Sem necessidade de fitting
3. **Intuição**: Alinhadas com análise de especialistas
4. **Momentum**: Capturam forma atual
5. **Simplicidade**: Fácil implementar e modificar

### ❌ Limitações

1. **Sem probabilidades exatas**: Apenas resultado categórico
2. **Thresholds arbitrários**: 15%, 20%, 3 jogos, etc.
3. **Peso igual**: Todos os fatores têm peso fixo
4. **Sem contexto de qualidade**: Vitória contra time forte = vitória contra fraco
5. **Overfitting visual**: Fácil ajustar regras ao histórico

### 🔧 Melhorias Possíveis

Para tornar o sistema ainda melhor:

1. **Machine Learning**: Aprender pesos automaticamente
2. **Contexto de qualidade**: Ponderar por força do adversário
3. **Sazonalidade**: Considerar fase da temporada
4. **Lesões/Suspensões**: Integrar dados de elenco
5. **Testes A/B**: Validar thresholds em dados históricos

---

## Exemplos Práticos

### Exemplo 1: Favorito Claro

```
Arsenal (Casa) vs Burnley (Fora)

Forma Recente:
  Arsenal: 80% aproveitamento (4V-1E)
  Burnley: 20% aproveitamento (1V-4D)
  → +3 pontos Arsenal

Performance Casa/Fora:
  Arsenal em casa: 85%
  Burnley fora: 25%
  → +2 pontos Arsenal

Sequências:
  Arsenal: 4 vitórias consecutivas
  → +2 pontos Arsenal

TOTAL: Arsenal 7 x 0 Burnley
PREDIÇÃO: Vitória Arsenal (confiança 85%)
```

---

### Exemplo 2: Jogo Equilibrado

```
Manchester United (Casa) vs Tottenham (Fora)

Forma Recente:
  Man Utd: 60% aproveitamento
  Tottenham: 53% aproveitamento
  → +1 ponto Man Utd

Performance Casa/Fora:
  Man Utd em casa: 75%
  Tottenham fora: 83%
  → +1 ponto Tottenham

Confronto Direto:
  Últimos 5: 2V-1E-2D (equilibrado)
  → 0 pontos

Sequências:
  Nenhuma sequência significativa
  → 0 pontos

TOTAL: Man Utd 1 x 1 Tottenham
PREDIÇÃO: Empate (confiança 45%)
```

---

### Exemplo 3: Forma Recente vs Histórico

```
Liverpool (Casa) vs Chelsea (Fora)

Forma Recente:
  Liverpool: 40% (2V-3D) - Má fase
  Chelsea: 73% (4V-1D) - Boa fase
  → +3 pontos Chelsea

Performance Casa/Fora:
  Liverpool em casa: 67%
  Chelsea fora: 67%
  → 0 pontos

Confronto Direto:
  Últimos 5: 4V-0E-1D (Liverpool domina)
  → +2 pontos Liverpool

TOTAL: Liverpool 2 x 3 Chelsea
PREDIÇÃO: Vitória Chelsea (confiança 60%)

# Nota: Forma recente superou histórico
```

---

## Conclusão

O **Sistema de Heurísticas** é uma ferramenta poderosa para:

1. ✅ Análise rápida de múltiplas partidas
2. ✅ Identificação de padrões e tendências
3. ✅ Complemento aos modelos estatísticos
4. ✅ Comunicação clara com não-especialistas

**Use com:**
- Dixon-Coles para probabilidades precisas
- Offensive-Defensive para análise ofensiva/defensiva
- Consenso entre modelos para decisões finais

---

## Referências e Recursos

**Scripts relacionados:**
- `heuristicas.py` - Implementação principal
- `prever_com_heuristicas.py` - Interface interativa
- `comparar_modelos_completo.py` - Comparação entre modelos

**Documentação complementar:**
- `DIXON_COLES_GUIA.md` - Modelo Dixon-Coles
- `OFFENSIVE_DEFENSIVE_GUIA.md` - Modelo Offensive-Defensive
- `EXEMPLOS_USO.md` - Exemplos práticos gerais

**Artigos sobre heurísticas em esportes:**
- Kahneman & Tversky: "Judgment under Uncertainty: Heuristics and Biases"
- Silver, N.: "The Signal and the Noise"

---

**Desenvolvido para o projeto Análises Esportivas v3**
*Documentação atualizada: Outubro 2024*

