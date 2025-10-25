"""
Configuração centralizada de logging para o projeto

Uso:
    from logger_config import setup_logger
    
    logger = setup_logger(__name__)
    logger.info("Mensagem informativa")
    logger.warning("Aviso")
    logger.error("Erro")
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logger(name='analises_esportivas', level=logging.INFO, log_to_console=True):
    """
    Configura logger para o projeto com rotação de arquivos
    
    Args:
        name: Nome do logger (geralmente __name__ do módulo)
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_console: Se True, também exibe logs no console
        
    Returns:
        Logger configurado
        
    Exemplos:
        >>> logger = setup_logger(__name__)
        >>> logger.info("Sistema iniciado")
        >>> logger.warning("Aviso: API próxima do limite")
        >>> logger.error("Erro ao processar dados", exc_info=True)
    """
    
    # Cria diretório de logs se não existir
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)
    
    # Formata mensagens com timestamp e informações detalhadas
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para arquivo (rotativo - 10MB, mantém 5 backups)
    log_file = os.path.join(log_dir, f'app_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)
    
    # Configura logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove handlers existentes para evitar duplicação
    logger.handlers.clear()
    
    # Adiciona file handler
    logger.addHandler(file_handler)
    
    # Handler para console (apenas warnings e errors)
    if log_to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.WARNING)
        logger.addHandler(console_handler)
    
    return logger


def log_function_call(logger):
    """
    Decorator para logar chamadas de função automaticamente
    
    Args:
        logger: Logger configurado
        
    Exemplo:
        >>> logger = setup_logger(__name__)
        >>> 
        >>> @log_function_call(logger)
        >>> def minha_funcao(x, y):
        >>>     return x + y
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"Chamando {func.__name__} com args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"{func.__name__} retornou: {result}")
                return result
            except Exception as e:
                logger.error(f"Erro em {func.__name__}: {str(e)}", exc_info=True)
                raise
        return wrapper
    return decorator


def log_model_training(logger, model_name):
    """
    Context manager para logar treinamento de modelos
    
    Args:
        logger: Logger configurado
        model_name: Nome do modelo sendo treinado
        
    Exemplo:
        >>> logger = setup_logger(__name__)
        >>> with log_model_training(logger, "Dixon-Coles"):
        >>>     model.fit(df)
    """
    class ModelTrainingLogger:
        def __enter__(self):
            logger.info(f"Iniciando treinamento do modelo: {model_name}")
            self.start_time = datetime.now()
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            duration = (datetime.now() - self.start_time).total_seconds()
            
            if exc_type is None:
                logger.info(f"Modelo {model_name} treinado com sucesso em {duration:.2f}s")
            else:
                logger.error(
                    f"Erro ao treinar modelo {model_name} após {duration:.2f}s: {exc_val}",
                    exc_info=True
                )
            
            return False  # Propaga exceção se houver
    
    return ModelTrainingLogger()


# Configuração global do projeto
def setup_project_logging():
    """
    Configura logging para todo o projeto
    Deve ser chamado no início da aplicação
    """
    # Logger principal
    main_logger = setup_logger('analises_esportivas', level=logging.INFO)
    
    # Loggers específicos para módulos
    setup_logger('dixon_coles', level=logging.INFO)
    setup_logger('offensive_defensive', level=logging.INFO)
    setup_logger('heuristicas', level=logging.INFO)
    setup_logger('ensemble', level=logging.INFO)
    setup_logger('betting_tools', level=logging.INFO)
    setup_logger('bankroll_manager', level=logging.INFO)
    setup_logger('api_client', level=logging.INFO)
    
    main_logger.info("Sistema de logging configurado")
    main_logger.info(f"Logs sendo salvos em: logs/")
    
    return main_logger


if __name__ == "__main__":
    # Teste do sistema de logging
    logger = setup_logger('test', level=logging.DEBUG)
    
    logger.debug("Mensagem de debug")
    logger.info("Mensagem informativa")
    logger.warning("Mensagem de aviso")
    logger.error("Mensagem de erro")
    
    # Teste do decorator
    @log_function_call(logger)
    def teste_funcao(x, y):
        return x + y
    
    resultado = teste_funcao(2, 3)
    
    # Teste do context manager
    with log_model_training(logger, "Modelo Teste"):
        import time
        time.sleep(0.5)
    
    print("✅ Sistema de logging testado com sucesso!")
    print("📁 Verifique o arquivo de log em logs/")

