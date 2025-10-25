# 🎰 Guia do Sistema de Apostas Múltiplas (Bingo)

## O que é?

Sistema que analisa seus palpites do dia e gera **UMA ÚNICA cartela otimizada** de apostas múltiplas (3-5 jogos), selecionando automaticamente os melhores palpites com base em Expected Value (EV) e probabilidade.

## 🚀 Como Usar

### Passo 1: Analisar Partidas
1. Abra o aplicativo: `streamlit run app_betting.py`
2. Vá na aba **"🎯 Análise de Apostas"**
3. Analise **pelo menos 3 partidas diferentes**
4. O sistema salvará automaticamente os **value bets** no cache

### Passo 2: Gerar o Bingo
1. Vá na aba **"🎰 Bingo (Apostas Múltiplas)"**
2. Veja quantas partidas e palpites estão em cache
3. Configure os filtros:
   - **Mínimo/Máximo de jogos**: 3-5 palpites na cartela
   - **EV% mínimo**: Valor esperado mínimo (padrão: 3%)
   - **Probabilidade mínima**: Chance mínima de cada palpite (padrão: 35%)
   - **Valor da aposta**: Quanto quer apostar na cartela
4. Clique em **"🎲 GERAR O MELHOR BINGO DO DIA"**

### Passo 3: Usar a Cartela
1. O sistema mostrará:
   - **Odd total** (multiplicação de todas as odds)
   - **Probabilidade combinada** de acerto
   - **EV% da múltipla**
   - **Retorno potencial e lucro esperado**
   - **Detalhes de cada palpite**
2. Copie os palpites e monte sua múltipla na casa de apostas!

## 📊 Como Funciona o Algoritmo

### Estratégia de Otimização:
1. **Filtra palpites** que atendem critérios mínimos (EV e probabilidade)
2. **Seleciona melhor palpite** de cada partida (maior score)
3. **Calcula score do palpite**: `(EV% × 0.6) + (Prob% × 0.4)`
4. **Gera TODAS as combinações** possíveis de 3-5 jogos
5. **Calcula métricas** de cada combinação
6. **Ranqueia** por score final
7. **Retorna a TOP 1** cartela

### Score da Cartela:
```
Quality Score = (EV% × 0.5) + (Prob% × 30) + (Num_jogos × 2)
```

Isso favorece cartelas com:
- ✅ Bom EV (value)
- ✅ Probabilidade razoável (confiabilidade)
- ✅ Mais jogos (maior odd total)

## 💡 Exemplo Prático

### Análises do Dia:
```
1. Arsenal vs Chelsea - Vitória Casa
   Odd: 2.10 | Prob: 55% | EV: +15.5%

2. Liverpool vs Man City - Over 2.5
   Odd: 1.75 | Prob: 65% | EV: +13.8%

3. Tottenham vs Brighton - BTTS Sim
   Odd: 1.90 | Prob: 60% | EV: +14.0%

4. Newcastle vs Wolves - Vitória Casa
   Odd: 2.20 | Prob: 50% | EV: +10.0%
```

### Melhor Cartela Gerada:
```
📊 MÉTRICAS:
- Odd Total: 15.36
- Probabilidade: 10.73%
- Score: 43.59

💰 FINANCEIRO:
- Investimento: R$ 100.00
- Retorno se acertar: R$ 1,536.15
- Lucro esperado (EV): R$ +64.75
- ROI esperado: +64.75%

🎯 PALPITES: 4 jogos (todos os acima)
```

## 🔍 Entendendo as Métricas

### Odd Total
Multiplicação de todas as odds: `2.10 × 1.75 × 1.90 × 2.20 = 15.36`

### Probabilidade Combinada
Produto das probabilidades: `0.55 × 0.65 × 0.60 × 0.50 = 10.73%`

### EV da Múltipla
```
EV = (Prob × Odd × Stake) - Stake
EV = (0.1073 × 15.36 × 100) - 100
EV = R$ 64.75
```

### ROI Esperado
```
ROI% = (EV / Stake) × 100 = 64.75%
```

## ⚙️ Configurações Recomendadas

### Para Conservador:
- Min jogos: 3
- Max jogos: 3
- EV% mínimo: 8%
- Prob mínima: 50%

**Resultado:** Cartelas triplas com alta confiabilidade

### Para Moderado (Recomendado):
- Min jogos: 3
- Max jogos: 5
- EV% mínimo: 3%
- Prob mínima: 35%

**Resultado:** Balanceia value com probabilidade

### Para Agressivo:
- Min jogos: 4
- Max jogos: 5
- EV% mínimo: 0%
- Prob mínima: 30%

