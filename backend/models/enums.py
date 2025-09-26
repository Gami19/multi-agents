"""列挙型定義"""
from enum import Enum

class AgentServiceType(str, Enum):
    """エージェントサービス種別"""
    AWS_DOCUMENTATION = "aws_documentation"
    ARXIV = "arxiv"
    BRAVE_SEARCH = "brave_search"
    DUCKDUCKGO = "duckduckgo"
    HACKERNEWS = "hackernews"

class MultiAgentMode(str, Enum):
    """マルチエージェントモード"""
    COORDINATE = "coordinate"
    COLLABORATE = "collaborate"
    ROUTE = "route"

class AgentType(str, Enum):
    """エージェントタイプ"""
    MCP = "mcp"
    ORIGINAL = "original"

class RequestStatus(str, Enum):
    """リクエスト状態"""
    SUCCESS = "success"
    ERROR = "error"
    PROCESSING = "processing"
    WAITING = "waiting"

class LogLevel(str, Enum):
    """ログレベル"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"