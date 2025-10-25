"""
Gerenciamento de Banca e Histórico de Apostas

Sistema completo para:
- Gerenciar banca (saldo atual)
- Registrar apostas
- Acompanhar resultados
- Histórico e estatísticas
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import os


class BankrollManager:
    """Gerenciador de banca e apostas"""
    
    def __init__(self, db_path: str = "data/bankroll.db"):
        """
        Inicializa gerenciador
        
        Args:
            db_path: Caminho para o banco de dados SQLite
        """
        self.db_path = db_path
        
        # Garante que o diretório existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Inicializa banco
        self._init_database()
    
    def _init_database(self):
        """Cria tabelas se não existirem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de configuração da banca
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bankroll (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                initial_value REAL NOT NULL,
                current_value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabela de apostas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_info TEXT NOT NULL,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                match_date TEXT,
                market TEXT NOT NULL,
                odds REAL NOT NULL,
                stake REAL NOT NULL,
                prob_model REAL NOT NULL,
                ev_percent REAL NOT NULL,
                kelly_percent REAL NOT NULL,
                status TEXT DEFAULT 'PENDING',
                result TEXT,
                profit REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                settled_at TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Tabela de histórico da banca (snapshots)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bankroll_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bankroll_value REAL NOT NULL,
                change_amount REAL NOT NULL,
                change_reason TEXT NOT NULL,
                bet_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (bet_id) REFERENCES bets(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def setup_bankroll(self, initial_value: float) -> Dict:
        """
        Configura banca inicial (apenas se não houver banca)
        
        Args:
            initial_value: Valor inicial da banca
            
        Returns:
            Dict com informações da banca
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verifica se já existe banca
        cursor.execute("SELECT COUNT(*) FROM bankroll")
        count = cursor.fetchone()[0]
        
        if count > 0:
            conn.close()
            raise ValueError("Banca já configurada. Use reset_bankroll() para reiniciar.")
        
        # Insere banca inicial
        cursor.execute("""
            INSERT INTO bankroll (initial_value, current_value)
            VALUES (?, ?)
        """, (initial_value, initial_value))
        
        # Registra no histórico
        cursor.execute("""
            INSERT INTO bankroll_history (bankroll_value, change_amount, change_reason)
            VALUES (?, ?, ?)
        """, (initial_value, initial_value, "Configuração inicial"))
        
        conn.commit()
        
        # Retorna informações
        cursor.execute("""
            SELECT id, initial_value, current_value, created_at
            FROM bankroll
            ORDER BY id DESC LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        return {
            'id': result[0],
            'initial_value': result[1],
            'current_value': result[2],
            'created_at': result[3]
        }
    
    def get_bankroll(self) -> Optional[Dict]:
        """
        Obtém banca atual
        
        Returns:
            Dict com informações da banca ou None se não configurada
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, initial_value, current_value, created_at, updated_at
            FROM bankroll
            ORDER BY id DESC LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        return {
            'id': result[0],
            'initial_value': result[1],
            'current_value': result[2],
            'created_at': result[3],
            'updated_at': result[4],
            'profit': result[2] - result[1],
            'roi': ((result[2] - result[1]) / result[1] * 100) if result[1] > 0 else 0
        }
    
    def update_bankroll(self, new_value: float, reason: str = "Ajuste manual") -> Dict:
        """
        Atualiza valor da banca
        
        Args:
            new_value: Novo valor da banca
            reason: Motivo da alteração
            
        Returns:
            Dict com informações atualizadas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtém valor atual
        cursor.execute("SELECT current_value FROM bankroll ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            raise ValueError("Banca não configurada. Use setup_bankroll() primeiro.")
        
        old_value = result[0]
        change = new_value - old_value
        
        # Atualiza banca
        cursor.execute("""
            UPDATE bankroll
            SET current_value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)
        """, (new_value,))
        
        # Registra no histórico
        cursor.execute("""
            INSERT INTO bankroll_history (bankroll_value, change_amount, change_reason)
            VALUES (?, ?, ?)
        """, (new_value, change, reason))
        
        conn.commit()
        conn.close()
        
        return self.get_bankroll()
    
    def add_bet(self, bet_info: Dict) -> int:
        """
        Registra uma nova aposta
        
        Args:
            bet_info: Dict com informações da aposta
                - match_info: str (ex: "Arsenal vs Chelsea")
                - home_team: str
                - away_team: str
                - match_date: str (opcional)
                - market: str (ex: "Vitória Casa")
                - odds: float
                - stake: float
                - prob_model: float
                - ev_percent: float
                - kelly_percent: float
                - notes: str (opcional)
                
        Returns:
            ID da aposta registrada
        """
        # Valida banca suficiente
        bankroll = self.get_bankroll()
        if not bankroll:
            raise ValueError("Banca não configurada")
        
        stake = bet_info['stake']
        if stake > bankroll['current_value']:
            raise ValueError(f"Saldo insuficiente. Disponível: R$ {bankroll['current_value']:.2f}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Insere aposta
        cursor.execute("""
            INSERT INTO bets (
                match_info, home_team, away_team, match_date,
                market, odds, stake, prob_model, ev_percent, kelly_percent,
                status, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', ?)
        """, (
            bet_info['match_info'],
            bet_info['home_team'],
            bet_info['away_team'],
            bet_info.get('match_date'),
            bet_info['market'],
            bet_info['odds'],
            stake,
            bet_info['prob_model'],
            bet_info['ev_percent'],
            bet_info['kelly_percent'],
            bet_info.get('notes', '')
        ))
        
        bet_id = cursor.lastrowid
        
        # Deduz valor da banca
        new_bankroll = bankroll['current_value'] - stake
        cursor.execute("""
            UPDATE bankroll
            SET current_value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)
        """, (new_bankroll,))
        
        # Registra no histórico
        cursor.execute("""
            INSERT INTO bankroll_history (bankroll_value, change_amount, change_reason, bet_id)
            VALUES (?, ?, ?, ?)
        """, (new_bankroll, -stake, f"Aposta registrada: {bet_info['market']}", bet_id))
        
        conn.commit()
        conn.close()
        
        return bet_id
    
    def settle_bet(self, bet_id: int, result: str, notes: str = "") -> Dict:
        """
        Finaliza uma aposta (registra resultado)
        
        Args:
            bet_id: ID da aposta
            result: Resultado ('WON', 'LOST', 'VOID')
            notes: Observações adicionais
            
        Returns:
            Dict com informações da aposta finalizada
        """
        if result not in ['WON', 'LOST', 'VOID']:
            raise ValueError("Resultado deve ser 'WON', 'LOST' ou 'VOID'")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Busca aposta
        cursor.execute("""
            SELECT stake, odds, status
            FROM bets
            WHERE id = ?
        """, (bet_id,))
        
        bet = cursor.fetchone()
        if not bet:
            conn.close()
            raise ValueError(f"Aposta {bet_id} não encontrada")
        
        stake, odds, status = bet
        
        if status != 'PENDING':
            conn.close()
            raise ValueError(f"Aposta já finalizada com status: {status}")
        
        # Calcula lucro
        if result == 'WON':
            profit = stake * (odds - 1)  # Lucro líquido
            bankroll_change = stake + profit  # Retorna stake + lucro
        elif result == 'LOST':
            profit = -stake  # Perde tudo
            bankroll_change = 0  # Não retorna nada
        else:  # VOID
            profit = 0  # Sem lucro/perda
            bankroll_change = stake  # Retorna stake
        
        # Atualiza aposta
        cursor.execute("""
            UPDATE bets
            SET status = ?,
                result = ?,
                profit = ?,
                settled_at = CURRENT_TIMESTAMP,
                notes = ?
            WHERE id = ?
        """, (result, result, profit, notes, bet_id))
        
        # Atualiza banca
        bankroll = self.get_bankroll()
        new_bankroll = bankroll['current_value'] + bankroll_change
        
        cursor.execute("""
            UPDATE bankroll
            SET current_value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)
        """, (new_bankroll,))
        
        # Registra no histórico
        reason = f"Aposta {result.lower()}: {profit:+.2f}"
        cursor.execute("""
            INSERT INTO bankroll_history (bankroll_value, change_amount, change_reason, bet_id)
            VALUES (?, ?, ?, ?)
        """, (new_bankroll, bankroll_change, reason, bet_id))
        
        conn.commit()
        conn.close()
        
        return self.get_bet(bet_id)
    
    def get_bet(self, bet_id: int) -> Optional[Dict]:
        """Obtém informações de uma aposta"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM bets
            WHERE id = ?
        """, (bet_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return None
        
        columns = [
            'id', 'match_info', 'home_team', 'away_team', 'match_date',
            'market', 'odds', 'stake', 'prob_model', 'ev_percent', 'kelly_percent',
            'status', 'result', 'profit', 'created_at', 'settled_at', 'notes'
        ]
        
        return dict(zip(columns, result))
    
    def get_pending_bets(self) -> List[Dict]:
        """Obtém todas as apostas pendentes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM bets
            WHERE status = 'PENDING'
            ORDER BY created_at DESC
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        columns = [
            'id', 'match_info', 'home_team', 'away_team', 'match_date',
            'market', 'odds', 'stake', 'prob_model', 'ev_percent', 'kelly_percent',
            'status', 'result', 'profit', 'created_at', 'settled_at', 'notes'
        ]
        
        return [dict(zip(columns, row)) for row in results]
    
    def get_bet_history(self, limit: int = 50) -> pd.DataFrame:
        """
        Obtém histórico de apostas
        
        Args:
            limit: Número máximo de apostas
            
        Returns:
            DataFrame com histórico
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                id, match_info, home_team, away_team, match_date,
                market, odds, stake, prob_model, ev_percent, kelly_percent,
                status, result, profit, created_at, settled_at
            FROM bets
            ORDER BY created_at DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, conn, params=(limit,))
        conn.close()
        
        return df
    
    def get_statistics(self) -> Dict:
        """
        Calcula estatísticas gerais
        
        Returns:
            Dict com estatísticas completas
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estatísticas de apostas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bets,
                SUM(CASE WHEN status = 'WON' THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN status = 'LOST' THEN 1 ELSE 0 END) as losses,
                SUM(CASE WHEN status = 'VOID' THEN 1 ELSE 0 END) as voids,
                SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending,
                SUM(stake) as total_staked,
                SUM(profit) as total_profit,
                AVG(odds) as avg_odds,
                AVG(stake) as avg_stake
            FROM bets
        """)
        
        bet_stats = cursor.fetchone()
        
        # Estatísticas da banca
        bankroll = self.get_bankroll()
        
        conn.close()
        
        if not bet_stats or not bankroll:
            return {
                'total_bets': 0,
                'wins': 0,
                'losses': 0,
                'voids': 0,
                'pending': 0,
                'settled': 0,
                'win_rate': 0,
                'total_staked': 0,
                'total_profit': 0,
                'roi': 0,
                'avg_odds': 0,
                'avg_stake': 0,
                'bankroll': bankroll
            }
        
        total_bets = bet_stats[0] or 0
        wins = bet_stats[1] or 0
        losses = bet_stats[2] or 0
        voids = bet_stats[3] or 0
        pending = bet_stats[4] or 0
        total_staked = bet_stats[5] or 0
        total_profit = bet_stats[6] or 0
        avg_odds = bet_stats[7] or 0
        avg_stake = bet_stats[8] or 0
        
        settled = wins + losses + voids
        win_rate = (wins / settled * 100) if settled > 0 else 0
        roi = (total_profit / total_staked * 100) if total_staked > 0 else 0
        
        return {
            'total_bets': total_bets,
            'wins': wins,
            'losses': losses,
            'voids': voids,
            'pending': pending,
            'settled': settled,
            'win_rate': win_rate,
            'total_staked': total_staked,
            'total_profit': total_profit,
            'roi': roi,
            'avg_odds': avg_odds,
            'avg_stake': avg_stake,
            'bankroll': bankroll
        }
    
    def get_bankroll_evolution(self) -> pd.DataFrame:
        """
        Obtém evolução da banca ao longo do tempo
        
        Returns:
            DataFrame com histórico de valores
        """
        conn = sqlite3.connect(self.db_path)
        
        query = """
            SELECT 
                id, bankroll_value, change_amount, change_reason, bet_id, created_at
            FROM bankroll_history
            ORDER BY created_at ASC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df
    
    def reset_bankroll(self, new_initial_value: float) -> Dict:
        """
        Reseta banca (CUIDADO: deleta histórico!)
        
        Args:
            new_initial_value: Novo valor inicial
            
        Returns:
            Dict com nova banca
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Deleta tudo
        cursor.execute("DELETE FROM bankroll")
        cursor.execute("DELETE FROM bets")
        cursor.execute("DELETE FROM bankroll_history")
        
        conn.commit()
        conn.close()
        
        # Configura nova banca
        return self.setup_bankroll(new_initial_value)
    
    def delete_bet(self, bet_id: int) -> bool:
        """
        Deleta uma aposta pendente (apenas se PENDING)
        
        Args:
            bet_id: ID da aposta
            
        Returns:
            True se deletado, False caso contrário
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verifica status
        cursor.execute("SELECT status, stake FROM bets WHERE id = ?", (bet_id,))
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return False
        
        status, stake = result
        
        if status != 'PENDING':
            conn.close()
            raise ValueError("Apenas apostas pendentes podem ser deletadas")
        
        # Retorna stake para banca
        bankroll = self.get_bankroll()
        new_bankroll = bankroll['current_value'] + stake
        
        cursor.execute("""
            UPDATE bankroll
            SET current_value = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)
        """, (new_bankroll,))
        
        # Registra no histórico
        cursor.execute("""
            INSERT INTO bankroll_history (bankroll_value, change_amount, change_reason, bet_id)
            VALUES (?, ?, ?, ?)
        """, (new_bankroll, stake, f"Aposta cancelada", bet_id))
        
        # Deleta aposta
        cursor.execute("DELETE FROM bets WHERE id = ?", (bet_id,))
        
        conn.commit()
        conn.close()
        
        return True


if __name__ == "__main__":
    # Exemplo de uso
    print("\n" + "="*80)
    print("GERENCIADOR DE BANCA - Exemplo de Uso")
    print("="*80 + "\n")
    
    # Inicializa gerenciador
    manager = BankrollManager("data/bankroll_test.db")
    
    try:
        # Configura banca inicial
        print("1. Configurando banca inicial de R$ 1000...")
        bankroll = manager.setup_bankroll(1000.0)
        print(f"   ✓ Banca configurada: R$ {bankroll['current_value']:.2f}")
    except ValueError:
        print("   ✓ Banca já existe")
        bankroll = manager.get_bankroll()
        print(f"   Banca atual: R$ {bankroll['current_value']:.2f}")
    
    print("\n2. Registrando uma aposta...")
    bet_info = {
        'match_info': 'Arsenal vs Chelsea',
        'home_team': 'Arsenal',
        'away_team': 'Chelsea',
        'match_date': '2025-10-26',
        'market': 'Vitória Casa',
        'odds': 2.20,
        'stake': 25.0,
        'prob_model': 0.55,
        'ev_percent': 5.5,
        'kelly_percent': 2.5,
        'notes': 'Arsenal em boa forma'
    }
    
    bet_id = manager.add_bet(bet_info)
    print(f"   ✓ Aposta registrada (ID: {bet_id})")
    
    bankroll = manager.get_bankroll()
    print(f"   Banca após aposta: R$ {bankroll['current_value']:.2f}")
    
    print("\n3. Apostas pendentes:")
    pending = manager.get_pending_bets()
    for bet in pending:
        print(f"   - ID {bet['id']}: {bet['match_info']} | {bet['market']} @ {bet['odds']:.2f} | R$ {bet['stake']:.2f}")
    
    print("\n4. Estatísticas:")
    stats = manager.get_statistics()
    print(f"   Total de apostas: {stats['total_bets']}")
    print(f"   Pendentes: {stats['pending']}")
    print(f"   Banca atual: R$ {stats['bankroll']['current_value']:.2f}")
    print(f"   ROI da banca: {stats['bankroll']['roi']:+.2f}%")
    
    print("\n" + "="*80)
    print("Para finalizar uma aposta, use:")
    print(f"  manager.settle_bet({bet_id}, 'WON')  # ou 'LOST' ou 'VOID'")
    print("="*80 + "\n")