**Resultado:** Cartelas maiores com odds mais altas

## ⚠️ Avisos Importantes

### Regras:
1. **Cache diário**: O cache é limpo automaticamente à meia-noite
2. **Mínimo 3 partidas**: Precisa analisar pelo menos 3 jogos diferentes
3. **1 palpite por jogo**: O sistema seleciona apenas o MELHOR de cada partida
4. **Value bets only**: Apenas palpites com EV positivo são salvos

### Validações:
- ✅ Garante jogos únicos (sem repetir partida)
- ✅ Valida ranges (odds > 1.01, prob 0-100%)
- ✅ Alerta se nenhuma combinação atende os critérios
- ✅ Mostra quantas combinações foram analisadas

## 🎯 Dicas de Uso

### Maximize seus Resultados:
1. **Analise mais partidas**: Quanto mais opções, melhor a cartela
2. **Seja seletivo**: Configure filtros baseados no seu perfil de risco
3. **Compare com simples**: Às vezes apostar em simples pode ser melhor
4. **Use com moderação**: Múltiplas são arriscadas, aposte consciente

### Gestão de Banca:
- **Nunca aposte mais que 5% da banca** em múltiplas
- **Considere o EV da cartela**: Positivo = boa aposta a longo prazo
- **Probabilidade < 10%** = High risk, high reward
- **Probabilidade > 20%** = Mais equilibrado

## 🔄 Limpeza de Cache

Se quiser recomeçar:
1. Clique no botão **"🔄 Limpar Cache e Começar Novo Bingo"**
2. Ou feche e reabra o aplicativo

Cache é **automaticamente limpo** todo dia à meia-noite.

## 📈 Interpretando Resultados

### Score de Qualidade:
- **< 30**: Cartela fraca
- **30-40**: Cartela média
- **40-50**: Cartela boa ✅
- **> 50**: Cartela excelente ⭐

### EV da Múltipla:
- **< 0%**: Sem value (não aposte!)
- **0-20%**: Value baixo
- **20-50%**: Value moderado ✅
- **> 50%**: Value alto ⭐

### Probabilidade Combinada:
- **< 5%**: Muito arriscado
- **5-15%**: Alto risco, alta recompensa
- **15-30%**: Equilibrado ✅
- **> 30%**: Conservador

## 🤔 FAQ

### "Não consigo gerar cartela"
- Verifique se analisou pelo menos 3 partidas diferentes
- Reduza os filtros mínimos (EV% e Probabilidade)
- Analise mais jogos para ter mais opções

### "Probabilidade muito baixa"
- Normal em múltiplas! 10% é razoável para 4 jogos
- Use menos jogos se quer maior probabilidade
- Aumente o filtro de "Probabilidade mínima"

### "EV negativo mesmo com value bets"
- Isso pode acontecer se as probabilidades forem muito baixas
- O sistema sempre busca a melhor combinação disponível
- Se EV < 0, considere apostar em simples

### "Cache vazio após fechar app"
- Cache persiste durante o dia no session_state
- Se fechar o app, precisa analisar novamente
- Isso é intencional para garantir dados frescos

## 🎓 Exemplo Completo de Uso

```
1. Abrir app: streamlit run app_betting.py

2. Aba "Análise de Apostas":
   - Analisar Arsenal vs Chelsea → 2 value bets encontrados
   - Analisar Liverpool vs City → 3 value bets encontrados
   - Analisar Tottenham vs Brighton → 2 value bets encontrados
   - Analisar Newcastle vs Wolves → 1 value bet encontrado
   Total: 8 palpites em cache, 4 partidas

3. Aba "Bingo":
   - Configurar: 3-5 jogos, EV > 3%, Prob > 35%
   - Stake: R$ 100
   - Clicar "GERAR BINGO"
   
4. Resultado:
   - Cartela com 4 jogos
   - Odd total: 15.36
   - Prob: 10.73%
   - EV: +64.75%
   - Lucro esperado: R$ 64.75
   
5. Ação:
   - Copiar palpites
   - Montar múltipla na casa de apostas
   - Apostar R$ 100
```

---

## 🎉 Pronto!

Você agora tem um sistema automático que:
- ✅ Coleta seus melhores palpites do dia
- ✅ Analisa TODAS as combinações possíveis
- ✅ Gera a MELHOR cartela otimizada
- ✅ Mostra métricas completas e confiáveis

**Aposte com dados, não com emoção! 💰**

---

**Desenvolvido para o projeto Análises Esportivas v3**
*Última atualização: Outubro 2025*

