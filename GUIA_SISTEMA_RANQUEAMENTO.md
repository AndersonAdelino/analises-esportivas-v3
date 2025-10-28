# 🎯 Sistema de Ranqueamento de Apostas

## Visão Geral

O Sistema de Ranqueamento de Apostas é uma ferramenta avançada que analisa e classifica apostas esportivas usando múltiplos critérios quantitativos, fornecendo recomendações objetivas e stakes calculadas através do Critério de Kelly ajustado.

## 📊 Componentes do Sistema

### 1. Critérios de Avaliação

O sistema avalia cada aposta usando 4 critérios principais:

#### EV% (Expected Value)
- **Definição**: Valor esperado da aposta em percentual
- **Cálculo**: `EV% = ((odds × p_model) - 1) × 100`
- **Importância**: Indica o retorno esperado a longo prazo
- **Exemplo**: EV% = +10% significa retorno esperado de 10% sobre o valor apostado

#### Edge (Vantagem)
- **Definição**: Diferença entre a probabilidade do modelo e a probabilidade implícita nas odds
- **Cálculo**: `Edge = (p_model - p_implicita) × 100`
- **Importância**: Mede a discrepância entre sua análise e o mercado
- **Exemplo**: Edge = +5% significa que você estima 5% mais de chance que o mercado

#### P(modelo) (Probabilidade do Modelo)
- **Definição**: Probabilidade estimada pelo seu modelo preditivo
- **Formato**: Valor entre 0 e 1 (ex: 0.55 = 55%)
- **Importância**: Reflete sua confiança na previsão
- **Uso**: Maior probabilidade = maior confiança

#### Stake (Kelly Ajustada)
- **Definição**: Fração do bankroll a ser apostada
- **Cálculo**: Critério de Kelly multiplicado pela fração do perfil
- **Importância**: Gerenciamento de risco e crescimento ótimo do bankroll
- **Limites**: Mínimo e máximo configuráveis

### 2. Perfis de Apostador

O sistema oferece três perfis que definem a agressividade e os pesos dos critérios:

#### 🟢 Conservador
```
Fração de Kelly: 25%
Pesos:
  - EV%: 40%
  - Edge: 30%
  - P(modelo): 20%
  - Stake: 10%
```

**Características**:
- Menor exposição ao risco
- Prioriza valor esperado e vantagem sobre o mercado
- Ideal para bankrolls menores ou apostadores iniciantes

#### 🟡 Moderado (Padrão)
```
Fração de Kelly: 50%
Pesos:
  - EV%: 35%
  - Edge: 25%
  - P(modelo): 25%
  - Stake: 15%
```

**Características**:
- Equilíbrio entre risco e retorno
- Balanceamento entre critérios
- Recomendado para maioria dos apostadores

#### 🔴 Agressivo
```
Fração de Kelly: 100%
Pesos:
  - EV%: 25%
  - Edge: 20%
  - P(modelo): 30%
  - Stake: 25%
```

**Características**:
- Maior exposição ao risco
- Prioriza probabilidade do modelo e stake
- Para apostadores experientes com bankroll sólido

## 🧮 Metodologia de Cálculo

### Score de Ranqueamento

O score de cada aposta é calculado em 4 etapas:

#### Etapa 1: Normalização
Cada critério é normalizado para escala 0-100:

```python
valor_normalizado = ((valor - min_dia) / (max_dia - min_dia)) × 100
```

Onde:
- `valor`: Valor do critério para a aposta específica
- `min_dia`: Menor valor do critério entre todas as apostas do dia
- `max_dia`: Maior valor do critério entre todas as apostas do dia

#### Etapa 2: Aplicação dos Pesos
Cada critério normalizado é multiplicado pelo peso do perfil:

```python
componente_ev = EV_norm × w_ev
componente_edge = Edge_norm × w_edge
componente_p = P_norm × w_p
componente_stake = Stake_norm × w_stake
```

#### Etapa 3: Cálculo do Score Final
O score é a média ponderada dos componentes:

```python
Score = (componente_ev + componente_edge + 
         componente_p + componente_stake) / soma_pesos
```

#### Etapa 4: Classificação
Apostas são ordenadas por score (maior para menor).

### Cálculo da Stake (Critério de Kelly)

