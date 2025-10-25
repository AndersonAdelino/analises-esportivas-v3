# 📊 Guia de Análise Detalhada de Times

## 🎯 Visão Geral

O sistema agora inclui uma funcionalidade completa de análise de times, permitindo que você visualize histórico, estatísticas e tendências de qualquer time da Premier League.

## 🚀 Como Usar

### Acesso à Análise de Times

1. Execute o aplicativo Streamlit: `streamlit run app_betting.py`
2. Na interface, clique na aba **"📊 Análise de Times"**
3. Selecione o time que deseja analisar
4. Ajuste o número de jogos para análise (10-50 partidas)

## 📈 Estatísticas Disponíveis

### 1. Estatísticas Gerais

- **Jogos Totais**: Número total de partidas analisadas
- **Vitórias**: Total de vitórias e taxa de vitória (%)
- **Empates**: Total de empates
- **Derrotas**: Total de derrotas
- **Forma**: Últimos 5 resultados (V=Vitória, E=Empate, D=Derrota)

### 2. Estatísticas de Gols

- **Gols Marcados**: Total de gols marcados
- **Gols Sofridos**: Total de gols sofridos
- **Saldo de Gols**: Diferença entre gols marcados e sofridos
- **Média de Gols/Jogo**: Média de gols marcados por partida
- **Pontos**: Total de pontos e média por jogo

### 3. Estatísticas para Apostas

- **Over 2.5 Gols**: Percentual de jogos com mais de 2.5 gols
- **BTTS (Both Teams to Score)**: Percentual de jogos onde ambos marcaram
- **Média de Gols Marcados**: Média ofensiva do time
- **Média de Gols Sofridos**: Média defensiva do time

### 4. Análise Casa vs Fora

Comparação detalhada do desempenho:
- Em casa (mandante)
- Fora (visitante)

Inclui: vitórias, gols marcados e sofridos por local.

## 📊 Gráficos Disponíveis

### 🎯 Gráfico de Resultados

**O que mostra**: Pontos conquistados em cada partida ao longo do tempo

**Como interpretar**:
- **Pontos verdes**: Vitórias (3 pontos)
- **Pontos cinzas**: Empates (1 ponto)
- **Pontos vermelhos**: Derrotas (0 pontos)

**Útil para**: Identificar sequências de resultados e momentos de forma

### ⚽ Gráfico de Tendência de Gols

**O que mostra**: Média móvel de 5 jogos para gols marcados e sofridos

**Como interpretar**:
- **Linha verde**: Tendência ofensiva (gols marcados)
- **Linha vermelha**: Tendência defensiva (gols sofridos)
- Linhas subindo = melhora
- Linhas descendo = piora

**Útil para**: 
- Identificar times em boa fase ofensiva
- Identificar defesas frágeis
- Apostar em Over/Under

### 📈 Gráfico de Forma (Pontos Acumulados)

**O que mostra**: Pontos acumulados vs linha de pontos esperados (média da liga)

**Como interpretar**:
- **Linha azul**: Pontos reais acumulados
- **Linha cinza tracejada**: Pontos esperados (1.5 por jogo = meio de tabela)
- Acima da linha = desempenho acima da média
- Abaixo da linha = desempenho abaixo da média

**Útil para**: 
- Avaliar se o time está em tendência de alta ou baixa
- Comparar com expectativas da liga

### 🏠 Gráfico Casa vs Fora

**O que mostra**: Comparação direta entre desempenho em casa e fora

**Como interpretar**:
- **Barras azuis**: Desempenho em casa
- **Barras vermelhas**: Desempenho fora
- Diferenças grandes indicam dependência do mando de campo

**Útil para**: 
- Identificar times muito dependentes do mando
- Avaliar times que performam melhor fora
- Ajustar apostas baseado no local do jogo

### 📋 Gráfico de Distribuição de Resultados

**O que mostra**: Proporção de vitórias, empates e derrotas

**Como interpretar**:
- **Verde**: % de vitórias
- **Cinza**: % de empates
- **Vermelho**: % de derrotas

**Útil para**: Visualizar rapidamente o perfil do time

## 🗓️ Histórico de Partidas

### Tabela de Partidas Recentes

Exibe todas as partidas analisadas com:
- **Data**: Data da partida
- **Adversário**: Time oponente
- **Local**: Casa ou Fora
- **Placar**: Resultado (gols do time - gols do adversário)
- **Resultado**: V (Vitória), E (Empate) ou D (Derrota)
- **Competição**: Nome da competição

