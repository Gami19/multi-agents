"""カスタムバリデーター定義"""
from pydantic import validator
from typing import Any

class QueryValidator:
    """クエリバリデーター"""
    
    @staticmethod
    def validate_query_length(query: str) -> str:
        """クエリの長さを検証"""
        if len(query.strip()) < 2:
            raise ValueError("クエリが短すぎます")
        if len(query) > 10000:
            raise ValueError("クエリが長すぎます")
        return query.strip()
    
    @staticmethod
    def validate_reasoning_mode(mode: bool) -> bool:
        """推論モードの検証"""
        return mode

class ModelValidator:
    """モデルバリデーター"""
    
    @staticmethod
    def validate_agent_service_consistency(
        agent_type: str,
        multi_agent_mode: str
    ) -> bool:
        """エージェントサービスとモードの一貫性検証"""
        valid_combinations = {
            ("mcp", "route"): True,
            ("mcp", "coordinate"): True,
            ("mcp", "collaborate"): True,
            ("original", "route"): True,
            ("original", "coordinate"): True,
            ("original", "collaborate"): True,
        }
        
        return valid_combinations.get((agent_type, multi_agent_mode), False)