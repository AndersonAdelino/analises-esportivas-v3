"""
Controle de Versão do Sistema de Análises Esportivas
"""

__version__ = "1.2.0"
__version_name__ = "Ranking Edition"
__release_date__ = "2025-10-28"

# Changelog
CHANGELOG = {
    "1.2.0": {
        "date": "2025-10-28",
        "name": "Ranking Edition",
        "features": [
            "Sistema de ranqueamento de apostas",
            "3 perfis de apostador (conservador/moderado/agressivo)",
            "Cálculo automático de stake com Kelly ajustado",
            "Score normalizado 0-100",
            "Interface Streamlit para ranqueamento",
            "14 testes unitários",
            "Documentação completa"
        ]
    },
    "1.1.0": {
        "date": "2025-10",
        "name": "Multi-League Update",
        "features": [
            "Suporte a 5 ligas (Premier League, Brasileirão, La Liga, Serie A, Primeira Liga)",
            "Sistema de análise por time com gráficos",
            "Comparação visual entre modelos",
            "Heatmaps de placares"
        ]
    },
    "1.0.0": {
        "date": "2025-09",
        "name": "Initial Release",
        "features": [
            "Sistema de gerenciamento de banca",
            "Value betting e Kelly Criterion",
            "Interface Streamlit completa",
            "3 modelos preditivos (Dixon-Coles, Offensive-Defensive, Heurísticas)"
        ]
    }
}


def get_version():
    """Retorna a versão atual"""
    return __version__


def get_version_info():
    """Retorna informações completas da versão"""
    return {
        "version": __version__,
        "name": __version_name__,
        "release_date": __release_date__
    }


def get_full_version_string():
    """Retorna string formatada da versão"""
    return f"v{__version__} - {__version_name__}"


if __name__ == "__main__":
    print(f"Sistema de Análises Esportivas")
    print(f"Versão: {get_full_version_string()}")
    print(f"Release: {__release_date__}")

