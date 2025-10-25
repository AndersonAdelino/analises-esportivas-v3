"""
Sistema de Heurísticas para Análise e Predição de Futebol

Heurísticas são regras simples baseadas em padrões observados:
- Forma recente (últimos N jogos)
- Confronto direto (head-to-head)
- Sequências de vitórias/derrotas
- Performance casa vs fora
- Média de gols
- Tendências ofensivas/defensivas
"""

import pandas as pd
import numpy as np
from datetime import datetime
from glob import glob
import os


class HeuristicasModel:
    """Sistema de heurísticas para análise de futebol"""
    
    def __init__(self):
        """Inicializa o modelo de heurísticas"""
        self.df = None
        self.teams = None
        
    def _load_data_from_api(self, league_code):
        """Carrega dados diretamente da API"""
        from api_client import FootballDataClient
        
        try:
            client = FootballDataClient()
            matches_data = client.get_competition_matches(league_code, status='FINISHED', limit=100)
            
            matches_list = []
            for match in matches_data.get('matches', []):
                if match['status'] != 'FINISHED':
                    continue
                    
                score = match.get('score', {}).get('fullTime', {})
                if score.get('home') is None or score.get('away') is None:
                    continue
                
                matches_list.append({
                    'time_casa': match['homeTeam']['name'],
                    'time_visitante': match['awayTeam']['name'],
                    'gols_casa': score['home'],
                    'gols_visitante': score['away'],
                    'data': match['utcDate'][:10]
                })
            
            if not matches_list:
                raise ValueError(f"Nenhuma partida finalizada encontrada")
            
            return pd.DataFrame(matches_list)
        
        except Exception as e:
            raise RuntimeError(f"Erro ao buscar dados da API: {e}")
    
    def _normalize_data(self, df):
        """
        Normaliza dados de time_casa/time_visitante para formato time/adversario
        
        Args:
            df: DataFrame com colunas time_casa, time_visitante, gols_casa, gols_visitante
            
        Returns:
            DataFrame normalizado com colunas time, adversario, gols_marcados, gols_sofridos, resultado, local
        """
        # Cria duas linhas para cada partida (uma do ponto de vista de cada time)
        
        # Jogos do time da casa
        jogos_casa = df[['data', 'time_casa', 'time_visitante', 'gols_casa', 'gols_visitante']].copy()
        if 'competicao' in df.columns:
            jogos_casa['competicao'] = df['competicao']
        
        jogos_casa = jogos_casa.rename(columns={
            'time_casa': 'time',
            'time_visitante': 'adversario',
            'gols_casa': 'gols_marcados',
            'gols_visitante': 'gols_sofridos'
        })
        jogos_casa['local'] = 'Casa'
        
        # Jogos do time visitante
        jogos_fora = df[['data', 'time_casa', 'time_visitante', 'gols_casa', 'gols_visitante']].copy()
        if 'competicao' in df.columns:
            jogos_fora['competicao'] = df['competicao']
        
        jogos_fora = jogos_fora.rename(columns={
            'time_visitante': 'time',
            'time_casa': 'adversario',
            'gols_visitante': 'gols_marcados',
            'gols_casa': 'gols_sofridos'
        })
        jogos_fora['local'] = 'Fora'
        
        # Combina
        df_normalized = pd.concat([jogos_casa, jogos_fora], ignore_index=True)
        
        # Adiciona coluna de resultado
        def calcular_resultado(row):
            if row['gols_marcados'] > row['gols_sofridos']:
                return 'Vitoria'
            elif row['gols_marcados'] < row['gols_sofridos']:
                return 'Derrota'
            else:
                return 'Empate'
        
        df_normalized['resultado'] = df_normalized.apply(calcular_resultado, axis=1)
        
        return df_normalized.sort_values('data', ascending=False)
    
    def load_data(self, league_code=None):
        """
        Carrega dados de partidas
        
        Args:
            league_code: Código da liga (ex: 'PL', 'BSA'). Se None, carrega Premier League
        
        Returns:
            self (para encadeamento de métodos)
        """
        from config import LEAGUES, PREMIER_LEAGUE_CODE
        
        if league_code is None:
            league_code = PREMIER_LEAGUE_CODE
        
        # Mapeia code para nome do arquivo
        league_name_map = {info['code']: name.lower().replace(' ', '_').replace('ã', 'a') 
                          for name, info in LEAGUES.items()}
        league_prefix = league_name_map.get(league_code, 'league')
        
        # Busca arquivos da liga específica
        csv_files = glob(f'data/{league_prefix}_matches_*.csv')
        
        # Se não encontrou arquivos específicos, tenta o formato antigo
        if not csv_files:
            csv_files = glob('data/all_teams_matches_*.csv')
        
        if not csv_files:
            # Sem arquivos locais, tenta buscar da API
            print(f"Nenhum arquivo local encontrado. Buscando dados da API...")
            df_raw = self._load_data_from_api(league_code)
            self.df = self._normalize_data(df_raw)
            self.teams = sorted(set(self.df['time'].unique()))
            print(f"Dados carregados: {len(df_raw)} partidas originais, {len(self.df)} linhas processadas, {len(self.teams)} times")
            return self
        
        csv_file = max(csv_files, key=os.path.getctime)
        print(f"Carregando dados de: {csv_file}")
        
        df_raw = pd.read_csv(csv_file)
        df_raw['data'] = pd.to_datetime(df_raw['data'])
        
        # Filtra pela liga específica
        league_full_name = [info['name'] for name, info in LEAGUES.items() if info['code'] == league_code][0]
        if 'competicao' in df_raw.columns:
            # Tenta filtrar pelo nome completo da liga
            df_raw = df_raw[df_raw['competicao'].str.contains(league_full_name.split()[0], na=False, case=False)]
        
        # Normaliza os dados
        self.df = self._normalize_data(df_raw)
        self.teams = sorted(set(self.df['time'].unique()))
        
        print(f"Dados carregados: {len(df_raw)} partidas originais, {len(self.df)} linhas processadas, {len(self.teams)} times")
        
        return self
    
    def forma_recente(self, team, n_jogos=5):
        """
        Calcula a forma recente de um time
        
        Args:
            team: Nome do time
            n_jogos: Número de jogos recentes a considerar
            
        Returns:
            Dict com estatísticas da forma recente
        """
        jogos = self.df[self.df['time'] == team].sort_values('data', ascending=False).head(n_jogos)
        
        if len(jogos) == 0:
            return None
        
        vitorias = len(jogos[jogos['resultado'] == 'Vitoria'])
        empates = len(jogos[jogos['resultado'] == 'Empate'])
        derrotas = len(jogos[jogos['resultado'] == 'Derrota'])
        
        pontos = vitorias * 3 + empates
        pontos_max = len(jogos) * 3
        aproveitamento = (pontos / pontos_max * 100) if pontos_max > 0 else 0
        
        gols_marcados = jogos['gols_marcados'].sum()
        gols_sofridos = jogos['gols_sofridos'].sum()
        media_gols_marcados = jogos['gols_marcados'].mean()
        media_gols_sofridos = jogos['gols_sofridos'].mean()
        
        # Sequência atual
        sequencia = []
        for _, jogo in jogos.iterrows():
            if jogo['resultado'] == 'Vitoria':
                sequencia.append('V')
            elif jogo['resultado'] == 'Empate':
                sequencia.append('E')
            else:
                sequencia.append('D')
        
        return {
            'time': team,
            'jogos': len(jogos),
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'pontos': pontos,
            'aproveitamento': aproveitamento,
            'gols_marcados': gols_marcados,
            'gols_sofridos': gols_sofridos,
            'media_gols_marcados': media_gols_marcados,
            'media_gols_sofridos': media_gols_sofridos,
            'saldo': gols_marcados - gols_sofridos,
            'sequencia': ' '.join(sequencia),
            'invicto': 'D' not in sequencia
        }
    
    def confronto_direto(self, team_a, team_b, n_jogos=5):
        """
        Analisa o histórico de confrontos diretos entre dois times
        
        Args:
            team_a: Time A
            team_b: Time B
            n_jogos: Número de confrontos recentes
            
        Returns:
            Dict com estatísticas do confronto direto
        """
        # Jogos onde team_a enfrentou team_b
        confrontos = self.df[
            ((self.df['time'] == team_a) & (self.df['adversario'] == team_b)) |
            ((self.df['time'] == team_b) & (self.df['adversario'] == team_a))
        ].sort_values('data', ascending=False).head(n_jogos)
        
        if len(confrontos) == 0:
            return None
        
        # Resultados do ponto de vista do team_a
        vitorias_a = 0
        empates = 0
        vitorias_b = 0
        gols_a = 0
        gols_b = 0
        
        for _, jogo in confrontos.iterrows():
            if jogo['time'] == team_a:
                gols_a += jogo['gols_marcados']
                gols_b += jogo['gols_sofridos']
                if jogo['resultado'] == 'Vitoria':
                    vitorias_a += 1
                elif jogo['resultado'] == 'Empate':
                    empates += 1
                else:
                    vitorias_b += 1
            else:  # time == team_b
                gols_b += jogo['gols_marcados']
                gols_a += jogo['gols_sofridos']
                if jogo['resultado'] == 'Vitoria':
                    vitorias_b += 1
                elif jogo['resultado'] == 'Empate':
                    empates += 1
                else:
                    vitorias_a += 1
        
        return {
            'confrontos': len(confrontos),
            'vitorias_a': vitorias_a,
            'empates': empates,
            'vitorias_b': vitorias_b,
            'gols_a': gols_a,
            'gols_b': gols_b,
            'media_gols_a': gols_a / len(confrontos),
            'media_gols_b': gols_b / len(confrontos),
            'favorito': team_a if vitorias_a > vitorias_b else (team_b if vitorias_b > vitorias_a else 'Equilibrado')
        }
    
    def performance_casa_fora(self, team, local='Casa', n_jogos=10):
        """
        Analisa performance do time jogando em casa ou fora
        
        Args:
            team: Nome do time
            local: 'Casa' ou 'Fora'
            n_jogos: Número de jogos a considerar
            
        Returns:
            Dict com estatísticas de performance
        """
        jogos = self.df[
            (self.df['time'] == team) & (self.df['local'] == local)
        ].sort_values('data', ascending=False).head(n_jogos)
        
        if len(jogos) == 0:
            return None
        
        vitorias = len(jogos[jogos['resultado'] == 'Vitoria'])
        empates = len(jogos[jogos['resultado'] == 'Empate'])
        derrotas = len(jogos[jogos['resultado'] == 'Derrota'])
        
        pontos = vitorias * 3 + empates
        aproveitamento = (pontos / (len(jogos) * 3) * 100)
        
        return {
            'time': team,
            'local': local,
            'jogos': len(jogos),
            'vitorias': vitorias,
            'empates': empates,
            'derrotas': derrotas,
            'aproveitamento': aproveitamento,
            'media_gols_marcados': jogos['gols_marcados'].mean(),
            'media_gols_sofridos': jogos['gols_sofridos'].mean()
        }
    
    def tendencia_gols(self, team, n_jogos=5):
        """
        Analisa tendência de gols (over/under)
        
        Args:
            team: Nome do time
            n_jogos: Número de jogos recentes
            
        Returns:
            Dict com tendências de gols
        """
        jogos = self.df[self.df['time'] == team].sort_values('data', ascending=False).head(n_jogos)
        
        if len(jogos) == 0:
            return None
        
        total_gols = jogos['gols_marcados'] + jogos['gols_sofridos']
        
        over_2_5 = len(total_gols[total_gols > 2.5])
        over_1_5 = len(total_gols[total_gols > 1.5])
        btts = len(jogos[(jogos['gols_marcados'] > 0) & (jogos['gols_sofridos'] > 0)])
        
        return {
            'time': team,
            'jogos': len(jogos),
            'media_total_gols': total_gols.mean(),
            'over_2.5_freq': over_2_5 / len(jogos) * 100,
            'over_1.5_freq': over_1_5 / len(jogos) * 100,
            'btts_freq': btts / len(jogos) * 100,
            'maior_gols': int(total_gols.max()),
            'menor_gols': int(total_gols.min())
        }
    
    def sequencias(self, team):
        """
        Identifica sequências de resultados
        
        Args:
            team: Nome do time
            
        Returns:
            Dict com informações sobre sequências
        """
        jogos = self.df[self.df['time'] == team].sort_values('data', ascending=False)
        
        if len(jogos) == 0:
            return None
        
        # Sequência atual
        sequencia_atual = []
        tipo_seq = None
        
        for _, jogo in jogos.iterrows():
            resultado = jogo['resultado']
            
            if tipo_seq is None:
                tipo_seq = resultado
                sequencia_atual.append(resultado)
            elif resultado == tipo_seq:
                sequencia_atual.append(resultado)
            else:
                break
        
        # Maior sequência de vitórias
        max_vitorias = 0
        atual_vitorias = 0
        
        for _, jogo in jogos.iterrows():
            if jogo['resultado'] == 'Vitoria':
                atual_vitorias += 1
                max_vitorias = max(max_vitorias, atual_vitorias)
            else:
                atual_vitorias = 0
        
        # Jogos sem vencer
        jogos_sem_vencer = 0
        for _, jogo in jogos.iterrows():
            if jogo['resultado'] != 'Vitoria':
                jogos_sem_vencer += 1
            else:
                break
        
        return {
            'time': team,
            'sequencia_tipo': tipo_seq,
            'sequencia_tamanho': len(sequencia_atual),
            'sequencia_desc': f"{len(sequencia_atual)} {tipo_seq}(s) consecutiva(s)",
            'max_vitorias_consecutivas': max_vitorias,
            'jogos_sem_vencer': jogos_sem_vencer,
            'invicto': jogos_sem_vencer == 0 or tipo_seq != 'Derrota'
        }
    
    def predict_match(self, home_team, away_team, n_jogos_forma=5):
        """
        Faz predição baseada em heurísticas
        
        Args:
            home_team: Time da casa
            away_team: Time visitante
            n_jogos_forma: Número de jogos para forma recente
            
        Returns:
            Dict com análise heurística completa
        """
        print(f"\nAnalisando: {home_team} vs {away_team}")
        print("=" * 70)
        
        # 1. Forma recente
        forma_casa = self.forma_recente(home_team, n_jogos_forma)
        forma_fora = self.forma_recente(away_team, n_jogos_forma)
        
        # 2. Performance específica (casa/fora)
        perf_casa_casa = self.performance_casa_fora(home_team, 'Casa')
        perf_fora_fora = self.performance_casa_fora(away_team, 'Fora')
        
        # 3. Confronto direto
        confronto = self.confronto_direto(home_team, away_team)
        
        # 4. Tendência de gols
        tend_gols_casa = self.tendencia_gols(home_team, n_jogos_forma)
        tend_gols_fora = self.tendencia_gols(away_team, n_jogos_forma)
        
        # 5. Sequências
        seq_casa = self.sequencias(home_team)
        seq_fora = self.sequencias(away_team)
        
        # Análise heurística (pontuação)
        pontos_casa = 0
        pontos_fora = 0
        fatores = []
        
        # Fator 1: Forma recente (0-3 pontos)
        if forma_casa and forma_fora:
            if forma_casa['aproveitamento'] > forma_fora['aproveitamento'] + 15:
                pontos_casa += 3
                fatores.append(f"Forma recente favorece {home_team} ({forma_casa['aproveitamento']:.0f}% vs {forma_fora['aproveitamento']:.0f}%)")
            elif forma_fora['aproveitamento'] > forma_casa['aproveitamento'] + 15:
                pontos_fora += 3
                fatores.append(f"Forma recente favorece {away_team} ({forma_fora['aproveitamento']:.0f}% vs {forma_casa['aproveitamento']:.0f}%)")
            elif forma_casa['aproveitamento'] > forma_fora['aproveitamento']:
                pontos_casa += 1
            elif forma_fora['aproveitamento'] > forma_casa['aproveitamento']:
                pontos_fora += 1
        
        # Fator 2: Performance casa/fora (0-2 pontos)
        if perf_casa_casa and perf_fora_fora:
            if perf_casa_casa['aproveitamento'] > perf_fora_fora['aproveitamento'] + 20:
                pontos_casa += 2
                fatores.append(f"{home_team} forte em casa ({perf_casa_casa['aproveitamento']:.0f}%)")
            elif perf_fora_fora['aproveitamento'] > perf_casa_casa['aproveitamento']:
                pontos_fora += 1
        
        # Fator 3: Confronto direto (0-2 pontos)
        if confronto and confronto['confrontos'] >= 3:
            if confronto['favorito'] == home_team:
                pontos_casa += 2
                fatores.append(f"Historico favorece {home_team} ({confronto['vitorias_a']}V-{confronto['empates']}E-{confronto['vitorias_b']}D)")
            elif confronto['favorito'] == away_team:
                pontos_fora += 2
                fatores.append(f"Historico favorece {away_team}")
        
        # Fator 4: Sequências (0-2 pontos)
        if seq_casa and seq_fora:
            if seq_casa['sequencia_tipo'] == 'Vitoria' and seq_casa['sequencia_tamanho'] >= 3:
                pontos_casa += 2
                fatores.append(f"{home_team} em sequencia de {seq_casa['sequencia_tamanho']} vitorias")
            if seq_fora['sequencia_tipo'] == 'Derrota' and seq_fora['sequencia_tamanho'] >= 3:
                pontos_casa += 1
                fatores.append(f"{away_team} em ma fase ({seq_fora['sequencia_tamanho']} derrotas)")
            
            if seq_fora['sequencia_tipo'] == 'Vitoria' and seq_fora['sequencia_tamanho'] >= 3:
                pontos_fora += 2
                fatores.append(f"{away_team} em sequencia de {seq_fora['sequencia_tamanho']} vitorias")
            if seq_casa['sequencia_tipo'] == 'Derrota' and seq_casa['sequencia_tamanho'] >= 3:
                pontos_fora += 1
                fatores.append(f"{home_team} em ma fase ({seq_casa['sequencia_tamanho']} derrotas)")
        
        # Fator 5: Média de gols (para over/under)
        gols_esperados = 0
        if forma_casa and forma_fora:
            gols_esperados = (forma_casa['media_gols_marcados'] + 
                            forma_fora['media_gols_sofridos'] +
                            forma_fora['media_gols_marcados'] + 
                            forma_casa['media_gols_sofridos']) / 2
        
        # Decisão final
        total_pontos = pontos_casa + pontos_fora
        
        if total_pontos == 0:
            resultado_previsto = "Empate"
            confianca = 30
        elif pontos_casa > pontos_fora + 2:
            resultado_previsto = f"Vitoria {home_team}"
            confianca = min(70 + (pontos_casa - pontos_fora) * 5, 90)
        elif pontos_fora > pontos_casa + 2:
            resultado_previsto = f"Vitoria {away_team}"
            confianca = min(70 + (pontos_fora - pontos_casa) * 5, 90)
        elif pontos_casa > pontos_fora:
            resultado_previsto = f"Vitoria {home_team}"
            confianca = 55
        elif pontos_fora > pontos_casa:
            resultado_previsto = f"Vitoria {away_team}"
            confianca = 55
        else:
            resultado_previsto = "Empate"
            confianca = 45
        
        # Over/Under prediction
        if gols_esperados > 2.7:
            over_under = "Over 2.5"
            confianca_ou = 65
        elif gols_esperados < 2.2:
            over_under = "Under 2.5"
            confianca_ou = 65
        else:
            over_under = "Incerto"
            confianca_ou = 50
        
        # BTTS prediction
        if tend_gols_casa and tend_gols_fora:
            btts_avg = (tend_gols_casa['btts_freq'] + tend_gols_fora['btts_freq']) / 2
            if btts_avg > 60:
                btts = "Sim"
                confianca_btts = 65
            elif btts_avg < 40:
                btts = "Nao"
                confianca_btts = 60
            else:
                btts = "Incerto"
                confianca_btts = 50
        else:
            btts = "Incerto"
            confianca_btts = 50
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'resultado_previsto': resultado_previsto,
            'confianca': confianca,
            'pontos_casa': pontos_casa,
            'pontos_fora': pontos_fora,
            'fatores': fatores,
            'gols_esperados': gols_esperados,
            'over_under': over_under,
            'confianca_ou': confianca_ou,
            'btts': btts,
            'confianca_btts': confianca_btts,
            'forma_casa': forma_casa,
            'forma_fora': forma_fora,
            'perf_casa': perf_casa_casa,
            'perf_fora': perf_fora_fora,
            'confronto': confronto,
            'sequencias_casa': seq_casa,
            'sequencias_fora': seq_fora
        }


