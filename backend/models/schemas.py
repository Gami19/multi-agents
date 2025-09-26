"""Pydanticスキーマモデル"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .enums import MultiAgentMode, AgentType

class QueryRequest(BaseModel):
    """クエリリクエストスキーマ"""
    query: str = Field(..., description="ユーザーのクエリ", min_length=1)
    reasoning_mode: Optional[bool] = Field(
        default=False, 
        description="推論モードを使用するかどうか"
    )
    multi_agent_mode: Optional[MultiAgentMode] = Field(
        default=MultiAgentMode.ROUTE,
        description="マルチエージェントモード"
    )
    agent_type: Optional[AgentType] = Field(
        default=AgentType.MCP,
        description="エージェントタイプ"
    )

class QueryResponse(BaseModel):
    """クエリレスポンススキーマ"""
    response: str = Field(..., description="エージェントの応答")
    status: str = Field(default="success", description="処理状態")
    tools_used: Optional[List[Dict[str, Any]]] = Field(
        default=[],
        description="使用されたツール一覧"
    )
    debug_info: Optional[Dict[str, Any]] = Field(
        default={},
        description="デバッグ情報"
    )
    mode_used: Optional[str] = Field(
        default=None,
        description="使用されたモード"
    )

class StreamChunk(BaseModel):
    """ストリーミングチャンクスキーマ"""
    type: str = Field(..., description="チャンクの種類")
    content: str = Field(..., description="チャンク内容")
    timestamp: datetime = Field(default_factory=datetime.now, description="タイムスタンプ")

class ToolExecution(BaseModel):
    """ツール実行スキーマ"""
    name: str = Field(..., description="ツール名")
    arguments: Dict[str, Any] = Field(default={}, description="ツール引数")
    execution_time: Optional[float] = Field(default=None, description="実行時間（秒）")
    result: Optional[str] = Field(default=None, description="実行結果")

class ReasoningStep(BaseModel):
    """推論ステップスキーマ"""
    step: int = Field(..., description="ステップ番号")
    content: str = Field(..., description="ステップ内容")
    confidence: Optional[str] = Field(default=None, description="信頼度")

class TeamModeResponse(BaseModel):
    """チームモード情報レスポンススキーマ"""
    mode: str = Field(..., description="モード名")
    name: str = Field(..., description="モード表示名")
    description: str = Field(..., description="モード説明")
    teams: List[str] = Field(..., description="利用可能チーム一覧")

class OriginalAgentRequest(BaseModel):
    """オリジナルエージェント作成リクエストスキーマ"""
    agent_type: str = Field(..., description="エージェントタイプ (web_researcher, academic_researcher, tech_analyst)")
    name: Optional[str] = Field(None, description="カスタムエージェント名")
    role: Optional[str] = Field(None, description="エージェントの役割")
    instructions: Optional[str] = Field(None, description="カスタム指示")
    custom_tools: Optional[List[str]] = Field(default=[], description="追加ツール")

class OriginalAgentResponse(BaseModel):
    """オリジナルエージェント作成レスポンススキーマ"""
    status: str = Field(..., description="作成状態")
    agent_id: str = Field(..., description="作成されたエージェントのID")
    name: str = Field(..., description="エージェント名")
    role: str = Field(..., description="エージェントの役割")
    tools: List[str] = Field(..., description="利用可能ツール")
    created_at: datetime = Field(default_factory=datetime.now, description="作成時刻")

class OriginalTeamRequest(BaseModel):
    """オリジナルチーム作成リクエストスキーマ"""
    team_mode: str = Field(..., description="チームモード (route, coordinate, collaborate)")
    agent_selections: List[str] = Field(..., description="選択エージェント一覧")
    team_name: Optional[str] = Field(None, description="カスタムチーム名")
    custom_instructions: Optional[List[str]] = Field(default=[], description="カスタム指示")

class OriginalTeamResponse(BaseModel):
    """オリジナルチーム作成レスポンススキーマ"""
    status: str = Field(..., description="作成状態")
    team_key: str = Field(..., description="チームキー")
    team_name: str = Field(..., description="チーム名")
    mode: str = Field(..., description="チームモード")
    members: List[Dict[str, str]] = Field(..., description="チームメンバー")
    created_at: datetime = Field(default_factory=datetime.now, description="作成時刻")

class DynamicTeamQueryRequest(BaseModel):
    """動的チームクエリリクエストスキーマ"""
    query: str = Field(..., description="ユーザーのクエリ", min_length=1)
    team_key: str = Field(..., description="チームキー")
    reasoning_mode: Optional[bool] = Field(default=False, description="推論モード")

class DynamicTeamQueryResponse(BaseModel):
    """動的チームクエリレスポンススキーマ"""
    status: str = Field(default="success", description="処理状態")
    team_key: str = Field(..., description="使用したチームキー")
    mode: str = Field(..., description="使用したモード")
    execution_time: Optional[float] = Field(default=None, description="実行時間")
    timestamp: datetime = Field(default_factory=datetime.now, description="実行時刻")

class AgentTypesInfo(BaseModel):
    """利用可能エージェントタイプ情報スキーマ"""
    agent_types: List[Dict[str, str]] = Field(..., description="利用可能エージェントタイプ一覧")
    descriptions: Dict[str, str] = Field(..., description="各タイプの説明")

class TeamsInfo(BaseModel):
    """利用可能チーム情報スキーマ"""
    dynamic_teams: List[Dict[str, str]] = Field(..., description="動的作成チーム一覧")
    mcp_teams: List[str] = Field(..., description="MCPチーム一覧")
    modes: List[Dict[str, str]] = Field(..., description="利用可能モード一覧")

# ==========================================
# 完全カスタマイズ機能追加
# ==========================================

class CustomAgentRequest(BaseModel):
    """完全カスタマイズ可能なエージェント作成リクエストスキーマ"""
    name: str = Field(..., description="エージェント名")
    role: str = Field(..., description="エージェントの役割・専門分野")
    instructions: str = Field(..., description="エージェントの指示・動作定義")
    tools: List[str] = Field(..., description="使用ツール一覧")
    custom_tools: Optional[List[str]] = Field(default=[], description="追加カスタムツール")
    
    # 任意でテンプレートベースのカスタマイズ
    template: Optional[str] = Field(None, description="テンプレート基礎 (web_researcher, academic_researcher, tech_analyst)")

class CustomAgentResponse(BaseModel):
    """カスタムエージェント作成レスポンススキーマ"""
    status: str = Field(..., description="作成状態")
    agent_id: str = Field(..., description="作成されたエージェントのID")
    name: str = Field(..., description="エージェント名")
    role: str = Field(..., description="エージェントの役割")
    tools: List[str] = Field(..., description="利用可能ツール一覧")
    created_at: datetime = Field(default_factory=datetime.now, description="作成時刻")

class AvailableToolsInfo(BaseModel):
    """利用可能ツール情報スキーマ"""
    tool_name: str = Field(..., description="ツール名")
    description: str = Field(..., description="ツール説明")
    category: str = Field(..., description="ツールカテゴリ")
    example_usage: str = Field(..., description="使用例")

class CustomTeamRequest(BaseModel):
    """カスタムエージェントチーム作成リクエストスキーマ"""
    team_mode: str = Field(..., description="チームモード (route, coordinate, collaborate)")
    agent_selections: List[str] = Field(..., description="選択エージェント一覧")
    team_name: Optional[str] = Field(None, description="カスタムチーム名")
    custom_instructions: Optional[List[str]] = Field(default=[], description="カスタム指示")

class CustomTeamResponse(BaseModel):
    """カスタムチーム作成レスポンススキーマ"""
    status: str = Field(..., description="作成状態")
    team_key: str = Field(..., description="作成されたチームのキー")
    team_name: str = Field(..., description="チーム名")
    mode: str = Field(..., description="チームモード")
    member_count: int = Field(..., description="チームメンバー数")
    members: List[str] = Field(..., description="チームメンバー一覧")
    created_at: datetime = Field(default_factory=datetime.now, description="作成時刻")

class HealthStatus(BaseModel):
    """ヘルスチェックステータススキーマ"""
    status: str = Field(default="healthy", description="サービス状態")
    initialized: bool = Field(..., description="初期化済みかどうか")
    available_agents: List[str] = Field(..., description="利用可能エージェント")
    agent_status: Dict[str, str] = Field(..., description="エージェント状態詳細")
    available_teams: List[str] = Field(..., description="利用可能チーム一覧")
    team_status: Dict[str, str] = Field(..., description="チーム状態詳細")

class ErrorResponse(BaseModel):
    """エラーレスポンススキーマ"""
    error: str = Field(..., description="エラーメッセージ")
    status_code: int = Field(..., description="HTTPステータスコード")
    detail: Optional[str] = Field(default=None, description="詳細情報")
    timestamp: datetime = Field(
        default_factory=datetime.now,
        description="エラー発生時刻"
    )