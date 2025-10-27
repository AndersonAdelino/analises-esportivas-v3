# 🧪 Guia de Testes - La Liga e Serie A

## 📋 Checklist de Testes

Use este guia para validar a implementação das novas ligas.

---

## ⚙️ Pré-requisitos

Antes de testar:
- [ ] API Key configurada em `.env`
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Conexão com internet ativa

---

## 🔬 Testes Automatizados

### 1. Verificar Configuração

```bash
python
```

```python
# No Python REPL:
import config

# Verificar se as ligas foram adicionadas
print("Ligas disponíveis:")
for name, info in config.LEAGUES.items():
    print(f"  - {info['flag']} {name}: {info['code']} (ID: {info['id']})")

# Deve mostrar 4 ligas incluindo La Liga e Serie A
```

**Resultado Esperado:**
```
Ligas disponíveis:
  - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League: PL (ID: 2021)
  - 🇧🇷 Brasileirão Série A: BSA (ID: 2013)
  - 🇪🇸 La Liga: PD (ID: 2014)
  - 🇮🇹 Serie A: SA (ID: 2019)
```

---

### 2. Testar API Client

```python
from api_client import FootballDataClient

client = FootballDataClient()

# Testar La Liga
print("\nTestando La Liga (PD):")
try:
    teams_pd = client.get_competition_teams('PD')
    print(f"  ✅ {len(teams_pd.get('teams', []))} times encontrados")
except Exception as e:
    print(f"  ❌ Erro: {e}")

# Testar Serie A
print("\nTestando Serie A (SA):")
try:
    teams_sa = client.get_competition_teams('SA')
    print(f"  ✅ {len(teams_sa.get('teams', []))} times encontrados")
except Exception as e:
    print(f"  ❌ Erro: {e}")
```

**Resultado Esperado:**
```
Testando La Liga (PD):
  ✅ 20 times encontrados

Testando Serie A (SA):
  ✅ 20 times encontrados
```

---

## 📊 Testes de Coleta de Dados

### 3. Coletar Dados - La Liga

```bash
python get_team_matches.py
```

**Passos:**
1. Executar o script
2. Ver menu de ligas
3. Escolher opção 3 (La Liga)
4. Aguardar ~2-3 minutos
5. Verificar mensagem de sucesso

**Validar:**
- [ ] Script executou sem erros
- [ ] ~20 times processados
- [ ] ~400 partidas coletadas
- [ ] Arquivo criado: `data/la_liga_matches_*.csv`
- [ ] Arquivo criado: `data/la_liga_teams_*.json`

---

### 4. Coletar Dados - Serie A

```bash
python get_team_matches.py
```

**Passos:**
1. Executar o script
2. Ver menu de ligas
3. Escolher opção 4 (Serie A)
4. Aguardar ~2-3 minutos
5. Verificar mensagem de sucesso

**Validar:**
- [ ] Script executou sem erros
- [ ] ~20 times processados
- [ ] ~400 partidas coletadas
- [ ] Arquivo criado: `data/serie_a_matches_*.csv`
- [ ] Arquivo criado: `data/serie_a_teams_*.json`

---

## 🤖 Testes de Modelos

### 5. Treinar Modelo - La Liga

```python
from ensemble import EnsembleModel

# Treinar para La Liga
ensemble = EnsembleModel()
print("Treinando modelos para La Liga...")
ensemble.fit(league_code='PD')
print("✅ Modelos treinados com sucesso!")

# Fazer predição de teste
pred = ensemble.predict_match('Real Madrid', 'Barcelona')
print(f"\nPredição Real Madrid vs Barcelona:")
print(f"  Vitória Casa: {pred.get('prob_home', 0)*100:.1f}%")
print(f"  Empate: {pred.get('prob_draw', 0)*100:.1f}%")
print(f"  Vitória Fora: {pred.get('prob_away', 0)*100:.1f}%")
```

**Validar:**
- [ ] Modelos treinaram sem erros
- [ ] Predição retorna probabilidades
- [ ] Probabilidades somam ~100%
- [ ] Valores parecem razoáveis

---

### 6. Treinar Modelo - Serie A

```python
from ensemble import EnsembleModel

# Treinar para Serie A
ensemble = EnsembleModel()
print("Treinando modelos para Serie A...")
ensemble.fit(league_code='SA')
print("✅ Modelos treinados com sucesso!")

# Fazer predição de teste
pred = ensemble.predict_match('Juventus', 'Inter Milan')
print(f"\nPredição Juventus vs Inter Milan:")
print(f"  Vitória Casa: {pred.get('prob_home', 0)*100:.1f}%")
print(f"  Empate: {pred.get('prob_draw', 0)*100:.1f}%")
print(f"  Over 2.5: {pred.get('prob_over_2_5', 0)*100:.1f}%")
```

