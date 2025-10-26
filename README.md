# ⚽ Análises Esportivas - Multi-Ligas

Projeto de análise de dados esportivos utilizando dados históricos de **múltiplas ligas de futebol** através da API gratuita do [Football-Data.org](https://www.football-data.org/).

## 🏆 Ligas Suportadas

- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 **Premier League** (Inglaterra)
- 🇧🇷 **Brasileirão Série A** (Brasil)

**Novo!** Sistema totalmente adaptado para múltiplas ligas com modelos separados e interface intuitiva!

## 📋 Funcionalidades

### 🎰 Apostas Múltiplas (BINGO) - NOVO!
- ✅ **Sistema inteligente de apostas múltiplas**
- ✅ **Gera a MELHOR cartela otimizada do dia (3-5 jogos)**
- ✅ **Análise de TODAS as combinações possíveis**
- ✅ **Cache automático de análises diárias**
- ✅ **Métricas completas (Odd total, Probabilidade, EV)**
- ✅ **Interface intuitiva e visual**

### Coleta e Análise de Dados
- ✅ **🌎 Suporte a múltiplas ligas (Premier League + Brasileirão)**
- ✅ **🔄 Seletor de liga na interface web**
- ✅ Busca de dados históricos de partidas
- ✅ Exportação de dados em JSON e CSV
- ✅ Informações detalhadas de times
- ✅ Tabela de classificação
- ✅ Cliente Python para a API do Football-Data.org

### Modelos Preditivos
- ✅ **Modelo Dixon-Coles para predição de resultados**
- ✅ **Modelo Offensive-Defensive (alternativa mais rápida)**
- ✅ **Sistema de Heurísticas (análise baseada em regras)**
- ✅ **Cálculo de probabilidades (1X2, Over/Under, BTTS, Placares)**
- ✅ **Análise de forças de ataque e defesa dos times**
- ✅ **Comparação completa entre os 3 modelos**
- ✅ **🔍 Comparação Detalhada com Visualizações (NOVO!)**
  - Gráficos comparativos de probabilidades
  - Heatmaps de placares prováveis (6x6)
  - Gráfico radar multidimensional
  - Métricas de divergência e consenso
  - Recomendações automáticas baseadas em confiança

### Value Betting & Análise Avançada
- ✅ **Ensemble de modelos com pesos otimizados**
- ✅ **Expected Value (EV) e Kelly Criterion**
- ✅ **Interface web interativa com Streamlit**
- ✅ **📊 Análise detalhada de times com histórico completo**
- ✅ **📈 5 tipos de gráficos interativos (Plotly)**
- ✅ **🏠 Comparação de desempenho Casa vs Fora**
- ✅ **⚽ Tendências de gols e forma recente**
- ✅ **🎯 Estatísticas para apostas (Over/Under, BTTS)**
- ✅ **🔍 Comparação visual detalhada entre modelos (NOVO!)**
  - Visualize como cada modelo chegou às conclusões
  - Heatmaps de placares mais prováveis
  - Análise de convergência e consenso
  - Métricas de confiança nas predições

### 💰 Gerenciamento de Banca
- ✅ **Configuração e rastreamento de banca real**
- ✅ **Registro de apostas com 1 clique**
- ✅ **Acompanhamento de apostas pendentes**
- ✅ **Finalização automática com atualização de saldo**
- ✅ **Histórico completo de apostas**
- ✅ **Estatísticas: Win Rate, ROI, Lucro Total**
- ✅ **Gráfico de evolução da banca**
- ✅ **Banco de dados SQLite persistente**


## 🚀 Instalação

### 🪟 **Windows - Modo Fácil (Recomendado)**

**Duplo clique nos executáveis:**
1. `INSTALAR_DEPENDENCIAS.bat` - Instala tudo
2. Criar arquivo `.env` com sua API Key
3. `COLETAR_DADOS.bat` - Busca dados
4. `INICIAR_SERVIDOR.bat` - Abre interface web!

📖 **Veja:** `COMO_USAR_EXECUTAVEIS.txt` ou `README_EXECUTAVEIS.md`

---

### 💻 **Instalação Manual (Windows/Linux/Mac)**

#### 1. Clone o repositório ou navegue até a pasta do projeto

```bash
cd analises_esportivas_v3
```

#### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 3. Configure sua API Key

1. Acesse [Football-Data.org](https://www.football-data.org/client/register) e registre-se gratuitamente
2. Copie sua API Key
3. Crie um arquivo `.env` na raiz do projeto:

```bash
FOOTBALL_DATA_API_KEY=sua_chave_api_aqui
```

> ⚠️ **Importante**: Nunca compartilhe sua API Key publicamente!

## 📊 Uso

### 1. Buscar dados históricos das últimas 20 partidas

Execute o script principal:

```bash
python get_historical_data.py
```

Este script irá:
- Buscar as últimas 20 partidas finalizadas da Premier League
- Salvar os dados brutos em JSON
- Criar um CSV com dados processados
- Buscar informações dos times da competição
- Exibir estatísticas básicas

### 2. Buscar últimas 20 partidas de cada time

```bash
python get_team_matches.py
```

Coleta dados individuais de cada time (em todas as competições).

### 3. Análises Estatísticas

```bash
python analise_basica.py          # Análise geral da PL
python analise_por_time.py        # Análise detalhada por time
```

### 4. 🔮 Modelos Preditivos

#### 🎯 Dixon-Coles (mais preciso, estatístico)
```bash
python dixon_coles.py                    # Exemplos
python prever_proximas_partidas.py       # Próximas partidas da API
python predicao_interativa.py            # Interface interativa
```

#### ⚡ Offensive-Defensive (mais rápido, estatístico)
```bash
python offensive_defensive.py             # Exemplos
python prever_com_offensive_defensive.py  # Próximas partidas
```

#### 🧠 Heurísticas (baseado em regras e padrões)
```bash
python heuristicas.py                     # Exemplos
python prever_com_heuristicas.py          # Interface interativa
```

#### 🔍 Comparação entre os 3 modelos
```bash
python comparar_modelos.py                # Compara DC vs OD
python comparar_modelos_completo.py       # Compara DC vs OD vs Heurísticas
```

📖 **Documentação Completa:**
- [Guia Dixon-Coles](docs/DIXON_COLES_GUIA.md) - Modelo estatístico avançado
- [Guia Offensive-Defensive](docs/OFFENSIVE_DEFENSIVE_GUIA.md) - Modelo estatístico simplificado
- [Guia Heurísticas](docs/HEURISTICAS_GUIA.md) - Sistema de análise por regras
- [Guia Comparação de Modelos](docs/GUIA_COMPARACAO_MODELOS.md) - Análise visual detalhada (NOVO!)
- [Exemplos de Uso](docs/EXEMPLOS_USO.md) - Casos práticos

### Usar o cliente da API diretamente

```python
from api_client import FootballDataClient

# Inicializa o cliente
client = FootballDataClient()

# Busca partidas da Premier League
matches = client.get_competition_matches('PL', status='FINISHED', limit=20)

# Busca partidas de um time específico (ex: Manchester United - ID 66)
team_matches = client.get_team_matches(66, limit=10)

# Busca classificação da Premier League
standings = client.get_competition_standings('PL')

# Busca times da Premier League
teams = client.get_competition_teams('PL')
```

### Usar os Modelos Preditivos

**Dixon-Coles (estatístico):**
```python
from dixon_coles import DixonColesModel

model = DixonColesModel()
model.load_data()
model.fit()

pred = model.predict_match('Arsenal FC', 'Liverpool FC')
print(f"Vitória Casa: {pred['prob_casa']*100:.1f}%")
print(f"Empate: {pred['prob_empate']*100:.1f}%")
print(f"Over 2.5: {pred['prob_over_2_5']*100:.1f}%")
```

**Heurísticas (regras):**
```python
from heuristicas import HeuristicasModel

model = HeuristicasModel()
model.load_data()

pred = model.predict_match('Arsenal FC', 'Liverpool FC')
print(f"Resultado: {pred['resultado_previsto']}")
print(f"Confiança: {pred['confianca']}%")
print(f"Over/Under: {pred['over_under']}")

# Análises específicas
forma = model.forma_recente('Arsenal FC', n_jogos=5)
confronto = model.confronto_direto('Arsenal FC', 'Liverpool FC')
```

## 📁 Estrutura do Projeto

```
analises_esportivas_v3/
├── data/                              # Dados coletados (JSON e CSV)
│   ├── *_matches_*.csv                # Partidas coletadas
│   ├── *_teams_*.json                 # Informações dos times
│   └── predicoes_*.csv                # Predições dos modelos
├── .env                               # Configurações (API Key) - NÃO COMMITAR
├── .gitignore                         # Arquivos ignorados pelo Git
├── config.py                          # Configurações do projeto
│
├── # === COLETA DE DADOS ===
├── api_client.py                      # Cliente para a API Football-Data
├── get_historical_data.py             # Busca partidas da PL
├── get_team_matches.py                # Busca partidas por time
│
├── # === ANÁLISES ===
├── analise_basica.py                  # Análise geral da PL
├── analise_por_time.py                # Análise detalhada por time
│
├── # === MODELOS PREDITIVOS ===
├── dixon_coles.py                     # 🎯 Modelo Dixon-Coles
├── offensive_defensive.py             # ⚡ Modelo Offensive-Defensive
├── heuristicas.py                     # 🧠 Sistema de Heurísticas
│
├── # === SCRIPTS DE PREDIÇÃO ===
├── predicao_interativa.py             # Interface interativa (Dixon-Coles)
├── prever_proximas_partidas.py        # Próximas partidas (Dixon-Coles)
├── prever_com_offensive_defensive.py  # Próximas partidas (OD)
├── prever_com_heuristicas.py          # Análise interativa (Heurísticas)
├── gerar_predicoes_lote.py            # Predições em lote
│
├── # === COMPARAÇÃO DE MODELOS ===
├── comparar_modelos.py                # Compara DC vs OD
├── comparar_modelos_completo.py       # Compara DC vs OD vs Heurísticas
│
├── # === VALUE BETTING & INTERFACE ===
├── app_betting.py                     # 🌐 Interface Web Streamlit (com análise de times!)
├── ensemble.py                        # Ensemble dos 3 modelos
├── betting_tools.py                   # EV e Kelly Criterion
├── bankroll_manager.py                # 💰 Gerenciador de banca (NOVO!)
├── test_bankroll_system.py            # 🧪 Teste do sistema de banca (NOVO!)
│
├── # === DOCUMENTAÇÃO ===
├── README.md                          # Este arquivo
├── docs/                              # 📚 Toda a documentação organizada
│   ├── README.md                      # Índice da documentação
│   ├── INICIO_RAPIDO.md               # ⚡ Comece aqui!
│   ├── GUIA_ANALISE_TIMES.md          # 📊 Análise de times (NOVO!)
│   ├── ESTRUTURA_ANALISE_TIMES.md     # 🏗️ Arquitetura técnica (NOVO!)
│   ├── GUIA_VALUE_BETTING.md          # 💰 Value betting
│   ├── DIXON_COLES_GUIA.md            # 🎯 Modelo Dixon-Coles
│   ├── OFFENSIVE_DEFENSIVE_GUIA.md    # ⚡ Modelo Offensive-Defensive
│   ├── HEURISTICAS_GUIA.md            # 🧠 Modelo Heurísticas
│   ├── EXEMPLOS_USO.md                # 💡 Exemplos práticos
│   ├── COMO_USAR_STREAMLIT.md         # 🌐 Interface web
│   └── README_EXECUTAVEIS.md          # 🔧 Scripts Windows
│
├── # === SCRIPTS BATCH (WINDOWS) ===
├── INSTALAR_DEPENDENCIAS.bat          # Instala dependências
├── ATUALIZAR_DEPENDENCIAS.bat         # Atualiza dependências (NOVO!)
├── COLETAR_DADOS.bat                  # Coleta dados da API
├── INICIAR_SERVIDOR.bat               # Inicia Streamlit
├── TESTAR_NOVA_FUNCIONALIDADE.bat     # Testa análise de times (NOVO!)
│
├── # === OUTROS ===
├── example_usage.py                   # Exemplos de uso da API
└── requirements.txt                   # Dependências Python (+ Plotly!)
```

## 📊 Dados Disponíveis

### Partidas
- ID da partida
- Data e horário
- Times (casa e visitante)
- Placar final
- Status da partida
- Rodada
- Estádio
- Vencedor
- Temporada

### Times
- Nome completo
- Nome curto
- Escudo (URL)
- Fundação
- Cores
- Estádio

## 🔧 API Football-Data.org

### Limites do Plano Gratuito
- 10 requisições por minuto
- Acesso às principais competições europeias
- Dados básicos de partidas e times

### Endpoints Principais

| Endpoint | Descrição |
|----------|-----------|
| `/competitions/{code}/matches` | Partidas de uma competição |
| `/teams/{id}/matches` | Partidas de um time |
| `/competitions/{code}/standings` | Classificação |
| `/competitions/{code}/teams` | Times da competição |

Documentação completa: [https://www.football-data.org/documentation/quickstart](https://www.football-data.org/documentation/quickstart)

## 🎯 Funcionalidades Implementadas

### Coleta e Processamento
- [x] Coleta de dados históricos da Premier League
- [x] Análise estatística das partidas
- [x] Análise detalhada por time

### Modelos Preditivos
- [x] **Modelo Dixon-Coles para predições (estatístico avançado)**
- [x] **Modelo Offensive-Defensive (estatístico simplificado)**
- [x] **Sistema de Heurísticas (baseado em regras e padrões)**
- [x] **Cálculo de probabilidades (1X2, Over/Under, BTTS, Placares)**
- [x] **Interface interativa para predições**
- [x] **Gerador de predições em lote**
- [x] **Análise de forças de ataque/defesa**
- [x] **Comparação completa entre os 3 modelos**

### Value Betting & Interface
- [x] **Ensemble de modelos com pesos otimizados**
- [x] **Expected Value (EV) e Kelly Criterion**
- [x] **Interface web com Streamlit**
- [x] **Sistema de recomendação de apostas**

### Análise de Times (📊 NOVO!)
- [x] **Histórico completo de qualquer time da PL**
- [x] **5 tipos de gráficos interativos (Plotly)**
- [x] **Estatísticas detalhadas para apostas**
- [x] **Comparação Casa vs Fora**
- [x] **Análise de tendências e forma**
- [x] **Tabela de histórico com código de cores**

### 5. 💰 Value Betting System & Análise de Times

**Sistema completo de apostas com value:**
```bash
streamlit run app_betting.py        # Interface web interativa
python ensemble.py                  # Teste do ensemble
python betting_tools.py             # Teste EV e Kelly
```

**Features - Análise de Apostas:**
- ✅ Ensemble dos 3 modelos (pesos: DC 55%, OD 30%, H 15%)
- ✅ Cálculo de Expected Value (EV)
- ✅ Kelly Criterion para gestão de banca
- ✅ Interface web com Streamlit
- ✅ Análise de value bets automática
- ✅ Recomendações de stake

**Features - Análise de Times (📊 NOVO!):**
- ✅ Histórico completo de qualquer time da Premier League (até 50 jogos)
- ✅ 5 tipos de gráficos interativos:
  - 🎯 Resultados ao longo do tempo (com código de cores)
  - ⚽ Tendência de gols (média móvel 5 jogos)
  - 📈 Forma e acúmulo de pontos vs esperado
  - 🏠 Comparação Casa vs Fora
  - 📋 Distribuição de resultados (Pizza)
- ✅ Estatísticas detalhadas:
  - Vitórias, empates, derrotas e taxa de vitória
  - Gols marcados/sofridos e médias
  - % Over 2.5 gols e BTTS (Both Teams Score)
  - Forma recente (últimos 5 jogos)
  - Desempenho específico por local (casa/fora)
- ✅ Tabela de histórico de partidas com código de cores
- ✅ Cache inteligente para performance otimizada

**Como usar:**
1. Execute: `streamlit run app_betting.py`
2. Clique na aba **"📊 Análise de Times"**
3. Selecione um time e número de jogos (10-50)
4. Explore gráficos e estatísticas
5. Use insights para análise de apostas!

📖 **Documentação:**
- [📚 Índice Completo](docs/README.md) - Toda a documentação organizada
- [⚡ Início Rápido](docs/INICIO_RAPIDO.md) - Comece em 3 passos!
- [💰 Guia Value Betting](docs/GUIA_VALUE_BETTING.md) - Sistema completo
- [📊 Guia Análise de Times](docs/GUIA_ANALISE_TIMES.md) - Análise visual
- [🏗️ Estrutura Técnica](docs/ESTRUTURA_ANALISE_TIMES.md) - Arquitetura do sistema

**Scripts úteis:**
```bash
ATUALIZAR_DEPENDENCIAS.bat    # Instala Plotly e outras dependências
TESTAR_NOVA_FUNCIONALIDADE.bat # Testa a nova funcionalidade
```

---

## 🚀 Deploy Online

### Streamlit Cloud (Recomendado)

O projeto está **pronto para deploy** no Streamlit Cloud!

**Guias de Deploy:**
- 📖 [DEPLOY_RESUMO.md](DEPLOY_RESUMO.md) - Resumo visual (⏱️ 5 minutos)
- 📖 [README_DEPLOY.md](README_DEPLOY.md) - Guia rápido
- 📖 [DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md) - Guia completo
- 📖 [CHECKLIST_DEPLOY.md](CHECKLIST_DEPLOY.md) - Checklist passo a passo
- 📖 [COMANDOS_GIT.md](COMANDOS_GIT.md) - Comandos Git úteis

**Deploy em 3 passos:**
1. Push para GitHub
2. Conectar no Streamlit Cloud
3. Configurar API Key

**Resultado:** App online 24/7 acessível de qualquer lugar! 🌐

---

## 🚀 Próximos Passos Possíveis

- [x] Visualizações com matplotlib/seaborn
- [x] Dashboard interativo com Streamlit
- [x] **Sistema de apostas múltiplas (BINGO)**
- [x] **Deploy no Streamlit Cloud**
- [ ] Validação do modelo (Brier Score, ROI)
- [ ] Ensemble com outros modelos (Elo Rating, XGBoost)
- [x] Análise de value bets
- [ ] API REST para servir predições

## 📝 Notas

- Os dados são salvos na pasta `data/` com timestamp
- O script trata automaticamente limites de requisições (HTTP 429)
- Certifique-se de manter seu `.env` fora do controle de versão

## 🤝 Contribuições

Sinta-se à vontade para expandir este projeto com novas análises e funcionalidades!

## 📄 Licença

Este projeto é de código aberto e está disponível para uso educacional e pessoal.

---

**Desenvolvido com ⚽ e Python 🐍**

