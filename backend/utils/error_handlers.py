"""エラーハンドリング"""
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from config.logging_config import get_logger

logger = get_logger(__name__)

def handle_agno_error(error: Exception, service_type: Optional[str] = None) -> JSONResponse:
    """Agno関連エラーの共通処理"""
    error_message = str(error)
    service_info = f"[{service_type}] " if service_type else ""
    
    # エラーログの書き込み
    logger.error(f"{service_info}Error: {error_message}")
    print(f"❌ {service_info}Error: {error_message}")
    
    # HTTPステータスコードの決定
    if "not available" in error_message.lower():
        status_code = 503
    elif "not found" in error_message.lower():
        status_code = 404
    elif "validation" in error_message.lower():
        status_code = 400
    else:
        status_code = 500
    
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": error_message,
            "error_type": "agno_error",
            "timestamp": datetime.now().isoformat()
        }
    )

def format_error_response(error: str, status_code: int = 500, error_type: str = "api_error") -> Dict[str, Any]:
    """エラーレスポンスの統一フォーマット"""
    return {
        "error": error,
        "status_code": status_code,
        "error_type": error_type,
        "timestamp": datetime.now().isoformat()
    }

def format_streaming_error(error: Exception, service_type: Optional[str] = None) -> str:
    """ストリーミング用エラーレスポンス"""
    from .helpers import format_response
    
    error_data = format_error_response(
        str(error),
        status_code=500,
        error_type="streaming_error"
    )
    
    service_info = f" [{service_type}]" if service_type else ""
    logger.error(f"Streaming error{service_info}: {error}")
    
    return format_response(error_data, "error")

def validate_stream_response(response_data: Dict[str, Any]) -> bool:
    """ストリーミングレスポンスの妥当性を確認"""
    required_fields = ["type", "content", "timestamp"]
    
    for field in required_fields:
        if field not in response_data:
            logger.error(f"Missing required field in stream response: {field}")
            return False
    
    return True