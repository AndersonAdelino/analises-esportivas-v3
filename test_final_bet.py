"""
Teste final - simula o que o Streamlit faz
"""

from bankroll_manager import BankrollManager
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("  TESTE FINAL - Simula fluxo do Streamlit")
print("="*80 + "\n")

# ETAPA 1: Usuário vai apostar
print("1. Usuário clica em APOSTAR...")
manager1 = BankrollManager()  # Nova instância (como no app corrigido)

bankroll_antes = manager1.get_bankroll()
print(f"   Saldo antes: R$ {bankroll_antes['current_value']:.2f}")

bet_info = {
    'match_info': 'Manchester United vs Liverpool',
    'home_team': 'Manchester United',
    'away_team': 'Liverpool',
    'match_date': '2025-10-27',
    'market': 'Over 2.5',
    'odds': 1.85,
    'stake': 2.0,
    'prob_model': 0.62,
    'ev_percent': 8.2,
    'kelly_percent': 3.0,
    'notes': 'Teste final'
}

try:
    bet_id = manager1.add_bet(bet_info)
    print(f"   ✅ Aposta registrada! ID: {bet_id}")
    
    bankroll_depois = manager1.get_bankroll()
    print(f"   Saldo depois: R$ {bankroll_depois['current_value']:.2f}")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "-"*80 + "\n")

# ETAPA 2: Streamlit recarrega (st.rerun)
print("2. Streamlit recarrega a página (st.rerun)...")
print("   Criando NOVA instância do manager (não usa cache)...")

manager2 = BankrollManager()  # NOVA instância (importante!)

bankroll_reload = manager2.get_bankroll()
pending_reload = manager2.get_pending_bets()

print(f"   Saldo atual: R$ {bankroll_reload['current_value']:.2f}")
print(f"   Apostas pendentes: {len(pending_reload)}")

print("\n" + "-"*80 + "\n")

# ETAPA 3: Usuário vai ver apostas pendentes
print("3. Usuário abre 'Apostas Pendentes'...")

manager3 = BankrollManager()  # NOVA instância novamente
pending_final = manager3.get_pending_bets()

print(f"   Total encontrado: {len(pending_final)} aposta(s)")

if pending_final:
    print("\n   ✅ APOSTAS ENCONTRADAS:")
    for bet in pending_final:
        print(f"      ID {bet['id']}: {bet['match_info']}")
        print(f"      Mercado: {bet['market']}")
        print(f"      Stake: R$ {bet['stake']:.2f} @ {bet['odds']:.2f}")
        print()
    
    print("   ✅✅✅ TESTE BEM-SUCEDIDO!")
    print("   O sistema está funcionando corretamente!")
else:
    print("   ❌ NENHUMA APOSTA ENCONTRADA!")
    print("   Algo ainda está errado...")

print("\n" + "="*80 + "\n")