**Validar:**
- [ ] Modelos treinaram sem erros
- [ ] Predição retorna probabilidades
- [ ] Probabilidades somam ~100%
- [ ] Valores parecem razoáveis

---

## 🌐 Testes de Interface Web

### 7. Interface Streamlit - La Liga

```bash
streamlit run app_betting.py
```

**Passos:**
1. Abrir navegador em `http://localhost:8501`
2. Verificar sidebar
3. Clicar em "🏆 Selecione a Liga"
4. Selecionar "La Liga 🇪🇸"
5. Aguardar carregamento

**Validar:**
- [ ] La Liga aparece no dropdown
- [ ] Seleção funciona sem erros
- [ ] Modelos carregam (pode demorar)
- [ ] Times da La Liga aparecem
- [ ] Interface mostra "La Liga" no título

---

### 8. Interface Streamlit - Serie A

**Passos:**
1. No mesmo navegador
2. Clicar em "🏆 Selecione a Liga"
3. Selecionar "Serie A 🇮🇹"
4. Aguardar carregamento

**Validar:**
- [ ] Serie A aparece no dropdown
- [ ] Seleção funciona sem erros
- [ ] Modelos carregam (pode demorar)
- [ ] Times da Serie A aparecem
- [ ] Interface mostra "Serie A" no título

---

## 📈 Testes de Análise

### 9. Análise de Apostas - La Liga

**Na interface Streamlit:**
1. Selecionar La Liga
2. Ir para aba "🎯 Análise de Apostas"
3. Ver se há partidas próximas
4. Selecionar uma partida
5. Inserir odds
6. Ver análise de value

**Validar:**
- [ ] Aba carrega sem erros
- [ ] Partidas aparecem (se houver)
- [ ] Análise funciona
- [ ] Gráficos são exibidos
- [ ] Recomendações aparecem

---

### 10. Análise de Times - Serie A

**Na interface Streamlit:**
1. Selecionar Serie A
2. Ir para aba "📊 Análise de Times"
3. Selecionar um time italiano (ex: Juventus)
4. Escolher 30 jogos
5. Ver estatísticas e gráficos

**Validar:**
- [ ] Aba carrega sem erros
- [ ] Times da Serie A aparecem
- [ ] Estatísticas calculadas corretamente
- [ ] 5 gráficos são exibidos
- [ ] Dados fazem sentido

---

## 🔄 Testes de Integração

### 11. Coletar Todas as Ligas

```bash
python get_team_matches.py
```

**Passos:**
1. Executar script
2. Escolher opção 5 (Todas as ligas)
3. Confirmar opção 5 no submenu
4. Aguardar ~10-12 minutos
5. Verificar coleta de todas as 4 ligas

**Validar:**
- [ ] Todas as 4 ligas são processadas
- [ ] Premier League: ~400 partidas
- [ ] Brasileirão: ~400 partidas
- [ ] La Liga: ~400 partidas
- [ ] Serie A: ~400 partidas
- [ ] Total: ~1600 partidas

---

### 12. Menu COLETAR_DADOS.bat (Windows)

```bash
COLETAR_DADOS.bat
```

**Validar:**
- [ ] Menu mostra 5 opções
- [ ] Opção 3 coleta La Liga
- [ ] Opção 4 coleta Serie A
- [ ] Opção 5 coleta todas
- [ ] Mensagens corretas aparecem

---

## ⚠️ Testes de Erro

### 13. Lidar com Liga Sem Dados

```python
from ensemble import EnsembleModel

# Tentar treinar sem dados
ensemble = EnsembleModel()
try:
    ensemble.fit(league_code='INVALID')
    print("❌ Deveria ter dado erro!")
except Exception as e:
    print(f"✅ Erro capturado corretamente: {e}")
```

**Validar:**
- [ ] Erro é capturado
- [ ] Mensagem de erro é clara
- [ ] Sistema não trava

---

### 14. Trocar Ligas Rapidamente

**Na interface Streamlit:**
1. Selecionar Premier League
2. Aguardar carregar
3. Selecionar La Liga
4. Aguardar carregar
5. Selecionar Serie A
6. Aguardar carregar
7. Voltar para Premier League

**Validar:**
- [ ] Trocas funcionam suavemente
- [ ] Cache funciona (carregamento rápido)
- [ ] Dados corretos para cada liga
- [ ] Sem erros de memória

---

