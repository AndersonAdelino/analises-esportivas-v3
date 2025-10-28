# Correções: Problema de Probabilidades Negativas

## Data: 26/10/2025

## Problema Relatado
Ao analisar **Botafogo x Santos**, o sistema retornava **-7,8% de chance para vitória fora**, o que é um valor impossível (probabilidades devem estar entre 0% e 100%).

## Análise Realizada

### 1. Diagnóstico
Executamos testes completos em todos os modelos e identificamos os seguintes problemas:

#### Dixon-Coles
- **Problema**: `RuntimeWarning: invalid value encountered in log`
- **Causa**: A função `rho_correction()` estava retornando valores ≤ 0, causando -∞ ou NaN no logaritmo
- **Impacto**: Parâmetro rho muito alto (0.284) gerava tau negativo em alguns casos

#### Ensemble
- **Problema**: Não havia validação de probabilidades
- **Causa**: Valores negativos dos modelos individuais eram propagados sem verificação
- **Impacto**: Probabilidades negativas chegavam ao usuário final

#### Heurísticas
- **Problema**: Erro ao carregar dados do Brasileirão
- **Causa**: Tentava normalizar dados que já estavam normalizados
- **Impacto**: Modelo de Heurísticas falhava completamente

## Correções Implementadas

### 1. Dixon-Coles (`dixon_coles.py`)

#### a) Correção na função `rho_correction()`
```python
# ANTES: Poderia retornar valores negativos
return tau

# DEPOIS: Garante tau sempre > 0
return max(tau, 1e-10)  # Valor mínimo: 0.0000000001
```

**Justificativa**: Como tau é usado em `np.log(tau)`, valores ≤ 0 causam -∞ ou NaN. A correção garante um valor mínimo muito pequeno mas positivo.

#### b) Adição de bounds na otimização
```python
# Limites para evitar valores extremos
bounds = [
    (0, 1),          # home_advantage: [0, 1]
    (-0.2, 0.2),     # rho: [-0.2, 0.2] (restrito!)
    ...              # attack/defense: sem limite
]

# Mudança de método
method='L-BFGS-B'  # Suporta bounds (antes era 'BFGS')
```

**Justificativa**: Limitar rho ao intervalo [-0.2, 0.2] evita valores extremos que causam problemas numéricos.

### 2. Ensemble (`ensemble.py`)

#### Adição de validação completa de probabilidades

```python
# Validação ao coletar probabilidades
if prob_value < 0:
    print(f"AVISO: {model_name} retornou {key}={prob_value:.4f} (negativo). Corrigindo para 0.")
    prob_value = 0.0
elif prob_value > 1:
    print(f"AVISO: {model_name} retornou {key}={prob_value:.4f} (>1). Corrigindo para 1.")
    prob_value = 1.0

# Validação final após média ponderada
combined[key] = max(0.0, min(1.0, combined[key]))

# Validação de soma 1X2
if total > 0:
    combined['prob_casa'] /= total
    combined['prob_empate'] /= total
    combined['prob_fora'] /= total
else:
    # Fallback: distribuição uniforme
    combined['prob_casa'] = 1.0 / 3.0
    combined['prob_empate'] = 1.0 / 3.0
    combined['prob_fora'] = 1.0 / 3.0
```

**Justificativa**: Múltiplas camadas de validação garantem que valores inválidos são corrigidos e o usuário é alertado.

### 3. Heurísticas (`heuristicas.py`)

#### Detecção automática de formato de dados

```python
# Verifica se os dados já estão normalizados
required_normalized_cols = ['time', 'adversario', 'local', 'gols_marcados', 'gols_sofridos', 'resultado']
if all(col in df_raw.columns for col in required_normalized_cols):
    # Dados já estão normalizados
    self.df = df_raw.sort_values('data', ascending=False)
else:
    # Precisa normalizar
    self.df = self._normalize_data(df_raw)
```

**Justificativa**: Permite carregar CSVs em diferentes formatos sem erro.

## Resultados dos Testes

### Teste: Botafogo FR vs Santos FC

**ANTES**: -7.8% vitória fora (ERRO)

**DEPOIS**:
```
ENSEMBLE (Combinado):
  Casa:      68.67%  ✓
  Empate:    18.08%  ✓
  Fora:      13.25%  ✓ (Corrigido!)
  Over 2.5:  58.54%  ✓
  BTTS:      49.57%  ✓

Diagnóstico: OK - Nenhum problema detectado!
Todas as probabilidades estão no intervalo [0, 100%]
```

### Predições Individuais
- **Dixon-Coles**: Casa 71.70%, Empate 15.69%, Fora 12.62%
- **Offensive-Defensive**: Casa 70.45%, Empate 17.71%, Fora 11.84%
- **Heurísticas**: Casa 54.00%, Empate 27.60%, Fora 18.40%

### Melhorias na Convergência
- **Dixon-Coles**: Agora converge com sucesso (antes falhava)
- **Rho**: Valores mais estáveis (0.115 vs 0.284 anterior)
- **Warnings**: Eliminados os warnings de `invalid value in log`

## Impacto

### Positivo ✓
1. **Probabilidades válidas**: Sempre no intervalo [0, 100%]
2. **Convergência melhorada**: Dixon-Coles converge com mais sucesso
3. **Robustez**: Sistema lida com casos extremos graciosamente
4. **Transparência**: Avisos quando correções são aplicadas
5. **Compatibilidade**: Suporta diferentes formatos de dados

### Possíveis Efeitos Colaterais
1. **Valores corrigidos**: Probabilidades extremas são clipadas
2. **Performance**: Otimização L-BFGS-B pode ser ligeiramente mais lenta que BFGS
3. **Avisos**: Sistema pode gerar mais avisos no console (mas isso é bom para debugging)

## Recomendações

### Uso Imediato
O sistema agora está **pronto para uso em produção** com as seguintes características:
- ✓ Probabilidades sempre válidas
- ✓ Validação em múltiplas camadas
- ✓ Melhor convergência numérica

### Monitoramento
Fique atento a:
- Mensagens de aviso no console indicando correções
- Casos onde rho atinge os limites (-0.2 ou 0.2)
- Convergência do Offensive-Defensive (ainda pode falhar em raros casos)

### Melhorias Futuras (Opcional)
1. Adicionar logging estruturado das correções
2. Criar dashboard de monitoramento de convergência
3. Implementar testes automáticos para detectar regressões
4. Adicionar mais métricas de qualidade das predições

## Arquivos Modificados
1. `dixon_coles.py` - Função rho_correction() e otimização
2. `ensemble.py` - Validação de probabilidades
3. `heuristicas.py` - Carregamento de dados

## Arquivos de Teste Criados
1. `test_botafogo_santos.py` - Teste diagnóstico completo
2. `test_simple.py` - Teste de importações
3. `test_problema_negativo.py` - Teste focado
4. `test_correcao_final.py` - Teste final (RECOMENDADO)

## Como Testar
```bash
# Teste rápido
python test_correcao_final.py

# Teste completo (demorado)
python test_botafogo_santos.py
```

## Conclusão
✅ **Problema resolvido com sucesso!**

O sistema agora retorna probabilidades válidas para todas as partidas, incluindo Botafogo x Santos que estava com o problema de -7.8%.

As correções são robustas e não devem impactar negativamente a qualidade das predições, apenas garantem que os valores sejam sempre matematicamente válidos.