def print_prediction(pred):
    """Imprime predição de forma formatada"""
    print("\n" + "=" * 80)
    print(f"ANALISE HEURISTICA: {pred['home_team']} vs {pred['away_team']}")
    print("=" * 80)
    
    print(f"\nRESULTADO PREVISTO: {pred['resultado_previsto']}")
    print(f"Confianca: {pred['confianca']}%")
    print(f"Pontuacao Heuristica: Casa {pred['pontos_casa']} x {pred['pontos_fora']} Fora")
    
    print(f"\nFATORES CONSIDERADOS:")
    if pred['fatores']:
        for fator in pred['fatores']:
            print(f"  - {fator}")
    else:
        print("  - Times equilibrados")
    
    print(f"\nFORMA RECENTE (ultimos 5 jogos):")
    if pred['forma_casa']:
        fc = pred['forma_casa']
        print(f"  {pred['home_team']}: {fc['sequencia']} - {fc['aproveitamento']:.0f}% aproveitamento")
    if pred['forma_fora']:
        ff = pred['forma_fora']
        print(f"  {pred['away_team']}: {ff['sequencia']} - {ff['aproveitamento']:.0f}% aproveitamento")
    
    print(f"\nPERFORMANCE CASA/FORA:")
    if pred['perf_casa']:
        pc = pred['perf_casa']
        print(f"  {pred['home_team']} em casa: {pc['aproveitamento']:.0f}% ({pc['vitorias']}V-{pc['empates']}E-{pc['derrotas']}D)")
    if pred['perf_fora']:
        pf = pred['perf_fora']
        print(f"  {pred['away_team']} fora: {pf['aproveitamento']:.0f}% ({pf['vitorias']}V-{pf['empates']}E-{pf['derrotas']}D)")
    
    if pred['confronto'] and pred['confronto']['confrontos'] > 0:
        c = pred['confronto']
        print(f"\nCONFRONTO DIRETO (ultimos {c['confrontos']} jogos):")
        print(f"  {pred['home_team']}: {c['vitorias_a']} vitorias ({c['gols_a']} gols)")
        print(f"  Empates: {c['empates']}")
        print(f"  {pred['away_team']}: {c['vitorias_b']} vitorias ({c['gols_b']} gols)")
        print(f"  Favorito historico: {c['favorito']}")
    
    print(f"\nPREDICOES ADICIONAIS:")
    print(f"  Gols esperados: {pred['gols_esperados']:.2f}")
    print(f"  Over/Under 2.5: {pred['over_under']} (confianca: {pred['confianca_ou']}%)")
    print(f"  Ambos marcam: {pred['btts']} (confianca: {pred['confianca_btts']}%)")
    
    print("=" * 80)


if __name__ == "__main__":
    print("\n")
    print("=" * 80)
    print("SISTEMA DE HEURISTICAS - ANALISE DE FUTEBOL")
    print("=" * 80)
    print("\n")
    
    # Carrega modelo
    model = HeuristicasModel()
    model.load_data()
    
    print("\n")
    print("=" * 80)
    print("EXEMPLOS DE ANALISES HEURISTICAS")
    print("=" * 80)
    
    # Exemplos
    partidas = [
        ('Arsenal FC', 'Liverpool FC'),
        ('Manchester City FC', 'Chelsea FC'),
        ('Manchester United FC', 'Tottenham Hotspur FC'),
    ]
    
    for home, away in partidas:
        try:
            pred = model.predict_match(home, away)
            print_prediction(pred)
            print("\n")
        except Exception as e:
            print(f"\nErro ao analisar {home} vs {away}: {e}\n")
    
    print("=" * 80)
    print("ANALISES CONCLUIDAS!")
    print("=" * 80)
    print("\nUso programatico:")
    print("  from heuristicas import HeuristicasModel")
    print("  model = HeuristicasModel()")
    print("  model.load_data()")
    print("  pred = model.predict_match('Arsenal FC', 'Liverpool FC')")
    print()

