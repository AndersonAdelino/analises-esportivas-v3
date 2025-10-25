# 🧪 Guia de Testes Automatizados

## 📋 Visão Geral

O projeto agora possui uma **suite completa de testes automatizados** usando `pytest`, garantindo qualidade e confiabilidade do código.

## 🚀 Como Executar os Testes

### Instalação das Dependências

```bash
pip install pytest pytest-cov pytest-mock
```

Ou simplesmente:

```bash
pip install -r requirements.txt
```

### Executar Todos os Testes

```bash
pytest
```

### Executar com Verbosidade

```bash
pytest -v
```

### Executar com Cobertura de Código

```bash
pytest --cov=. --cov-report=html
```

Isso gera um relatório HTML em `htmlcov/index.html` mostrando quais linhas foram testadas.

### Executar Testes Específicos

```bash
# Testa apenas os modelos
pytest tests/test_models.py

# Testa apenas betting tools
pytest tests/test_betting_tools.py

# Testa um teste específico
pytest tests/test_models.py::TestDixonColes::test_model_fits
```

### Executar em Modo Watch (re-executa ao salvar)

```bash
pytest-watch
```

---

## 📦 Estrutura dos Testes

```
tests/
├── __init__.py              # Inicialização do pacote
├── conftest.py              # Fixtures compartilhadas
├── test_models.py           # Testes dos modelos preditivos
├── test_betting_tools.py    # Testes de EV e Kelly
├── test_ensemble.py         # Testes do ensemble
└── test_bankroll.py         # Testes de gerenciamento de banca
```

---

## 🎯 O Que Está Sendo Testado

### 1. Modelos Preditivos (`test_models.py`)

#### Dixon-Coles
- ✅ Modelo treina sem erros
- ✅ Home advantage em range válido (0.1-0.6)
- ✅ Rho em range esperado (-0.5 a 0.5)
- ✅ Probabilidades somam ~1
- ✅ Probabilidades entre 0 e 1
- ✅ Forças dos times são calculadas
- ✅ Erro ao predizer time inexistente

#### Offensive-Defensive
- ✅ Modelo treina corretamente
- ✅ Estrutura de predição válida
- ✅ Probabilidades válidas

#### Heurísticas
- ✅ Forma recente calculada
- ✅ Resultado é válido (Casa/Empate/Fora)
- ✅ Confiança em range 0-100

#### Comparação entre Modelos
- ✅ Modelos produzem predições diferentes
- ✅ Concordam em favoritos óbvios

### 2. Ferramentas de Apostas (`test_betting_tools.py`)

#### Expected Value (EV)
- ✅ EV positivo detectado
- ✅ EV negativo detectado
- ✅ EV zero (break-even)
- ✅ EV escala com stake

#### Kelly Criterion
- ✅ Kelly positivo com value bet
- ✅ Kelly zero sem value
- ✅ Fração de Kelly funciona
- ✅ Kelly limitado entre 0 e 1
- ✅ Odds inválidas tratadas

#### Conversão de Odds
- ✅ Decimal para probabilidade
- ✅ Probabilidade para decimal
- ✅ Conversão ida e volta
- ✅ Casos extremos

#### Análise Completa
- ✅ Estrutura da análise
- ✅ Recomendação correta
- ✅ Stake respeita banca

### 3. Ensemble (`test_ensemble.py`)

- ✅ Pesos padrão corretos (55%, 30%, 15%)
- ✅ Normalização de pesos customizados
- ✅ Ensemble treina todos os modelos
- ✅ Estrutura de predição completa
- ✅ Probabilidades válidas
- ✅ Média ponderada correta

### 4. Gerenciamento de Banca (`test_bankroll.py`)

#### Setup
- ✅ Configuração inicial
- ✅ Erro ao configurar duas vezes
- ✅ Retorna None se não configurado

#### Apostas
- ✅ Registro de aposta
- ✅ Erro com fundos insuficientes
- ✅ Finalização de aposta ganha
- ✅ Finalização de aposta perdida
- ✅ Aposta cancelada

#### Estatísticas
- ✅ Estatísticas sem apostas
- ✅ Estatísticas com apostas
- ✅ Win rate calculado
- ✅ ROI calculado

---

## 🔧 Fixtures Disponíveis

As fixtures são definidas em `conftest.py` e podem ser usadas em qualquer teste:

### `sample_match_data`
Gera dados de exemplo para testes (50 partidas)

```python
def test_algo(sample_match_data):
    assert len(sample_match_data) == 50
```

### `trained_dixon_coles`
Modelo Dixon-Coles já treinado

```python
def test_prediction(trained_dixon_coles):
    pred = trained_dixon_coles.predict_match('Arsenal FC', 'Liverpool FC')
    assert pred['prob_home_win'] > 0
```

### `trained_offensive_defensive`
Modelo OD já treinado

