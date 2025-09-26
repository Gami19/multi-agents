"""ログ設定管理"""
import logging
import sys
from typing import Optional

def setup_logging(
    level: int = logging.WARNING,
    format_str: Optional[str] = None,
    handlers: Optional[list] = None
) -> logging.Logger:
    """
    アプリケーションのログ設定を初期化
    
    Args:
        level: ログレベル (デフォルト: WARNING)
        format_str: カスタムフォーマット文字列
        handlers: カスタムハンドラー一覧
    
    Returns:
        Logger: 設定されたロガーインスタンス
    """
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    if handlers is None:
        handlers = [
            logging.StreamHandler(sys.stdout)
        ]
    
    # 基本的なログ設定
    logging.basicConfig(
        level=level,
        format=format_str,
        handlers=handlers
    )
    
    logger = logging.getLogger(__name__)
    logger.info(f"ログレベル設定完了: {logging.getLevelName(level)}")
    
    return logger

def get_logger(name: str = __name__) -> logging.Logger:
    """名前付きロガーを取得"""
    return logging.getLogger(name)

# 推論に関するログ設定
def setup_reasoning_logger() -> logging.Logger:
    """推論専用のロガー設定"""
    reasoning_logger = logging.getLogger("agno_reasoning")
    
    if not reasoning_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s [REASONING] - %(message)s'
        )
        handler.setFormatter(formatter)
        reasoning_logger.addHandler(handler)
        reasoning_logger.setLevel(logging.INFO)
    
    return reasoning_logger

# タスク用のログフィルタ
class TaskFilter(logging.Filter):
    """特定のタスクにフォーカスしたログフィルター"""
    
    def __init__(self, task_name: str):
        super().__init__()
        self.task_name = task_name
    
    def filter(self, record):
        """タスク名によるフィルタリング"""
        return self.task_name in record.getMessage()