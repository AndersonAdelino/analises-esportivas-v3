# 🌎 Guia Multi-Ligas - Sistema de Análise

## 🎯 Visão Geral

O sistema agora suporta **múltiplas ligas de futebol**, permitindo que você analise e faça apostas em diferentes competições sem precisar mudar de ferramenta!

## 🏆 Ligas Suportadas

### 1. Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿
- **Código**: PL
- **País**: Inglaterra
- **Times**: 20 times
- **Características**: Liga mais competitiva do mundo, muitos dados disponíveis

### 2. Brasileirão Série A 🇧🇷
- **Código**: BSA
- **País**: Brasil
- **Times**: 20 times
- **Características**: Liga emocionante, muitos gols, jogos equilibrados

---

## 🚀 Como Usar

### 1. Coletar Dados

#### Opção 1: Via Script .bat (Windows)

```bash
# Execute o script
COLETAR_DADOS.bat

# Escolha uma opção:
# 1 - Premier League
# 2 - Brasileirão Série A
# 3 - Ambas as ligas
```

#### Opção 2: Via Python (qualquer SO)

**Premier League:**
```bash
python get_team_matches.py
# Escolha opção 1 no menu
```

**Brasileirão:**
```bash
python get_brasileirao_data.py
# OU
python get_team_matches.py
# Escolha opção 2 no menu
```

**Ambas:**
```bash
python get_team_matches.py
# Escolha opção 3 no menu
```

---

### 2. Usar a Interface Web

1. **Inicie o servidor:**
   ```bash
   streamlit run app_betting.py
   ```

2. **Selecione a liga:**
   - No **sidebar** (barra lateral esquerda)
   - Clique no dropdown **"🏆 Selecione a Liga"**
   - Escolha entre Premier League ou Brasileirão

3. **Análise de Apostas:**
   - Os modelos serão treinados automaticamente para a liga selecionada
   - Próximas partidas serão buscadas da liga escolhida
   - Todas as análises e predições serão específicas dessa liga

4. **Análise de Times:**
   - Times mostrados serão da liga selecionada
   - Históricos e estatísticas filtrados por liga

---

## 📊 Como Funciona

### Separação de Dados

```
data/
├── premier_league_matches_YYYYMMDD_HHMMSS.csv     # Dados da Premier League
├── brasileirao_serie_a_matches_YYYYMMDD_HHMMSS.csv   # Dados do Brasileirão
├── premier_league_teams_YYYYMMDD_HHMMSS.json
└── brasileirao_serie_a_teams_YYYYMMDD_HHMMSS.json
```

### Modelos Separados

Cada liga tem seus próprios modelos treinados:

- **Dixon-Coles**: Parâmetros específicos por liga (home advantage, rho, etc.)
- **Offensive-Defensive**: Forças de ataque/defesa por liga
- **Heurísticas**: Padrões específicos de cada campeonato

**Por quê?**
- Cada liga tem características únicas
- Home advantage varia entre ligas
- Padrões de gols e resultados são diferentes

---

## 🎓 Diferenças Entre as Ligas

### Premier League
- ✅ **Vantagens:**
  - Muitos dados históricos disponíveis
  - Padrões mais previsíveis
  - Menos surpresas
  - Melhor para value betting

- ⚠️ **Características:**
  - Home advantage menor (~20-25%)
  - Menos gols em média
  - Mais empates técnicos

### Brasileirão Série A
- ✅ **Vantagens:**
  - Odds geralmente mais atrativas
  - Menos pesquisado que PL
  - Mais oportunidades de value

- ⚠️ **Características:**
  - Home advantage maior (~30-35%)
  - Mais gols por jogo
  - Maior imprevisibilidade
  - Variação maior de desempenho

---

## 💡 Dicas de Uso

### 1. Coleta de Dados

**Recomendação: Colete ambas as ligas**
```bash
# Execute uma vez por semana
COLETAR_DADOS.bat
# Escolha opção 3 (Ambas)
```

**Vantagens:**
- Dados sempre atualizados
- Flexibilidade para analisar ambas
- Aproveita melhor as oportunidades

### 2. Análise de Apostas

**Compare as ligas:**
- Veja qual liga tem mais value bets no dia
- Brasileirão pode ter odds melhores
- Premier League pode ser mais previsível

**Exemplo de workflow:**
```
1. Selecione Premier League
2. Veja partidas e value bets disponíveis
3. Mude para Brasileirão
4. Compare oportunidades
5. Aposte onde houver melhor value
```

