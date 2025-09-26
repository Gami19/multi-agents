"""定数定義"""
from typing import Dict, List

# APIレスポンス用定数
API_CONSTANTS = {
    "VERSION": "1.0.0",
    "SERVICE_NAME": "Agno Multi-Agent API",
    "DEFAULT_CORS_ORIGINS": ["http://localhost:3000"],
    "DEFAULT_PORT": 8001,
    "STREAM_HEADERS": {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*"
    }
}

# ログメッセージ定数
LOG_MESSAGES = {
    "INIT_AGENTS": "🚀 Initializing agents...",
    "AGENT_INIT_ERROR": "❌ Failed to initialize agent",
    "STREAM_START": "🚀 Starting stream",
    "STREAM_ERROR": "❌ Stream error",
    "TOOL_CALL": "🔧 Using tool: {}",
    "CHUNK_PREVIEW": "📝 Chunk: {}",
    "TEAM_COMPLETE": "✅ Team complete",
    "ERROR_GENERAL": "❌ Error: {}",
    "REASONING_LOG": "🧠 Reasoning: {}",
    "TOOL_EXECUTION": "⚡ Tool execution: {}"
}

# ツール実行パターン
TOOL_EXECUTION_PATTERN = r'([a-zA-Z_]+\([^)]*\)\s+completed\s+in\s+[\d.]+\s*s\.)'

# 推論キーワード
REASONING_KEYWORDS = [
    "**Initial Analysis**", 
    "**Approach Planning**", 
    "**Information Gathering**", 
    "**Validation**", 
    "**思考**", 
    "**推論**", 
    "**分析**"
]

ANSWER_KEYWORDS = [
    "**Final Synthesis**", 
    "**Answer**", 
    "**Conclusion**", 
    "**回答**", 
    "**結論**"
]

# エラーメッセージ定数
ERROR_MESSAGES = {
    "AGENT_NOT_AVAILABLE": "Agent not available",
    "SYSTEM_NOT_INITIALIZED": "Agent system not initialized",
    "TEAM_NOT_FOUND": "Team not found",
    "VALIDATION_ERROR": "Validation error",
    "REQUEST_ERROR": "Request processing error"
}