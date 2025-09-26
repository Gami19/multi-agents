"""バリデーション関数"""
from typing import Optional
from fastapi import HTTPException
from models.schemas import QueryRequest
from models.enums import AgentServiceType, MultiAgentMode, AgentType
from config.logging_config import get_logger

logger = get_logger(__name__)

def validate_query(query: str, min_length: int = 1, max_length: int = 10000) -> bool:
    """クエリの検証"""
    if not query or not query.strip():
        raise HTTPException(
            status_code=400, 
            detail="クエリが空です"
        )
    
    if len(query.strip()) < min_length:
        raise HTTPException(
            status_code=400,
            detail=f"クエリが短すぎます（最小{min_length}文字）"
        )
    
    if len(query) > max_length:
        raise HTTPException(
            status_code=400,
            detail=f"クエリが長すぎます（最大{max_length}文字）"
        )
    
    return True

def validate_request(request: QueryRequest) -> bool:
    """リクエストの完全な検証"""
    # 基本的なクエリ検証
    validate_query(request.query)
    
    # エージェントサービス型の検証
    try:
        AgentServiceType(request.agent_type.value)
    except ValueError:
        logger.error(f"Invalid agent_type: {request.agent_type}")
        raise HTTPException(
            status_code=400,
            detail=f"無効なエージェントタイプ: {request.agent_type}"
        )
    
    return True

def validate_team_combination(agent_type: AgentType, multi_agent_mode: MultiAgentMode) -> bool:
    """チーム構成の妥当性検証"""
    valid_combinations = [
        (AgentType.MCP, MultiAgentMode.ROUTE),
        (AgentType.MCP, MultiAgentMode.COORDINATE),
        (AgentType.MCP, MultiAgentMode.COLLABORATE),
        (AgentType.ORIGINAL, MultiAgentMode.ROUTE),
        (AgentType.ORIGINAL, MultiAgentMode.COORDINATE),
        (AgentType.ORIGINAL, MultiAgentMode.COLLABORATE),
    ]
    
    combination = (agent_type, multi_agent_mode)
    if combination not in valid_combinations:
        raise HTTPException(
            status_code=400,
            detail=f"無効な組み合わせ: {agent_type}, {multi_agent_mode}"
        )
    
    return True

def validate_reasoning_mode(reasoning_mode: bool, agent_type: AgentType) -> bool:
    """推論モードの妥当性を検証"""
    if reasoning_mode and agent_type not in [AgentType.MCP, AgentType.ORIGINAL]:
        raise HTTPException(
            status_code=400,
            detail="推論モードは現在サポートされているエージェントタイプでのみ利用可能です"
        )
    
    return True