### 3. Gestão de Banca

**Separe ou unifique:**

**Opção 1: Banca única**
- Use a mesma banca para ambas
- Mais simples
- Kelly Criterion gerencia o risco

**Opção 2: Bancas separadas**
- 50% para Premier League
- 50% para Brasileirão
- Menor correlação de risco
- Melhor para iniciantes

### 4. Estratégias por Liga

**Premier League:**
- Foque em Under 2.5 gols
- Empates têm bom value
- Casa vs Fora bem definido

**Brasileirão:**
- Over 2.5 é mais comum
- BTTS (ambos marcam) frequente
- Zebras acontecem mais

---

## 🔧 Uso Programático

### Treinar modelos para liga específica

```python
from ensemble import EnsembleModel

# Premier League
ensemble_pl = EnsembleModel()
ensemble_pl.fit(league_code='PL')

# Brasileirão
ensemble_bsa = EnsembleModel()
ensemble_bsa.fit(league_code='BSA')

# Predições
pred_pl = ensemble_pl.predict_match('Arsenal FC', 'Liverpool FC')
pred_bsa = ensemble_bsa.predict_match('Flamengo', 'Palmeiras')
```

### Carregar dados de liga específica

```python
from dixon_coles import load_match_data

# Premier League
df_pl = load_match_data(league_code='PL')

# Brasileirão  
df_bsa = load_match_data(league_code='BSA')
```

---

## 📈 Monitoramento de Performance

### Por Liga

Mantenha registros separados:

```python
# ROI por liga
roi_premier = calcular_roi(apostas_premier)
roi_brasileirao = calcular_roi(apostas_brasileirao)

# Compare
if roi_premier > roi_brasileirao:
    print("Premier League está sendo mais lucrativa")
```

### Insights

- Algumas ligas podem ter melhor ROI em certas épocas
- Brasileirão pode ser mais lucrativo no início
- Premier League pode ser mais consistente

---

## 🆘 Troubleshooting

### Erro: "Nenhum arquivo encontrado para BSA"

**Solução:** Colete dados do Brasileirão primeiro
```bash
python get_brasileirao_data.py
```

### Modelos não carregam para nova liga

**Solução:** Limpe o cache do Streamlit
- Feche o navegador
- No terminal, pressione 'C' para limpar cache
- Ou reinicie o servidor

### Partidas não aparecem

**Causa:** Pode não haver partidas agendadas na API

**Solução:**
- Verifique se há jogos programados para a liga
- Tente novamente mais próximo da rodada
- Use modo de predição manual (insira times diretamente)

---

## 🌟 Próximas Ligas (Futuro)

Em desenvolvimento:
- 🇪🇸 La Liga (Espanha)
- 🇩🇪 Bundesliga (Alemanha)
- 🇮🇹 Serie A (Itália)
- 🇫🇷 Ligue 1 (França)

**Quer contribuir?** O código está pronto para adicionar mais ligas facilmente!

---

## 📖 Recursos Adicionais

### Documentação Relacionada
- [Guia de Value Betting](GUIA_VALUE_BETTING.md)
- [Guia de Análise de Times](GUIA_ANALISE_TIMES.md)
- [Início Rápido](INICIO_RAPIDO.md)

### Configuração
- Veja `config.py` para adicionar novas ligas
- Código da liga deve estar na API do Football-Data.org

---

## ✅ Checklist Multi-Ligas

Antes de analisar uma liga nova:

- [ ] Dados coletados (`COLETAR_DADOS.bat`)
- [ ] Liga selecionada no sidebar
- [ ] Modelos treinados com sucesso
- [ ] Partidas aparecem na lista
- [ ] Times aparecem na análise
- [ ] Predições funcionando

---

## 💰 Dicas Finais

1. **Comece com uma liga**
   - Domine Premier League primeiro
   - Depois expanda para Brasileirão

2. **Compare sempre**
   - Mesma partida pode ter odds diferentes
   - Aproveite onde há mais value

3. **Respeite as diferenças**
   - Cada liga tem suas peculiaridades
   - Ajuste estratégia conforme a liga

4. **Mantenha registros**
   - ROI por liga
   - Win rate por competição
   - Melhores mercados de cada uma

---

**🌎 Agora você pode analisar futebol do mundo todo! ⚽**

*Boa sorte e aposte com responsabilidade!* 🍀

---

**Versão:** 1.0  
**Data:** Outubro 2025  
**Projeto:** Análises Esportivas v3

