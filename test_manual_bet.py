"""
Teste manual de registro de aposta
"""

from bankroll_manager import BankrollManager
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("  TESTE MANUAL DE REGISTRO DE APOSTA")
print("="*80 + "\n")

# Inicializa manager
manager = BankrollManager()

# Verifica banca
bankroll = manager.get_bankroll()
print(f"Banca atual: R$ {bankroll['current_value']:.2f}\n")

# Tenta registrar aposta
print("Registrando aposta de teste...")

bet_info = {
    'match_info': 'Arsenal vs Chelsea',
    'home_team': 'Arsenal',
    'away_team': 'Chelsea',
    'match_date': '2025-10-26',
    'market': 'Vitória Casa',
    'odds': 2.20,
    'stake': 1.0,
    'prob_model': 0.55,
    'ev_percent': 5.5,
    'kelly_percent': 2.5,
    'notes': 'Teste manual'
}

try:
    bet_id = manager.add_bet(bet_info)
    print(f"✅ Aposta registrada! ID: {bet_id}\n")
    
    # Verifica novo saldo
    new_bankroll = manager.get_bankroll()
    print(f"Novo saldo: R$ {new_bankroll['current_value']:.2f}")
    
    # Verifica apostas pendentes
    pending = manager.get_pending_bets()
    print(f"\nApostas pendentes: {len(pending)}")
    
    if pending:
        for bet in pending:
            print(f"  - ID {bet['id']}: {bet['match_info']} - R$ {bet['stake']:.2f}")
    
    print("\n✅ TESTE BEM-SUCEDIDO! O sistema está funcionando.")
    print("   O problema está no app Streamlit.\n")
    
except Exception as e:
    print(f"❌ ERRO: {e}\n")
    import traceback
    traceback.print_exc()

print("="*80 + "\n")

