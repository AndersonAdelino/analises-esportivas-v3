"""
Testes para o sistema de gerenciamento de banca
"""
import pytest
import os
import sqlite3
from bankroll_manager import BankrollManager


@pytest.fixture
def temp_db(tmp_path):
    """Cria banco de dados temporário para testes"""
    db_path = tmp_path / "test_bankroll.db"
    return str(db_path)


@pytest.fixture
def bankroll_manager(temp_db):
    """Cria instância do gerenciador com DB temporário"""
    return BankrollManager(db_path=temp_db)


class TestBankrollSetup:
    """Testes para configuração da banca"""
    
    def test_setup_bankroll(self, bankroll_manager):
        """Testa configuração inicial da banca"""
        result = bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        assert result['initial_value'] == 1000.0
        assert result['current_value'] == 1000.0
        assert 'id' in result
        assert 'created_at' in result
    
    def test_setup_bankroll_twice_raises_error(self, bankroll_manager):
        """Testa que não permite configurar banca duas vezes"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        with pytest.raises(ValueError, match="já configurada"):
            bankroll_manager.setup_bankroll(initial_value=2000.0)
    
    def test_get_bankroll_returns_none_if_not_setup(self, temp_db):
        """Testa que retorna None se banca não configurada"""
        manager = BankrollManager(db_path=temp_db)
        result = manager.get_bankroll()
        
        assert result is None
    
    def test_get_bankroll_returns_correct_data(self, bankroll_manager):
        """Testa que retorna dados corretos da banca"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        result = bankroll_manager.get_bankroll()
        
        assert result['initial_value'] == 1000.0
        assert result['current_value'] == 1000.0


class TestBetManagement:
    """Testes para gerenciamento de apostas"""
    
    def test_place_bet(self, bankroll_manager):
        """Testa registro de aposta"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        bet_id = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            match_date="2024-01-15 15:00",
            market="Vitória Casa",
            odds=2.0,
            stake=50.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1,
            notes="Teste"
        )
        
        assert bet_id > 0
        
        # Verifica se banca foi deduzida
        bankroll = bankroll_manager.get_bankroll()
        assert bankroll['current_value'] == 950.0
    
    def test_place_bet_insufficient_funds(self, bankroll_manager):
        """Testa erro ao apostar sem fundos suficientes"""
        bankroll_manager.setup_bankroll(initial_value=100.0)
        
        with pytest.raises(ValueError, match="Saldo insuficiente"):
            bankroll_manager.place_bet(
                match_info="Arsenal FC vs Liverpool FC",
                home_team="Arsenal FC",
                away_team="Liverpool FC",
                market="Vitória Casa",
                odds=2.0,
                stake=150.0,
                prob_model=0.6,
                ev_percent=20.0,
                kelly_percent=0.1
            )
    
    def test_settle_bet_won(self, bankroll_manager):
        """Testa finalização de aposta ganha"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        bet_id = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            market="Vitória Casa",
            odds=2.0,
            stake=100.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1
        )
        
        # Finaliza como ganha
        bankroll_manager.settle_bet(bet_id, result='WON')
        
        # Verifica banca atualizada (900 + 200 = 1100)
        bankroll = bankroll_manager.get_bankroll()
        assert bankroll['current_value'] == 1100.0
    
    def test_settle_bet_lost(self, bankroll_manager):
        """Testa finalização de aposta perdida"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        bet_id = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            market="Vitória Casa",
            odds=2.0,
            stake=100.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1
        )
        
        # Finaliza como perdida
        bankroll_manager.settle_bet(bet_id, result='LOST')
        
        # Verifica banca (já estava em 900, continua em 900)
        bankroll = bankroll_manager.get_bankroll()
        assert bankroll['current_value'] == 900.0
    
    def test_settle_bet_cancelled(self, bankroll_manager):
        """Testa finalização de aposta cancelada"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        bet_id = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            market="Vitória Casa",
            odds=2.0,
            stake=100.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1
        )
        
        # Cancela aposta
        bankroll_manager.settle_bet(bet_id, result='CANCELLED')
        
        # Verifica que stake foi devolvido (900 + 100 = 1000)
        bankroll = bankroll_manager.get_bankroll()
        assert bankroll['current_value'] == 1000.0


class TestBankrollHistory:
    """Testes para histórico da banca"""
    
    def test_get_bankroll_history(self, bankroll_manager):
        """Testa recuperação do histórico"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        # Faz algumas apostas
        bet1 = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            market="Vitória Casa",
            odds=2.0,
            stake=100.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1
        )
        
        bankroll_manager.settle_bet(bet1, result='WON')
        
        # Busca histórico
        history = bankroll_manager.get_bankroll_history()
        
        assert len(history) >= 2  # Setup + aposta + resultado
        assert history.iloc[0]['change_reason'] == 'Configuração inicial'


class TestStatistics:
    """Testes para estatísticas"""
    
    def test_get_statistics_no_bets(self, bankroll_manager):
        """Testa estatísticas sem apostas"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        stats = bankroll_manager.get_statistics()
        
        assert stats['total_bets'] == 0
        assert stats['pending_bets'] == 0
        assert stats['settled_bets'] == 0
        assert stats['win_rate'] == 0
        assert stats['total_profit'] == 0
        assert stats['roi'] == 0
    
    def test_get_statistics_with_bets(self, bankroll_manager):
        """Testa estatísticas com apostas"""
        bankroll_manager.setup_bankroll(initial_value=1000.0)
        
        # Aposta 1: Ganha
        bet1 = bankroll_manager.place_bet(
            match_info="Arsenal FC vs Liverpool FC",
            home_team="Arsenal FC",
            away_team="Liverpool FC",
            market="Vitória Casa",
            odds=2.0,
            stake=100.0,
            prob_model=0.6,
            ev_percent=20.0,
            kelly_percent=0.1
        )
        bankroll_manager.settle_bet(bet1, result='WON')
        
        # Aposta 2: Perde
        bet2 = bankroll_manager.place_bet(
            match_info="Chelsea FC vs Man City",
            home_team="Chelsea FC",
            away_team="Man City",
            market="Vitória Casa",
            odds=3.0,
            stake=50.0,
            prob_model=0.4,
            ev_percent=10.0,
            kelly_percent=0.05
        )
        bankroll_manager.settle_bet(bet2, result='LOST')
        
        stats = bankroll_manager.get_statistics()
        
        assert stats['total_bets'] == 2
        assert stats['settled_bets'] == 2
        assert stats['won_bets'] == 1
        assert stats['lost_bets'] == 1
        assert stats['win_rate'] == 50.0
        assert stats['total_staked'] == 150.0
        assert stats['total_profit'] == 50.0  # Ganhou 100, perdeu 50


if __name__ == "__main__":
    pytest.main([__file__, '-v'])