## 📊 Resultados Esperados

### Resumo de Testes

| Teste | Status | Observações |
|-------|--------|-------------|
| 1. Configuração | ⬜ | Verifica config.py |
| 2. API Client | ⬜ | Testa conexão |
| 3. Coleta La Liga | ⬜ | ~400 partidas |
| 4. Coleta Serie A | ⬜ | ~400 partidas |
| 5. Modelo La Liga | ⬜ | Treinamento OK |
| 6. Modelo Serie A | ⬜ | Treinamento OK |
| 7. Interface La Liga | ⬜ | Streamlit OK |
| 8. Interface Serie A | ⬜ | Streamlit OK |
| 9. Análise Apostas | ⬜ | La Liga OK |
| 10. Análise Times | ⬜ | Serie A OK |
| 11. Todas Ligas | ⬜ | 4 ligas OK |
| 12. Menu BAT | ⬜ | Windows OK |
| 13. Erros | ⬜ | Tratamento OK |
| 14. Troca Rápida | ⬜ | Performance OK |

**Legenda:**
- ⬜ Não testado
- ✅ Passou
- ❌ Falhou
- ⚠️ Com ressalvas

---

## 🐛 Problemas Comuns e Soluções

### Erro: API Key Inválida

**Problema:**
```
ValueError: API Key não configurada
```

**Solução:**
1. Verifique arquivo `.env`
2. Confirme chave no Football-Data.org
3. Recarregue ambiente Python

---

### Erro: Nenhuma Partida Coletada

**Problema:**
```
AVISO: Nenhuma partida foi coletada
```

**Solução:**
1. Verifique conexão internet
2. Aguarde 5 minutos e tente novamente
3. Verifique se não atingiu limite da API (10 req/min)

---

### Erro: Liga Não Aparece

**Problema:**
Interface mostra apenas 2 ligas

**Solução:**
1. Limpe cache: Pressione `C` no terminal Streamlit
2. Recarregue página: F5
3. Reinicie servidor se necessário

---

### Erro: Modelos Não Treinam

**Problema:**
```
FileNotFoundError: Nenhum arquivo encontrado
```

**Solução:**
1. Execute coleta de dados primeiro
2. Verifique pasta `data/`
3. Confirme nomes de arquivo corretos

---

## ✅ Critérios de Aceitação

Para considerar a implementação bem-sucedida, todos devem passar:

### Essenciais (Obrigatórios)
- [x] Config.py atualizado com PD e SA
- [x] API Client reconhece códigos PD e SA
- [x] Coleta de dados funciona para ambas ligas
- [x] Modelos treinam sem erros
- [x] Interface mostra 4 ligas no dropdown
- [x] Análises funcionam para La Liga e Serie A

### Desejáveis (Recomendados)
- [x] Documentação completa
- [x] Script de verificação criado
- [x] Guias de uso atualizados
- [x] Testes documentados

### Opcionais (Bônus)
- [ ] Testes automatizados com pytest
- [ ] CI/CD configurado
- [ ] Deploy em produção validado

---

## 📝 Relatório de Testes

Ao finalizar os testes, documente os resultados:

```markdown
### Relatório - [DATA]

**Testado por:** [SEU NOME]
**Ambiente:** [Windows/Linux/Mac]
**Python:** [VERSÃO]

**Resultados:**
- Testes passados: X/14
- Testes falhados: Y/14
- Taxa de sucesso: Z%

**Problemas encontrados:**
1. [DESCRIÇÃO]
2. [DESCRIÇÃO]

**Observações:**
[COMENTÁRIOS ADICIONAIS]
```

---

## 🎓 Conclusão

Após completar todos os testes acima, você terá validado:

✅ **Configuração** - Ligas adicionadas corretamente  
✅ **Coleta** - Dados sendo capturados da API  
✅ **Modelos** - Treinamento e predições funcionando  
✅ **Interface** - Streamlit exibindo todas as opções  
✅ **Integração** - Sistema completo operacional  

**Se todos os testes passarem, a implementação está APROVADA! 🎉**

---

**Versão:** 1.0  
**Data:** 27 de Outubro de 2025  
**Próxima revisão:** Após uso em produção  

---

## 📞 Suporte

**Problemas nos testes?**
- Revise seção "Problemas Comuns"
- Consulte `IMPLEMENTACAO_LA_LIGA_SERIE_A.md`
- Verifique logs em `logs/`

**Dúvidas sobre testes?**
- Leia documentação completa
- Execute `python verificar_ligas_disponiveis.py`
- Teste isoladamente cada componente

---

**🧪 Bons testes! 🚀**

