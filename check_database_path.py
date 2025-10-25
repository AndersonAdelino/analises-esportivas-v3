"""
Verifica qual banco está sendo usado
"""

from bankroll_manager import BankrollManager
import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("  VERIFICAÇÃO DE BANCO DE DADOS")
print("="*80 + "\n")

# Inicializa com path padrão
manager = BankrollManager()

print(f"Caminho do banco: {manager.db_path}")
print(f"Caminho absoluto: {os.path.abspath(manager.db_path)}")
print(f"Arquivo existe: {os.path.exists(manager.db_path)}")

print("\n" + "-"*80 + "\n")

# Verifica conteúdo de ambos os bancos
print("CONTEÚDO DO BANKROLL.DB:")
manager1 = BankrollManager("data/bankroll.db")
bankroll1 = manager1.get_bankroll()
pending1 = manager1.get_pending_bets()

if bankroll1:
    print(f"  Banca: R$ {bankroll1['current_value']:.2f}")
    print(f"  Apostas pendentes: {len(pending1)}")
    if pending1:
        for bet in pending1:
            print(f"    - ID {bet['id']}: {bet['match_info']}")
else:
    print("  ❌ Não configurado")

print("\n" + "-"*80 + "\n")

print("CONTEÚDO DO BANKROLL_TEST_DEMO.DB:")
manager2 = BankrollManager("data/bankroll_test_demo.db")
bankroll2 = manager2.get_bankroll()
pending2 = manager2.get_pending_bets()

if bankroll2:
    print(f"  Banca: R$ {bankroll2['current_value']:.2f}")
    print(f"  Apostas pendentes: {len(pending2)}")
    if pending2:
        for bet in pending2:
            print(f"    - ID {bet['id']}: {bet['match_info']}")
else:
    print("  ❌ Não configurado")

print("\n" + "="*80 + "\n")