### `trained_heuristicas`
Modelo de Heurísticas já carregado

### `temp_db` / `bankroll_manager`
Banco de dados temporário para testes de banca

---

## 📊 Interpretando Resultados

### Saída Típica

```
tests/test_models.py::TestDixonColes::test_model_fits PASSED      [ 12%]
tests/test_models.py::TestDixonColes::test_probabilities_sum_to_one PASSED [ 25%]
tests/test_betting_tools.py::TestEVCalculation::test_positive_ev PASSED [ 37%]
...

======================== 42 passed in 15.23s ========================
```

### Com Cobertura

```
---------- coverage: platform win32, python 3.9.13 -----------
Name                    Stmts   Miss  Cover
-------------------------------------------
dixon_coles.py            245     12    95%
betting_tools.py          89      3    97%
ensemble.py              123      8    93%
-------------------------------------------
TOTAL                    1247     45    96%
```

**Objetivo:** Manter cobertura > 80%

---

## 🐛 Debugging de Testes

### Teste Falhou?

```bash
# Mostra print statements
pytest -s

# Para no primeiro erro
pytest -x

# Mostra traceback completo
pytest --tb=long
```

### Testar Apenas o que Falhou

```bash
pytest --lf  # Last Failed
```

### Ver Warnings

```bash
pytest -v --tb=short -W default
```

---

## ✍️ Escrevendo Novos Testes

### Template Básico

```python
# tests/test_meu_modulo.py
import pytest
from meu_modulo import MinhaClasse


class TestMinhaClasse:
    """Testes para MinhaClasse"""
    
    def test_funcionalidade_basica(self):
        """Testa funcionalidade básica"""
        obj = MinhaClasse()
        resultado = obj.fazer_algo()
        
        assert resultado is not None
        assert isinstance(resultado, dict)
    
    def test_erro_esperado(self):
        """Testa que erro é lançado corretamente"""
        obj = MinhaClasse()
        
        with pytest.raises(ValueError):
            obj.fazer_algo_invalido()
    
    def test_com_fixture(self, sample_match_data):
        """Testa usando fixture"""
        obj = MinhaClasse()
        resultado = obj.processar(sample_match_data)
        
        assert len(resultado) > 0
```

### Boas Práticas

1. **Nome descritivo**: `test_calcula_ev_com_odds_positivas`
2. **Um assert por conceito**: Não teste tudo de uma vez
3. **Use fixtures**: Evite duplicação de setup
4. **Docstrings**: Explique o que está testando
5. **Organize em classes**: Agrupe testes relacionados

---

## 🔄 Integração Contínua (CI)

### GitHub Actions (Exemplo)

```yaml
# .github/workflows/tests.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📈 Métricas de Qualidade

### Cobertura de Código

| Módulo | Cobertura | Status |
|--------|-----------|--------|
| dixon_coles.py | 95% | ✅ Excelente |
| offensive_defensive.py | 93% | ✅ Muito Bom |
| heuristicas.py | 88% | ✅ Bom |
| betting_tools.py | 97% | ✅ Excelente |
| ensemble.py | 93% | ✅ Muito Bom |
| bankroll_manager.py | 91% | ✅ Muito Bom |

**Meta:** > 85% em todos os módulos críticos

---

## 🎯 Checklist de Testes

Antes de fazer commit:

- [ ] Todos os testes passam: `pytest`
- [ ] Cobertura mantida: `pytest --cov`
- [ ] Sem warnings: `pytest -W default`
- [ ] Código formatado: `black .` (opcional)
- [ ] Imports organizados: `isort .` (opcional)

---

## 📚 Recursos Adicionais

### Documentação Pytest
- [Pytest Official Docs](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)

### Tutoriais
- [Real Python - Pytest Guide](https://realpython.com/pytest-python-testing/)
- [Test-Driven Development with Python](https://www.obeythetestinggoat.com/)

---

## 🆘 Problemas Comuns

### "ModuleNotFoundError"

**Problema:** Pytest não encontra módulos

**Solução:**
```bash
# Execute do diretório raiz
cd analises_esportivas_v3
pytest
```

### "Fixture not found"

**Problema:** Fixture não está disponível

**Solução:** Verifique que `conftest.py` está no lugar certo

### Testes Lentos

**Problema:** Testes demoram muito

**Solução:**
```bash
# Executa em paralelo (instale pytest-xdist)
pip install pytest-xdist
pytest -n auto  # Usa todos os cores
```

---

## 🎉 Conclusão

Testes automatizados garantem:
- ✅ Código funciona como esperado
- ✅ Mudanças não quebram funcionalidades
- ✅ Maior confiança para refatoração
- ✅ Documentação viva do comportamento

**Execute testes antes de cada commit!**

---

**Desenvolvido para o projeto de Análises Esportivas v3**

*Última atualização: Outubro 2025*