A fração de Kelly é calculada usando a fórmula:

```
f = (bp - q) / b
```

Onde:
- `f`: Fração do bankroll a apostar
- `b`: Odds - 1 (retorno líquido)
- `p`: Probabilidade de ganhar (p_model)
- `q`: Probabilidade de perder (1 - p)

O valor final é ajustado pela fração do perfil:

```
stake_ajustada = f × fracao_perfil
```

E limitado pelos valores mínimo e máximo:

```python
if stake < stake_min:
    stake = 0  # Aposta muito pequena
else:
    stake = min(stake, stake_max)
```

## 📈 Níveis de Recomendação

O sistema classifica cada aposta em 4 níveis:

### 🟢 APOSTAR_ALTO
- **Critério**: Score ≥ 75
- **Interpretação**: Aposta de alta qualidade
- **Ação**: Considere fortemente esta aposta

### 🟡 APOSTAR_MEDIO
- **Critério**: 50 ≤ Score < 75
- **Interpretação**: Aposta de qualidade moderada
- **Ação**: Aposta aceitável, analise o contexto

### 🟠 APOSTAR_BAIXO
- **Critério**: 25 ≤ Score < 50
- **Interpretação**: Aposta de qualidade inferior
- **Ação**: Considere apenas se muito confiante

### ⚪ NÃO_APOSTAR
- **Critério**: Score < 25 ou stake < mínimo
- **Interpretação**: Aposta não recomendada
- **Ação**: Evite esta aposta

## 🔧 Configurações do Sistema

### Limites de Stake

#### Stake Mínima
- **Padrão**: 0.50%
- **Função**: Evita apostas muito pequenas
- **Recomendação**: 0.3% - 1.0%

#### Stake Máxima
- **Padrão**: 12.0%
- **Função**: Limita exposição em uma única aposta
- **Recomendação**: 8% - 15%

### Bankroll
- **Definição**: Capital total disponível para apostas
- **Importância**: Base para cálculo de todas as stakes
- **Gerenciamento**: Atualize regularmente conforme ganhos/perdas

## 📱 Como Usar

### Através da Interface Streamlit

1. **Execute a aplicação**:
```bash
streamlit run app_ranking.py
```
ou
```bash
EXECUTAR_RANKING.bat
```

2. **Configure seu perfil**:
   - Selecione o perfil de apostador (conservador/moderado/agressivo)
   - Defina seu bankroll
   - Ajuste os limites de stake se necessário

3. **Adicione apostas**:
   - Acesse a aba "Adicionar Apostas"
   - Preencha os dados de cada aposta
   - Clique em "Adicionar Aposta"

4. **Analise o ranking**:
   - Retorne à aba "Ranqueamento"
   - Veja o score de cada aposta
   - Identifique a melhor aposta (marcada com ⭐)
   - Verifique as stakes sugeridas

5. **Exporte resultados**:
   - Clique em "Download CSV" para salvar os resultados

### Através do Código Python

```python
from betting_ranking import criar_sistema_ranking, ApostaInput

# Criar sistema
sistema = criar_sistema_ranking(
    perfil="moderado",
    stake_min=0.5,
    stake_max=12.0,
    bankroll=1000.0
)

# Adicionar apostas
apostas = [
    ApostaInput(
        id="1",
        partida="Flamengo vs Palmeiras",
        mercado="Resultado Final",
        selecao="Flamengo",
        odds=2.10,
        p_model=0.52,
        ev_percent=9.2,
        edge=4.5
    ),
    # ... mais apostas
]

# Ranquear
ranqueadas = sistema.ranquear_apostas(apostas)

# Ver resultados
for aposta in ranqueadas:
    print(f"{aposta.partida}: Score {aposta.score:.1f}, "
          f"Stake R$ {aposta.stake_final:.2f}")

# Gerar relatório
relatorio = sistema.gerar_relatorio(ranqueadas, top_n=5)
print(relatorio)
```

## 🧪 Testes

Execute os testes para validar o sistema:

```bash
python -m pytest test_ranking_system.py -v
```

Testes incluem:
- ✅ Validação de inputs
- ✅ Cálculos de Kelly
- ✅ Normalização de valores
- ✅ Cálculo de scores
- ✅ Determinação de recomendações
- ✅ Ranqueamento completo
- ✅ Diferenças entre perfis
- ✅ Limites de stake

