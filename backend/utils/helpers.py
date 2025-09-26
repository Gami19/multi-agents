"""汎用ヘルパー関数"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi.responses import StreamingResponse
from models.enums import AgentServiceType
from config.logging_config import get_logger

logger = get_logger(__name__)

def format_response(data: Dict[str, Any], response_type: str = "answer") -> str:
    """レスポンスをJSONストリーミング形式にフォーマット"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def log_service_message(service_type: AgentServiceType, message: str, level: str = "info") -> None:
    """サービス固有のメッセージをログ出力"""
    formatted_message = f"[{service_type}] {message}"
    if level == "error":
        logger.error(formatted_message)
    elif level == "warning":
        logger.warning(formatted_message)
    else:
        logger.info(formatted_message)
    print(formatted_message)

def parse_chunk_content(chunk: Any, service_type: AgentServiceType) -> Dict[str, Any]:
    """チャンク内容の解析"""
    result = {
        "tool_calls": [],
        "content": "",
        "reasoning_content": "",
        "reasoning_steps": [],
        "tools": []
    }
    
    try:
        # ツール呼び出し情報の取得
        if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
            result["tool_calls"] = [
                {
                    "name": tool_call.get('name', 'Unknown') if isinstance(tool_call, dict) 
                           else getattr(tool_call, 'name', 'Unknown'),
                    "arguments": tool_call.get('arguments', {}) if isinstance(tool_call, dict)
                               else getattr(tool_call, 'arguments', {})
                }
                for tool_call in chunk.tool_calls
            ]
        
        # 推論内容の取得
        if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
            result["reasoning_content"] = str(chunk.reasoning_content)
            
        if hasattr(chunk, 'reasoning_steps') and chunk.reasoning_steps:
            result["reasoning_steps"] = [
                step.get('content', str(step)) if isinstance(step, dict) else str(step)
                for step in chunk.reasoning_steps
            ]
        
        # コンテンツの取得
        if hasattr(chunk, 'content') and chunk.content:
            result["content"] = str(chunk.content)
            
    except Exception as e:
        logger.error(f"Error parsing chunk: {e}")
    
    return result

def clean_agent_response(content: str) -> str:
    """エージェントレスポンスからツール実行ログを除去"""
    pattern = r'([a-zA-Z_]+\([^)]*\)\s+completed\s+in\s+[\d.]+\s*s\.)'
    return re.sub(pattern, '', content).strip()

def is_reasoning_content(content: str) -> bool:
    """推論コンテンツかどうかの判定"""
    reasoning_indicators = [
        "**思考**", "**推論**", "**分析**", "**検討**", "**考察**",
        "**Initial Analysis**", "**Approach Planning**", "**Step**",
        "thinking", "reasoning", "analysis", "approach"
    ]
    return any(indicator in content for indicator in reasoning_indicators)

def is_answer_content(content: str) -> bool:
    """回答コンテンツかどうかの判定"""
    answer_indicators = [
        "**回答**", "**結論**", "**要約**", "**答え**",
        "**Final Answer**", "**Conclusion**", "**Summary**", "**Result**"
    ]
    return any(indicator in content for indicator in answer_indicators)

def generate_timestamp() -> str:
    """ISO形式のタイムスタンプを生成"""
    return datetime.now().isoformat()

def sanitize_log_output(text: str, max_length: int = 50) -> str:
    """ログ用コンテンツの正規化"""
    # 改行を除去、長い文字列を切り捨て
    clean_text = text[:max_length].replace('\n', ' ')
    return clean_text + ("..." if len(text) > max_length else "")

def create_streaming_headers() -> Dict[str, str]:
    """ストリーミングレスポンス用ヘッダーを作成"""
    from .constants import API_CONSTANTS
    return API_CONSTANTS["STREAM_HEADERS"]

def create_base_response(type: str, content: str, timestamp: str = None) -> Dict[str, Any]:
    """基本レスポンスデータを作成"""
    return {
        "type": type,
        "content": content,
        "timestamp": timestamp or generate_timestamp()
    }

def safe_json_dumps(data: Any, **kwargs) -> str:
    """安全なJSONのシリアライゼーション"""
    try:
        return json.dumps(data, ensure_ascii=False, **kwargs)
    except (TypeError, ValueError) as e:
        logger.error(f"JSON serialization error: {e}")
        return json.dumps({"error": "Serialization failed"})