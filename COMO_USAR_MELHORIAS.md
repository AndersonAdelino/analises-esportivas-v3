# 🎯 Como Usar as Melhorias Críticas

## ⚡ Guia Rápido de 5 Minutos

### 1️⃣ Instalar Dependências de Teste (1 min)

**Windows:**
```bash
INSTALAR_TESTES.bat
```

**Linux/Mac:**
```bash
pip install pytest pytest-cov pytest-mock
```

### 2️⃣ Executar Testes (2 min)

**Windows:**
```bash
EXECUTAR_TESTES.bat
```

**Linux/Mac:**
```bash
pytest -v
```

**Resultado esperado:**
```
======================== 42 passed in 15.23s ========================
```

### 3️⃣ Ver Cobertura de Código (1 min)

```bash
pytest --cov=. --cov-report=html
```

Abra `htmlcov/index.html` no navegador para ver relatório visual.

### 4️⃣ Validar Modelos (5-10 min)

**Windows:**
```bash
VALIDAR_MODELOS.bat
```

**Linux/Mac:**
```bash
python validation.py
```

**Resultado:**
- Métricas de cada modelo (Brier Score, Log Loss, ROI)
- Ranking comparativo
- Arquivos salvos em `data/validation/`

### 5️⃣ Verificar Logs (30 seg)

```bash
# Ver último log
cat logs/app_20251025.log

# Windows
type logs\app_20251025.log
```

---

## 📚 Documentação Detalhada

| O Que | Onde |
|-------|------|
| **Como escrever/executar testes** | [docs/GUIA_TESTES.md](docs/GUIA_TESTES.md) |
| **Como validar modelos** | [docs/GUIA_VALIDACAO.md](docs/GUIA_VALIDACAO.md) |
| **Resumo das melhorias** | [MELHORIAS_CRITICAS.md](MELHORIAS_CRITICAS.md) |
| **README principal** | [README.md](README.md) |

---

## 🎯 Casos de Uso

### Antes de Fazer Commit

```bash
# 1. Execute os testes
pytest

# 2. Verifique cobertura
pytest --cov

# 3. Se tudo OK, commit!
git add .
git commit -m "Sua mensagem"
```

### Depois de Coletar Novos Dados

```bash
# 1. Colete dados
python get_team_matches.py

# 2. Re-valide modelos
python validation.py

# 3. Verifique se performance se mantém
cat data/validation/dixon_coles_validation.json
```

### Debugging de Problemas

```bash
# 1. Execute testes para isolar o problema
pytest tests/test_models.py -v

# 2. Verifique logs
tail -f logs/app_20251025.log

# 3. Use logging no código
python seu_script.py  # Logs automáticos
```

### Adicionar Nova Funcionalidade

```bash
# 1. Escreva o teste primeiro (TDD)
# tests/test_nova_funcionalidade.py

# 2. Implemente a funcionalidade
# nova_funcionalidade.py

# 3. Teste
pytest tests/test_nova_funcionalidade.py

# 4. Valide impacto nos modelos
python validation.py
```

---

## 🚀 Workflow Recomendado

### Desenvolvimento Diário

```
┌─────────────────┐
│ Escrever Código │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Executar Testes │◄──── pytest
└────────┬────────┘
         │
         ▼
    ┌─────────┐
    │ Passou? │
    └────┬────┘
         │
    ┌────┴────┐
    │   SIM   │────► Commit
    │         │
    │   NÃO   │────► Fix & Repeat
    └─────────┘
```

### Validação Semanal

```
Segunda:
  ├─ Coletar novos dados (get_team_matches.py)
  └─ Atualizar base

Terça:
  ├─ Validar modelos (python validation.py)
  ├─ Verificar métricas (ROI, Brier, etc)
  └─ Ajustar se necessário

Quarta-Sexta:
  ├─ Análise de jogos
  └─ Value betting

Sábado:
  └─ Review da semana (logs, estatísticas)
```

---

## 🔧 Comandos Úteis

### Testes

```bash
# Todos os testes
pytest

# Verbose (detalhado)
pytest -v

# Apenas testes rápidos
pytest -m "not slow"

# Com cobertura
pytest --cov=. --cov-report=html

# Parar no primeiro erro
pytest -x

# Re-executar últimos falhados
pytest --lf

# Mostrar prints
pytest -s
```

### Validação

