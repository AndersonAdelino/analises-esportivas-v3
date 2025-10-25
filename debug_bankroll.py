"""
Script de Debug para verificar o banco de dados
"""

from bankroll_manager import BankrollManager
import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("\n" + "="*80)
print("  DEBUG DO SISTEMA DE BANCA")
print("="*80 + "\n")

# Verifica arquivo do banco
db_path = "data/bankroll.db"
print(f"1. Verificando arquivo do banco: {db_path}")
print(f"   Existe? {os.path.exists(db_path)}")

if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"   Tamanho: {size} bytes")

print("\n" + "-"*80 + "\n")

# Inicializa manager
print("2. Inicializando BankrollManager...")
manager = BankrollManager()
print("   ✅ Manager inicializado")

print("\n" + "-"*80 + "\n")

# Verifica banca
print("3. Verificando banca configurada...")
bankroll = manager.get_bankroll()

if bankroll:
    print("   ✅ Banca configurada!")
    print(f"   - Valor inicial: R$ {bankroll['initial_value']:.2f}")
    print(f"   - Saldo atual: R$ {bankroll['current_value']:.2f}")
    print(f"   - Lucro/Prejuízo: R$ {bankroll['profit']:+.2f}")
    print(f"   - ROI: {bankroll['roi']:+.2f}%")
else:
    print("   ❌ Banca NÃO configurada!")
    print("   Configure em 'Gerenciamento de Banca' no app")

print("\n" + "-"*80 + "\n")

# Verifica apostas pendentes
print("4. Verificando apostas pendentes...")
pending = manager.get_pending_bets()
print(f"   Total: {len(pending)} apostas pendentes")

if pending:
    print("\n   Apostas encontradas:")
    for bet in pending:
        print(f"   - ID {bet['id']}: {bet['match_info']} - {bet['market']}")
        print(f"     Stake: R$ {bet['stake']:.2f} @ {bet['odds']:.2f}")
else:
    print("   📭 Nenhuma aposta pendente")

print("\n" + "-"*80 + "\n")

# Verifica estatísticas
print("5. Estatísticas gerais...")
stats = manager.get_statistics()
print(f"   Total de apostas: {stats['total_bets']}")
print(f"   Ganhas: {stats['wins']}")
print(f"   Perdidas: {stats['losses']}")
print(f"   Pendentes: {stats['pending']}")
print(f"   Total apostado: R$ {stats['total_staked']:.2f}")

print("\n" + "-"*80 + "\n")

# Teste de registro (opcional)
print("6. Teste de registro de aposta...")
if bankroll and bankroll['current_value'] >= 1.0:
    resposta = input("   Deseja testar registro de aposta? (s/n): ")
    
    if resposta.lower() == 's':
        try:
            test_bet = {
                'match_info': 'TESTE: Time A vs Time B',
                'home_team': 'Time A',
                'away_team': 'Time B',
                'match_date': '2025-10-26',
                'market': 'TESTE',
                'odds': 2.00,
                'stake': 1.0,
                'prob_model': 0.55,
                'ev_percent': 5.0,
                'kelly_percent': 2.0,
                'notes': 'Aposta de teste'
            }
            
            bet_id = manager.add_bet(test_bet)
            print(f"   ✅ Aposta de teste registrada! ID: {bet_id}")
            
            # Verifica se aparece
            pending = manager.get_pending_bets()
            print(f"   ✅ Apostas pendentes agora: {len(pending)}")
            
            # Pergunta se quer deletar
            deletar = input("   Deletar aposta de teste? (s/n): ")
            if deletar.lower() == 's':
                manager.delete_bet(bet_id)
                print("   ✅ Aposta de teste deletada!")
        except Exception as e:
            print(f"   ❌ Erro ao testar: {e}")
            import traceback
            traceback.print_exc()
else:
    print("   ⚠️ Banca não configurada ou saldo insuficiente para teste")

print("\n" + "="*80)
print("  DEBUG CONCLUÍDO")
print("="*80 + "\n")