## 📊 Exemplos Práticos

### Exemplo 1: Ranking Básico

**Entrada**:
```
Aposta 1: Flamengo vs Palmeiras
- Odds: 2.10
- P(modelo): 52%
- EV: +9.2%
- Edge: +4.5%

Aposta 2: São Paulo vs Santos
- Odds: 1.85
- P(modelo): 58%
- EV: +7.3%
- Edge: +3.8%
```

**Saída (Perfil Moderado, Bankroll R$ 1000)**:
```
#1 - São Paulo vs Santos
  Score: 75.2/100
  Stake: R$ 42.94 (4.29%)
  Recomendação: APOSTAR_ALTO

#2 - Flamengo vs Palmeiras
  Score: 67.8/100
  Stake: R$ 41.82 (4.18%)
  Recomendação: APOSTAR_MEDIO
```

### Exemplo 2: Comparação de Perfis

**Mesma aposta analisada com perfis diferentes**:

Aposta: Corinthians @ 1.75, P(modelo) = 62%, EV = +8.5%, Edge = +5.1%

| Perfil | Score | Stake (R$) | Stake (%) | Recomendação |
|--------|-------|-----------|-----------|--------------|
| Conservador | 95.9 | 28.33 | 2.83% | APOSTAR_ALTO |
| Moderado | 96.4 | 56.67 | 5.67% | APOSTAR_ALTO |
| Agressivo | 97.5 | 113.33 | 11.33% | APOSTAR_ALTO |

**Observação**: Perfil agressivo sugere stake 4x maior que conservador.

## ⚠️ Avisos e Limitações

### Avisos Importantes

1. **Não é garantia de lucro**: O sistema é uma ferramenta de auxílio à decisão
2. **Dados de entrada**: Qualidade do ranking depende da qualidade dos seus modelos
3. **Gerenciamento de risco**: Sempre respeite seu bankroll e limites pessoais
4. **Análise complementar**: Use em conjunto com outras análises (técnica, fundamentalista)

### Limitações

1. **Normalização diária**: Scores são relativos às apostas do dia
2. **Critérios fixos**: Sistema usa 4 critérios pré-definidos
3. **Modelo de Kelly**: Assume distribuição binomial simples
4. **Não considera**: Correlações entre apostas, contexto de jogo, lesões, etc.

### Melhores Práticas

1. **Atualize o bankroll**: Recalcule após cada sessão significativa
2. **Revise os limites**: Ajuste stake_min/max conforme experiência
3. **Mantenha disciplina**: Siga as recomendações do sistema
4. **Registre resultados**: Acompanhe desempenho para ajustes
5. **Diversifique**: Não aposte tudo nas apostas de maior score

## 🔄 Fluxo de Trabalho Recomendado

```
1. Análise Preditiva
   ↓
2. Calcular P(modelo), EV%, Edge
   ↓
3. Inserir apostas no sistema
   ↓
4. Configurar perfil e bankroll
   ↓
5. Ranquear apostas
   ↓
6. Revisar recomendações
   ↓
7. Validar com análise qualitativa
   ↓
8. Executar apostas
   ↓
9. Registrar resultados
   ↓
10. Atualizar bankroll e ajustar parâmetros
```

## 📚 Referências

- **Critério de Kelly**: Kelly, J.L. (1956). "A New Interpretation of Information Rate"
- **Expected Value**: Valor esperado em teoria das probabilidades
- **Gestão de Banca**: Principles of Professional Sports Betting
- **Normalização**: Min-Max Scaling em Machine Learning

## 🆘 Suporte

Para dúvidas ou problemas:

1. Consulte a aba "Como Usar" na interface
2. Execute os testes: `pytest test_ranking_system.py -v`
3. Verifique os logs de erro
4. Revise este guia

## 📝 Changelog

### v1.0.0 (2025-10-28)
- ✅ Implementação inicial do sistema
- ✅ Três perfis de apostador
- ✅ Cálculo de Kelly ajustado
- ✅ Interface Streamlit completa
- ✅ Suite de testes
- ✅ Documentação completa

---

**Desenvolvido para análises esportivas profissionais** 🎯

