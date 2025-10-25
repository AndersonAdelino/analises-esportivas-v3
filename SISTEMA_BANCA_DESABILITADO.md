# 💰 Sistema de Gerenciamento de Banca (Temporariamente Desabilitado)

## 📋 Status

O sistema de gerenciamento de banca foi **removido do app principal** para permitir validação do projeto base.

## 📁 Arquivos Mantidos

Os seguintes arquivos **foram preservados** para uso futuro:

### ✅ Módulo Principal
- `bankroll_manager.py` - Gerenciador completo de banca com SQLite
- `data/bankroll.db` - Banco de dados com apostas registradas

### ✅ Scripts de Teste
- `test_bankroll_system.py` - Teste completo do sistema
- `test_manual_bet.py` - Teste de registro manual
- `test_final_bet.py` - Teste que simula fluxo do Streamlit
- `debug_bankroll.py` - Script de diagnóstico
- `check_database_path.py` - Verificador de banco
- `TESTAR_GERENCIAMENTO_BANCA.bat` - Executável Windows

### ✅ Documentação
- `docs/GUIA_GERENCIAMENTO_BANCA.md` - Guia completo
- `LEIA-ME_GERENCIAMENTO_BANCA.txt` - Guia rápido

## 🔧 O Que Foi Removido do `app_betting.py`

1. ❌ **Import:** `from bankroll_manager import BankrollManager`
2. ❌ **Funções removidas:**
   - `setup_bankroll_manager()`
   - `display_bankroll_setup()`
   - `display_bankroll_info()`
   - `display_pending_bets()`
   - `display_bet_history()`
   - `display_statistics()`
   - `display_bankroll_evolution()`

3. ❌ **UI removida:**
   - Aba "💰 Gerenciamento de Banca"
   - Sidebar com saldo da banca
   - Botões "APOSTAR" nos value bets
   - Feedback de apostas registradas

4. ✅ **Restaurado:**
   - `display_bankroll_input()` simples (entrada manual)
   - 2 abas apenas: "Análise de Apostas" e "Análise de Times"
   - Recomendações sem botões de ação

## 🚀 Como Reativar o Sistema

### Passo 1: Restaurar Import

```python
# No topo do app_betting.py, adicionar:
from bankroll_manager import BankrollManager
```

### Passo 2: Adicionar as Funções

Copie as funções do backup ou do commit anterior:
- `setup_bankroll_manager()`
- `display_bankroll_setup()`  
- `display_bankroll_info()`
- `display_pending_bets()`
- `display_bet_history()`
- `display_statistics()`
- `display_bankroll_evolution()`

### Passo 3: Restaurar UI

1. **Sidebar:**
```python
# Adicionar na sidebar
st.header("💰 Minha Banca")
manager_sidebar = setup_bankroll_manager()
bankroll_sidebar = manager_sidebar.get_bankroll()
# ... resto do código
```

2. **Abas:**
```python
# Mudar de 2 para 3 abas
tab1, tab2, tab3 = st.tabs([
    "🎯 Análise de Apostas", 
    "📊 Análise de Times", 
    "💰 Gerenciamento de Banca"  # Nova aba
])
```

3. **Botões APOSTAR:**
```python
# Dentro dos value bets, adicionar:
if st.button(f"💰 APOSTAR R$ {stake:.2f}"):
    manager = setup_bankroll_manager()
    bet_id = manager.add_bet(bet_info)
    st.success(f"✅ Aposta registrada! ID: {bet_id}")
    st.rerun()
```

## 🧪 Testar Sistema (Sem App)

Mesmo com o sistema desabilitado no app, você pode testá-lo diretamente:

```bash
# Teste completo
python test_bankroll_system.py

# Teste manual
python test_manual_bet.py

# Debug
python debug_bankroll.py

# Verificar banco
python check_database_path.py
```

## 📊 Funcionalidades do Sistema (Quando Reativado)

- ✅ Configurar banca inicial
- ✅ Registrar apostas com 1 clique
- ✅ Dedução automática do saldo
- ✅ Apostas pendentes
- ✅ Finalizar apostas (Ganhou/Perdeu/Cancelou)
- ✅ Histórico completo
- ✅ Estatísticas: Win Rate, ROI, Lucro Total
- ✅ Gráfico de evolução da banca
- ✅ Persistência em SQLite

## 💾 Dados Preservados

O banco de dados `data/bankroll.db` contém:
- Configuração da banca: R$ 20,00 inicial
- 1 aposta pendente: Manchester United vs Liverpool
- Histórico de transações

**Dados não serão perdidos!** Apenas a interface foi removida.

## 🎯 Recomendação

**Quando reativar:**
1. Validar o projeto base primeiro
2. Garantir que todos os modelos funcionam
3. Testar o sistema de banca isoladamente
4. Integrar gradualmente ao app
5. Fazer testes completos

## 📞 Suporte

Se precisar de ajuda para reativar:
1. Consulte: `docs/GUIA_GERENCIAMENTO_BANCA.md`
2. Execute: `python test_bankroll_system.py`
3. Verifique commits anteriores no git

---

**Versão do App:** Sem gerenciamento de banca  
**Data:** Outubro 2025  
**Status:** Funcional sem persistência de apostas