```bash
# Validação completa
python validation.py

# Apenas Dixon-Coles (edite validation.py)
# Ou use programaticamente:
python -c "from validation import *; # seu código"
```

### Logging

```bash
# Ver logs em tempo real
tail -f logs/app_20251025.log

# Buscar erros
grep "ERROR" logs/app_20251025.log

# Últimas 50 linhas
tail -n 50 logs/app_20251025.log
```

---

## 📊 Métricas a Monitorar

### Testes

| Métrica | Meta | Como Ver |
|---------|------|----------|
| **Testes passando** | 100% | `pytest` |
| **Cobertura** | > 85% | `pytest --cov` |
| **Tempo de execução** | < 30s | `pytest --durations=10` |

### Validação

| Métrica | Meta | Onde Ver |
|---------|------|----------|
| **Brier Score** | < 0.20 | `data/validation/*.json` |
| **Log Loss** | < 1.0 | `data/validation/*.json` |
| **ROI** | > +5% | `data/validation/*.json` |
| **Win Rate** | 45-55% | `data/validation/*.json` |

### Logs

| O Que | Onde | Frequência |
|-------|------|------------|
| **Erros** | `logs/app_*.log` | Diário |
| **Warnings** | `logs/app_*.log` | Semanal |
| **Performance** | `logs/app_*.log` | Mensal |

---

## ⚠️ Avisos Importantes

### ❌ NÃO Faça

- ❌ Commitar sem executar testes
- ❌ Ignorar testes falhando
- ❌ Commitar arquivos de log
- ❌ Commitar resultados de validação (já no .gitignore)
- ❌ Apostar sem validar modelos primeiro

### ✅ FAÇA

- ✅ Execute `pytest` antes de todo commit
- ✅ Re-valide modelos semanalmente
- ✅ Monitore logs para erros
- ✅ Mantenha cobertura > 85%
- ✅ Documente novos testes

---

## 🎓 Próximos Passos

### Aprendizado

1. Leia [docs/GUIA_TESTES.md](docs/GUIA_TESTES.md) completo
2. Leia [docs/GUIA_VALIDACAO.md](docs/GUIA_VALIDACAO.md) completo
3. Explore os testes em `tests/` para ver exemplos
4. Execute validação e analise os resultados

### Prática

1. Escreva um teste simples para uma função nova
2. Execute validação em diferentes períodos
3. Compare métricas de diferentes modelos
4. Monitore logs durante uso normal

### Expansão

1. Adicione mais testes (aumentar cobertura)
2. Crie validações customizadas
3. Configure CI/CD (GitHub Actions)
4. Implemente alertas baseados em logs

---

## 🆘 Problemas?

### Testes não executam

```bash
# Verifique instalação
pip list | grep pytest

# Reinstale
pip install --force-reinstall pytest pytest-cov
```

### Validação demora muito

```bash
# Use menos splits
# Edite validation.py:
# n_splits=3  # ao invés de 5
```

### Logs muito grandes

```bash
# Limpe logs antigos
rm logs/app_2025*.log

# Ou configure rotação menor em logger_config.py
```

---

## ✅ Checklist Diário

Ao trabalhar no projeto:

- [ ] Executei testes: `pytest`
- [ ] Testes passaram: 100%
- [ ] Cobertura mantida: `pytest --cov`
- [ ] Código está logando adequadamente
- [ ] Sem erros críticos nos logs
- [ ] Modelos validados recentemente (< 1 semana)
- [ ] Documentação atualizada se necessário

---

## 📞 Suporte

### Dúvidas Frequentes

**Q: Quanto tempo leva a validação?**
A: 2-5 minutos com 5 splits, dependendo do tamanho dos dados.

**Q: Preciso validar após cada mudança?**
A: Não. Valide após:
- Mudanças nos modelos
- Coleta de novos dados
- Ajustes em parâmetros
- Semanalmente por rotina

**Q: Os testes falham no meu ambiente**
A: Verifique que está usando Python 3.8+ e que todas as dependências estão instaladas.

### Mais Ajuda

- 📖 Leia a documentação completa
- 🔍 Verifique os logs para detalhes
- 🧪 Execute testes individuais para isolar problemas
- 💬 Consulte exemplos em cada módulo

---

**Criado para facilitar o uso das melhorias críticas! 🚀**

*Última atualização: Outubro 2025*