**Cores**:
- 🟢 **Verde**: Vitória
- 🔴 **Vermelho**: Derrota
- ⚪ **Cinza**: Empate

## 💡 Dicas para Análise

### 1. Para Apostas em Resultado (1X2)

✅ **Procure por**:
- Times com alta taxa de vitória (>60%)
- Forma recente positiva (VVV ou VVEV)
- Bom desempenho no local do jogo (casa/fora)

❌ **Evite**:
- Times inconsistentes (forma alternada: VDVDV)
- Times com muitos empates (>35%)

### 2. Para Apostas em Over/Under 2.5

✅ **Over 2.5 quando**:
- Percentual Over 2.5 > 60%
- Média de gols total (marcados + sofridos) > 3.0
- Tendência de gols em alta nos últimos jogos

✅ **Under 2.5 quando**:
- Percentual Over 2.5 < 40%
- Defesa sólida (média gols sofridos < 1.0)
- Ataque fraco (média gols marcados < 1.2)

### 3. Para Apostas em BTTS (Both Teams to Score)

✅ **BTTS Sim quando**:
- Percentual BTTS > 60%
- Time marca bem MAS também sofre gols
- Defesa frágil (média sofridos > 1.5)

✅ **BTTS Não quando**:
- Percentual BTTS < 40%
- Defesa muito sólida OU ataque muito fraco
- Jogos com poucos gols no total

### 4. Para Gestão de Banca

📊 **Use as estatísticas para**:
- Confirmar suas análises antes de apostar
- Identificar value bets comparando com odds oferecidas
- Ajustar o tamanho da aposta baseado na consistência do time

⚠️ **Cuidado com**:
- Times em mudança de técnico (comportamento imprevisível)
- Primeiros jogos da temporada (pouco histórico)
- Times que enfrentam adversários muito diferentes do histórico

## 🔄 Combinando com Análise de Apostas

### Fluxo Recomendado:

1. **Selecione a partida** na aba "Análise de Apostas"
2. **Vá para "Análise de Times"** e analise ambos os times
3. **Volte para "Análise de Apostas"** com insights sobre:
   - Força ofensiva/defensiva de cada time
   - Forma recente
   - Desempenho casa/fora
   - Tendências de gols
4. **Insira as odds** com mais confiança
5. **Compare** as recomendações do sistema com sua análise

## 📊 Exemplos de Uso

### Exemplo 1: Time Ofensivo vs Time Defensivo

**Análise**:
- Time A: 70% Over 2.5, média 2.5 gols marcados
- Time B: 30% Over 2.5, média 0.8 gols sofridos

**Insight**: Odds de Over 2.5 podem não ser value bet, pois a defesa forte do Time B pode neutralizar o ataque do Time A

### Exemplo 2: Mando de Campo Decisivo

**Análise**:
- Time A em casa: 80% vitórias, média 2.3 gols
- Time A fora: 30% vitórias, média 0.9 gols

**Insight**: Apostar em vitória do Time A apenas quando joga em casa

### Exemplo 3: Identificando Valor em BTTS

**Análise**:
- Time A: 65% BTTS, defesa frágil (1.8 gols sofridos/jogo)
- Time B: 58% BTTS, ataque consistente (1.6 gols/jogo)

**Insight**: BTTS Sim tem alta probabilidade, verifique se as odds oferecem valor

## ⚙️ Configurações Recomendadas

### Número de Jogos para Análise

- **10-15 jogos**: Forma recente (últimas 5-6 semanas)
- **20-30 jogos**: Análise equilibrada (meio da temporada) ⭐ **RECOMENDADO**
- **40-50 jogos**: Análise completa da temporada

### Quando Usar Cada Configuração

- **Início da temporada**: 10-15 jogos (incluir temporada anterior)
- **Meio da temporada**: 20-30 jogos (melhor equilíbrio)
- **Final da temporada**: 30-50 jogos (visão completa)

## 🎓 Conclusão

A análise detalhada de times é uma ferramenta poderosa para:
- ✅ Confirmar as previsões dos modelos
- ✅ Identificar padrões não capturados pelos modelos estatísticos
- ✅ Aumentar sua confiança nas apostas
- ✅ Fazer gestão de banca mais inteligente

**Lembre-se**: Combine sempre a análise quantitativa (modelos) com a análise qualitativa (histórico e contexto) para tomar as melhores decisões!

---

**💰 Aposte com responsabilidade!**

