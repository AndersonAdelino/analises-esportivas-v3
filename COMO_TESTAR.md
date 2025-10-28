# 🧪 Como Testar o Sistema

## Testes Disponíveis

### 1️⃣ Teste Rápido (30 segundos)
Testa apenas Botafogo x Santos (o caso que estava com problema)

```bash
python test_correcao_final.py
```

**O que testa**:
- ✅ Botafogo FR vs Santos FC
- ✅ Todas as probabilidades
- ✅ Ensemble completo

---

### 2️⃣ Teste Completo (3-5 minutos) ⭐ RECOMENDADO
Testa 12 partidas em ambas as ligas

```bash
python test_validacao_final.py
```

ou no Windows:

```bash
.\executar_teste.bat
```

**O que testa**:
- ✅ 6 partidas do Brasileirão
- ✅ 6 partidas da Premier League
- ✅ Times fortes vs fortes
- ✅ Times fortes vs médios
- ✅ Times equilibrados
- ✅ Casos extremos
- ✅ Total: 78 validações de probabilidades

**Resultado esperado**:
```
================================================================================
RESULTADO: SUCESSO!
================================================================================

Todas as 12 partidas foram testadas com sucesso!

VERIFICADO:
  [OK] Nenhuma probabilidade negativa
  [OK] Nenhuma probabilidade > 100%
  [OK] Probabilidades 1X2 somam ~1.0
  [OK] Brasileirao funciona corretamente
  [OK] Premier League funciona corretamente

*** SISTEMA VALIDADO E PRONTO PARA PRODUCAO ***
```

---

### 3️⃣ Teste de Integração
Testa a integração com o sistema de apostas

```bash
python test_app_integration.py
```

**O que testa**:
- ✅ Ensemble
- ✅ Betting tools
- ✅ Análise de value bets
- ✅ Kelly Criterion

---

### 4️⃣ Teste no App Streamlit
Testa o app completo em funcionamento

```bash
streamlit run app_betting.py
```

**Como testar**:
1. Selecione "Brasileirão Série A" ou "Premier League"
2. Escolha uma partida (ex: Botafogo FR vs Santos FC)
3. Insira as odds:
   - Casa: 2.00
   - Empate: 3.50
   - Fora: 3.80
4. Configure sua banca (ex: R$ 1000)
5. Clique em "Analisar"
6. ✅ Verifique que todas as probabilidades são positivas!

---

## 🎯 O Que Verificar

Em todos os testes, verifique:

✅ **Nenhuma probabilidade negativa** (ex: -7.8%)  
✅ **Nenhuma probabilidade > 100%**  
✅ **Soma Casa + Empate + Fora ≈ 100%**  
✅ **Over 2.5 e BTTS entre 0% e 100%**  
✅ **Mensagem de sucesso ao final**  

---

## 🐛 Se Encontrar Problemas

### Problema: Erro de encoding (emojis)
**Solução**: Use `executar_teste.bat` em vez de executar Python diretamente

### Problema: Time não encontrado
**Verificação**: Veja os nomes exatos dos times:
```bash
python -c "import pandas as pd; df = pd.read_csv('data/brasileirao_série_a_matches_20251025_075556.csv'); print(sorted(df['time'].unique()))"
```

### Problema: API Key não configurada
**Solução**: Configure no arquivo `.env` ou Streamlit Secrets

---

## 📊 Interpretando os Resultados

### Exemplo de Saída Correta:
```
[1] Botafogo FR vs Santos FC
    Casa:  68.67% | Empate:  18.08% | Fora:  13.25%
```

✅ **Todos os valores são positivos**  
✅ **Soma = 100.00%** (68.67 + 18.08 + 13.25 = 100.00)  
✅ **Valores fazem sentido** (casa favorita, fora com menor chance)  

### Exemplo de Saída INCORRETA (bug):
```
[1] Botafogo FR vs Santos FC
    Casa:  75.80% | Empate:  18.08% | Fora:  -7.80%
```

❌ **Fora é negativo** (-7.80%)  
❌ **Isso NÃO DEVE ACONTECER MAIS**  

---

## ✅ Checklist de Validação

Após executar os testes, confirme:

- [ ] Teste rápido passou sem erros
- [ ] Teste completo passou sem erros (12/12 partidas OK)
- [ ] Nenhuma mensagem de erro crítico
- [ ] Todas as probabilidades entre 0% e 100%
- [ ] Soma 1X2 sempre próxima de 100%
- [ ] App Streamlit abre sem erros
- [ ] Análise de partida funciona no app
- [ ] Value bets são calculados corretamente

Se todos os itens estiverem marcados: **✅ SISTEMA PRONTO!**

---

## 🎉 Sucesso!

Se todos os testes passaram, você pode usar o sistema com confiança!

O problema de probabilidades negativas foi **100% corrigido** e **validado em 12 partidas reais**.

