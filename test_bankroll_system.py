"""
Script de Teste do Sistema de Gerenciamento de Banca

Demonstra todas as funcionalidades do sistema.
"""

from bankroll_manager import BankrollManager
import os
import sys

# Configurar encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def print_section(title):
    """Imprime cabeçalho de seção"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")


def test_complete_workflow():
    """Testa workflow completo do sistema"""
    
    # Remove banco de teste se existir
    test_db = "data/bankroll_test_demo.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    print_section("🚀 TESTE DO SISTEMA DE GERENCIAMENTO DE BANCA")
    
    # Inicializa gerenciador
    manager = BankrollManager(test_db)
    print("✅ Gerenciador inicializado")
    
    # 1. CONFIGURAR BANCA
    print_section("1️⃣ CONFIGURANDO BANCA INICIAL")
    
    bankroll = manager.setup_bankroll(1000.0)
    print(f"✅ Banca configurada!")
    print(f"   - Valor inicial: R$ {bankroll['initial_value']:.2f}")
    print(f"   - Saldo atual: R$ {bankroll['current_value']:.2f}")
    print(f"   - Data: {bankroll['created_at']}")
    
    # 2. REGISTRAR APOSTAS
    print_section("2️⃣ REGISTRANDO APOSTAS")
    
    apostas = [
        {
            'match_info': 'Arsenal vs Chelsea',
            'home_team': 'Arsenal',
            'away_team': 'Chelsea',
            'match_date': '2025-10-26',
            'market': '🏠 Vitória Casa',
            'odds': 2.20,
            'stake': 25.0,
            'prob_model': 0.55,
            'ev_percent': 5.5,
            'kelly_percent': 2.5,
            'notes': 'Arsenal em excelente forma'
        },
        {
            'match_info': 'Liverpool vs Manchester City',
            'home_team': 'Liverpool',
            'away_team': 'Manchester City',
            'match_date': '2025-10-27',
            'market': '📈 Over 2.5',
            'odds': 1.85,
            'stake': 30.0,
            'prob_model': 0.62,
            'ev_percent': 8.2,
            'kelly_percent': 3.0,
            'notes': 'Ambos times com ataques fortes'
        },
        {
            'match_info': 'Manchester United vs Tottenham',
            'home_team': 'Manchester United',
            'away_team': 'Tottenham',
            'match_date': '2025-10-28',
            'market': '✅ BTTS Sim',
            'odds': 1.70,
            'stake': 20.0,
            'prob_model': 0.68,
            'ev_percent': 10.4,
            'kelly_percent': 2.0,
            'notes': 'Defesas fracas'
        }
    ]
    
    bet_ids = []
    for aposta in apostas:
        bet_id = manager.add_bet(aposta)
        bet_ids.append(bet_id)
        print(f"✅ Aposta {bet_id} registrada: {aposta['match_info']} - {aposta['market']}")
        print(f"   Stake: R$ {aposta['stake']:.2f} @ {aposta['odds']:.2f}")
    
    bankroll = manager.get_bankroll()
    print(f"\n💰 Saldo após apostas: R$ {bankroll['current_value']:.2f}")
    print(f"   Total apostado: R$ {1000 - bankroll['current_value']:.2f}")
    
    # 3. APOSTAS PENDENTES
    print_section("3️⃣ APOSTAS PENDENTES")
    
    pending = manager.get_pending_bets()
    print(f"📋 Total de apostas pendentes: {len(pending)}\n")
    
    for bet in pending:
        print(f"ID {bet['id']}: {bet['match_info']}")
        print(f"  └─ {bet['market']} @ {bet['odds']:.2f} - R$ {bet['stake']:.2f}")
        print(f"  └─ Prob: {bet['prob_model']*100:.1f}% | EV: {bet['ev_percent']:+.2f}%")
        print()
    
    # 4. FINALIZAR APOSTAS
    print_section("4️⃣ FINALIZANDO APOSTAS")
    
    # Aposta 1: GANHOU
    print(f"🎲 Finalizando aposta {bet_ids[0]} (Arsenal vs Chelsea)...")
    settled = manager.settle_bet(bet_ids[0], 'WON', 'Arsenal ganhou 2-1')
    print(f"   ✅ GANHOU! Lucro: R$ {settled['profit']:+.2f}")
    
    # Aposta 2: PERDEU
    print(f"\n🎲 Finalizando aposta {bet_ids[1]} (Liverpool vs Manchester City)...")
    settled = manager.settle_bet(bet_ids[1], 'LOST', 'Apenas 2 gols no jogo')
    print(f"   ❌ PERDEU. Prejuízo: R$ {settled['profit']:+.2f}")
    
    # Aposta 3: GANHOU
    print(f"\n🎲 Finalizando aposta {bet_ids[2]} (Manchester United vs Tottenham)...")
    settled = manager.settle_bet(bet_ids[2], 'WON', 'Ambos marcaram, terminou 2-2')
    print(f"   ✅ GANHOU! Lucro: R$ {settled['profit']:+.2f}")
    
    bankroll = manager.get_bankroll()
    print(f"\n💰 Saldo final: R$ {bankroll['current_value']:.2f}")
    print(f"   Lucro/Prejuízo: R$ {bankroll['profit']:+.2f}")
    print(f"   ROI: {bankroll['roi']:+.2f}%")
    
    # 5. ESTATÍSTICAS
    print_section("5️⃣ ESTATÍSTICAS FINAIS")
    
    stats = manager.get_statistics()
    
    print(f"📊 RESUMO DE APOSTAS:")
    print(f"   Total de apostas: {stats['total_bets']}")
    print(f"   ✅ Ganhas: {stats['wins']}")
    print(f"   ❌ Perdidas: {stats['losses']}")
    print(f"   ⏳ Pendentes: {stats['pending']}")
    print(f"   Taxa de acerto: {stats['win_rate']:.1f}%")
    
    print(f"\n💰 RESUMO FINANCEIRO:")
    print(f"   Valor inicial: R$ {stats['bankroll']['initial_value']:.2f}")
    print(f"   Saldo atual: R$ {stats['bankroll']['current_value']:.2f}")
    print(f"   Total apostado: R$ {stats['total_staked']:.2f}")
    print(f"   Lucro total: R$ {stats['total_profit']:+.2f}")
    print(f"   ROI: {stats['roi']:+.2f}%")
    print(f"   Stake médio: R$ {stats['avg_stake']:.2f}")
    
    # 6. EVOLUÇÃO DA BANCA
    print_section("6️⃣ EVOLUÇÃO DA BANCA")
    
    evolution = manager.get_bankroll_evolution()
    
    print(f"📈 HISTÓRICO DE TRANSAÇÕES ({len(evolution)} registros):\n")
    
    for _, row in evolution.iterrows():
        print(f"{row['created_at']}")
        print(f"  └─ R$ {row['bankroll_value']:.2f} ({row['change_amount']:+.2f}) - {row['change_reason']}")
    
    # 7. ADICIONAR FUNDOS
    print_section("7️⃣ TESTE: ADICIONAR FUNDOS")
    
    print("💵 Adicionando R$ 500 de depósito...")
    manager.update_bankroll(bankroll['current_value'] + 500, "Depósito adicional")
    
    new_bankroll = manager.get_bankroll()
    print(f"✅ Novo saldo: R$ {new_bankroll['current_value']:.2f}")
    
    # 8. HISTÓRICO COMPLETO
    print_section("8️⃣ HISTÓRICO COMPLETO DE APOSTAS")
    
    history = manager.get_bet_history(100)
    
    print(f"📜 {len(history)} apostas registradas:\n")
    
    for _, bet in history.iterrows():
        status_emoji = {
            'WON': '✅',
            'LOST': '❌',
            'VOID': '⚪',
            'PENDING': '⏳'
        }
        
        emoji = status_emoji.get(bet['status'], '❓')
        print(f"{emoji} {bet['match_info']} - {bet['market']}")
        print(f"   Stake: R$ {bet['stake']:.2f} @ {bet['odds']:.2f}")
        print(f"   Resultado: {bet['status']} - R$ {bet['profit']:+.2f}")
        print()
    
    # RESUMO FINAL
    print_section("✅ TESTE CONCLUÍDO COM SUCESSO!")
    
    final_bankroll = manager.get_bankroll()
    final_stats = manager.get_statistics()
    
    print("📊 RESUMO FINAL:")
    print(f"   💰 Banca inicial: R$ {final_stats['bankroll']['initial_value']:.2f}")
    print(f"   💰 Banca final: R$ {final_bankroll['current_value']:.2f}")
    print(f"   📈 Lucro/Prejuízo: R$ {final_bankroll['profit']:+.2f}")
    print(f"   💹 ROI: {final_bankroll['roi']:+.2f}%")
    print(f"   ✅ Taxa de acerto: {final_stats['win_rate']:.1f}%")
    print(f"   🎲 Total de apostas: {final_stats['total_bets']}")
    
    print(f"\n📁 Banco de dados salvo em: {test_db}")
    print("   Você pode abrir e inspecionar o arquivo SQLite")
    
    print("\n" + "="*80)
    print("  SISTEMA PRONTO PARA USO! 🚀")
    print("  Execute: streamlit run app_betting.py")
    print("="*80 + "\n")


if __name__ == "__main__":
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

