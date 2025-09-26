"""Agno エージェント管理"""

from __future__ import annotations
from typing import Dict, Optional, List
import os
import platform
import traceback
import uuid
from datetime import datetime

from agno.agent import Agent
from agno.models.aws import AwsBedrock
from agno.tools.mcp import MCPTools
from agno.tools.arxiv import ArxivTools
from agno.team.team import Team
from agno.tools.reasoning import ReasoningTools
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools

from config.settings import get_aws_model
from models.enums import AgentServiceType
from models.schemas import (
    OriginalAgentRequest, OriginalAgentResponse, OriginalTeamRequest, 
    OriginalTeamResponse, AgentTypesInfo, TeamsInfo,
    CustomAgentRequest, CustomAgentResponse
)
from config.logging_config import get_logger

logger = get_logger(__name__)

class AgnoAgentManager:
    """Agno エージェント管理クラス"""
    
    def __init__(self):
        self.mcp_tools: Dict[AgentServiceType, MCPTools] = {}
        self.agents: Dict[AgentServiceType, Agent] = {}
        self.teams: Dict[str, Team] = {}
        # 新機能追加
        self.original_agents: Dict[str, Agent] = {}  # 動的オリジナルエージェント
        self.dynamic_teams: Dict[str, Team] = {}     # 動的チーム
        self.initialized = False
        
        # モデル設定の取得
        self.model = get_aws_model()

    async def initialize_agents(self):
        """各エージェントを初期化"""
        try:
            print("🚀 Initializing agents...")
            
            # AWS Documentation (MCP)
            await self._initialize_mcp_server(
                AgentServiceType.AWS_DOCUMENTATION,
                "python -m awslabs.aws_documentation_mcp_server.server" if platform.system() == "Windows"
                else "uvx awslabs.aws-documentation-mcp-server@latest",
                "AWS Documentation分析を行います。AWS関連の質問に詳細に回答します。"
            )

            # ArXiv (Agnoデフォルトツール)
            await self._initialize_arxiv_agent()

            # Brave Search (Agnoデフォルトツール)
            brave_api_key = os.getenv("BRAVE_API_KEY")
            if brave_api_key:
                await self._initialize_brave_search_agent(brave_api_key)
            else:
                print("⚠️  BRAVE_API_KEY not found, skipping Brave Search agent")

            # MCPチームの初期化
            await self._initialize_mcp_teams()
            
            # DuckDuckGo Agent初期化
            await self._initialize_duckduckgo_agent()
            
            # HackerNews Agent初期化
            await self._initialize_hackernews_agent()

            self.initialized = True
            print(f"✅ Initialized {len(self.agents)} agents and {len(self.teams)} teams")
       
        except Exception as e:
            print(f"❌ Failed to initialize agents: {e}")
            traceback.print_exc()

    async def _initialize_mcp_server(
        self, 
        service_type: AgentServiceType, 
        command: str, 
        instructions: str, 
        env: Optional[Dict] = None
    ):
        """MCPサーバーの初期化"""
        try:
            print(f"📡 Initializing {service_type} (MCP)...")
            
            mcp_tools = MCPTools(command=command, env=env)
            await mcp_tools.connect()
            
            agent = Agent(
                model=self.model,
                tools=[mcp_tools],
                instructions=instructions,
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            self.mcp_tools[service_type] = mcp_tools
            self.agents[service_type] = agent
            
            print(f"✅ {service_type} initialized")

        except Exception as e:
            print(f"❌ Failed to initialize {service_type}: {e}")
            logger.error(f"Error initializing MCP server {service_type}: {e}")

    async def _initialize_arxiv_agent(self):
        """ArXivエージェントの初期化"""
        try:
            print("🔍 Initializing ArXiv agent...")
            
            arxiv_tools = ArxivTools()
            
            agent = Agent(
                model=self.model,
                tools=[arxiv_tools],
                instructions="ArXiv論文の検索・取得・分析を行います。最新の研究論文について詳しく調べることができます。",
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            self.agents[AgentServiceType.ARXIV] = agent
            print("✅ ArXiv agent initialized")

        except Exception as e:
            print(f"❌ Failed to initialize ArXiv agent: {e}")
            logger.error(f"Error initializing ArXiv agent: {e}")

    async def _initialize_brave_search_agent(self, brave_api_key: str):
        """Brave Searchエージェントの初期化（MCPサーバー使用）"""
        try:
            print("🔍 Initializing Brave Search agent (MCP)...")
            
            mcp_tools = MCPTools(
                command="npx -y @modelcontextprotocol/server-brave-search",
                env={
                    "BRAVE_API_KEY": brave_api_key,
                    "PATH": os.environ.get("PATH", "")
                }
            )
            
            await mcp_tools.connect()
            
            agent = Agent(
                model=self.model,
                tools=[mcp_tools],
                instructions="""あなたはBrave Searchを使用してウェブ検索を行うアシスタントです。
                
                以下の指示に従ってください：
                - ユーザーのクエリに対して適切な検索を実行する
                - 検索結果を分析し、有用な情報を提供する
                - 検索結果の信頼性を考慮して回答する
                - 必要に応じて複数の検索を実行して情報を補完する
                - 日本語で回答する""",
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            self.mcp_tools[AgentServiceType.BRAVE_SEARCH] = mcp_tools
            self.agents[AgentServiceType.BRAVE_SEARCH] = agent
            print("✅ Brave Search agent (MCP) initialized")

        except Exception as e:
            print(f"❌ Failed to initialize Brave Search agent (MCP): {e}")
            logger.error(f"Error initializing Brave Search agent: {e}")

    async def _initialize_duckduckgo_agent(self):
        """DuckDuckGo検索エージェントの初期化"""
        try:
            print("🔍 Initializing DuckDuckGo agent...")
            
            duckduckgo_tools = DuckDuckGoTools()
            
            agent = Agent(
                model=self.model,
                tools=[duckduckgo_tools],
                instructions="Web検索と一般情報の調査を行います。DuckDuckGoを使用してインターネット上から最新の情報を検索・分析します。",
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            self.agents[AgentServiceType.DUCKDUCKGO] = agent
            print("✅ DuckDuckGo agent initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize DuckDuckGo agent: {e}")
            logger.error(f"Error initializing DuckDuckGo agent: {e}")

    async def _initialize_hackernews_agent(self):
        """HackerNewsエージェントの初期化"""
        try:
            print("📰 Initializing HackerNews agent...")
            
            hackernews_tools = HackerNewsTools()
            
            agent = Agent(
                model=self.model,
                tools=[hackernews_tools],
                instructions="HackerNewsコミュニティからの技術情報と議論を分析します。最新の技術トレンド、プログラミング話題、イノベーション動向について調査します。",
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            self.agents[AgentServiceType.HACKERNEWS] = agent
            print("✅ HackerNews agent initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize HackerNews agent: {e}")
            logger.error(f"Error initializing HackerNews agent: {e}")

    async def _initialize_mcp_teams(self):
        """MCPチームの初期化"""
        try:
            print("🏗️ Initializing MCP teams...")

            # 利用可能なエージェントをフィルタリング
            available_members = []
            if AgentServiceType.AWS_DOCUMENTATION in self.agents and self.agents[AgentServiceType.AWS_DOCUMENTATION] is not None:
                available_members.append(self.agents[AgentServiceType.AWS_DOCUMENTATION])
                
            if AgentServiceType.ARXIV in self.agents and self.agents[AgentServiceType.ARXIV] is not None:
                available_members.append(self.agents[AgentServiceType.ARXIV])
                
            if AgentServiceType.BRAVE_SEARCH in self.agents and self.agents[AgentServiceType.BRAVE_SEARCH] is not None:
                available_members.append(self.agents[AgentServiceType.BRAVE_SEARCH])

            if AgentServiceType.DUCKDUCKGO in self.agents and self.agents[AgentServiceType.DUCKDUCKGO] is not None:
                available_members.append(self.agents[AgentServiceType.DUCKDUCKGO])

            if AgentServiceType.HACKERNEWS in self.agents and self.agents[AgentServiceType.HACKERNEWS] is not None:
                available_members.append(self.agents[AgentServiceType.HACKERNEWS])

            if not available_members:
                print("⚠️  No MCP agents available for team initialization")
                return
    
            # Route Mode Team (MCP)
            mcp_route_team = Team(
                name="MCP Route Team",
                mode="route",
                model=self.model,
                members=[
                    self.agents[AgentServiceType.AWS_DOCUMENTATION],
                    self.agents[AgentServiceType.ARXIV],
                    self.agents[AgentServiceType.BRAVE_SEARCH]
                ],
                instructions=[
                    "あなたはMCPエージェントのルーターです",
                    "AWS関連の質問はAWS Documentationエージェントに",
                    "学術研究関連はArXivエージェントに", 
                    "Web検索関連はBrave Searchエージェントに振り分けてください",
                    "適切なエージェントが見つからない場合は、最も関連性の高いエージェントを選択してください"
                ],
                show_tool_calls=True,
                markdown=True,
                show_members_responses=True,
                debug_mode=True
            )

            # Coordinate Mode Team (MCP)
            mcp_coordinate_team = Team(
                name="MCP Coordinate Team", 
                mode="coordinate",
                model=self.model,
                members=[
                    self.agents[AgentServiceType.AWS_DOCUMENTATION],
                    self.agents[AgentServiceType.ARXIV],
                    self.agents[AgentServiceType.BRAVE_SEARCH]
                ],
                instructions=[
                    "あなたはMCPエージェントのコーディネーターです",
                    "各エージェントに専門的なタスクを委譲し、結果を統合してください",
                    "AWS Documentationエージェントには技術的な観点を",
                    "ArXivエージェントには学術的な観点を",
                    "Brave Searchエージェントには最新情報の観点を担当させてください"
                ],
                show_tool_calls=True,
                markdown=True,
                show_members_responses=True,
                debug_mode=True
            )

            # Collaborate Mode Team (MCP)
            mcp_collaborate_team = Team(
                name="MCP Collaborate Team",
                mode="collaborate", 
                model=self.model,
                members=[
                    self.agents[AgentServiceType.AWS_DOCUMENTATION],
                    self.agents[AgentServiceType.ARXIV],
                    self.agents[AgentServiceType.BRAVE_SEARCH]
                ],
                instructions=[
                    "あなたはMCPエージェントの協調チームです",
                    "全エージェントが協力して同じ問題に取り組んでください",
                    "各エージェントの専門性を活かしながら、包括的な回答を生成してください",
                    "異なる視点からの分析結果を統合して、多角的な解決策を提示してください"
                ],
                show_tool_calls=True,
                markdown=True,
                show_members_responses=True,
                debug_mode=True
            )

            self.teams["mcp_route"] = mcp_route_team
            self.teams["mcp_coordinate"] = mcp_coordinate_team
            self.teams["mcp_collaborate"] = mcp_collaborate_team
            
            print("✅ MCP teams initialized")
            
        except Exception as e:
            print(f"❌ Failed to initialize MCP teams: {e}")
            logger.error(f"Error initializing MCP teams: {e}")


    async def shutdown(self):
        """MCPサーバーのシャットダウン"""
        for service_type, mcp_tools in self.mcp_tools.items():
            try:
                await mcp_tools.close()
                print(f"✅ {service_type} shutdown")
            except Exception as e:
                print(f"❌ Error shutting down {service_type}: {e}")
                logger.error(f"Error shutting down {service_type}: {e}")

    def get_agent(self, service_type: AgentServiceType) -> Optional[Agent]:
        """エージェントを取得"""
        return self.agents.get(service_type)

    def get_team(self, team_key: str) -> Optional[Team]:
        """チームを取得（標準チームと動的チームの両方を検索）"""
        # まず通常のteamsから検索
        team = self.teams.get(team_key)
        if team:
            return team
        
        # 次に動的チームから検索
        return self.dynamic_teams.get(team_key)

    # ==========================================
    # 動的オリジナルエージェント管理機能
    async def create_original_agent(self, request: OriginalAgentRequest) -> OriginalAgentResponse:
        """オリジナルエージェントの動的作成"""
        try:
            agent_id = str(uuid.uuid4())
            tools = []
            
            # エージェントタイプに基づくツール設定
            if request.agent_type == "web_researcher":
                tools = [DuckDuckGoTools()]
                default_name = "Web Researcher"
                default_role = "Web検索と一般調査の専門家"
                default_instructions = "Web検索を行い、最新の情報を提供します。常に信頼できるソースを含めてください。"
            elif request.agent_type == "academic_researcher":
                tools = [ArxivTools(), DuckDuckGoTools()]
                default_name = "Academic Researcher"
                default_role = "学術研究と論文分析の専門家"
                default_instructions = "学術論文と研究文献を調査し、エビデンスベースの分析を提供します。"
            elif request.agent_type == "tech_analyst":
                tools = [HackerNewsTools(), DuckDuckGoTools()]
                default_name = "Tech Analyst"
                default_role = "技術トレンドとイノベーション分析の専門家"
                default_instructions = "技術コミュニティの動向とイノベーショントレンドを分析します。"
            else:
                raise ValueError(f"Unknown agent type: {request.agent_type}")
            
            # カスタムツールの追加処理
            if request.custom_tools:
                # 将来のカスタムツール拡張用
                pass
            
            # Agent作成
            agent = Agent(
                name=request.name or default_name,
                role=request.role or default_role,
                model=self.model,
                tools=tools,
                instructions=request.instructions or default_instructions,
                add_datetime_to_instructions=True,
                debug_mode=True
            )
            
            # 保存
            self.original_agents[agent_id] = agent
            
            # レスポンス生成
            tool_names = [tool.__class__.__name__ for tool in tools]
                
            response = OriginalAgentResponse(
                status="success",
                agent_id=agent_id,
                name=agent.name,
                role=agent.role,
                tools=tool_names,
                created_at=datetime.now()
            )
            
            print(f"✅ Created original agent: {agent.name} ({agent_id})")
            return response
            
        except Exception as e:
            print(f"❌ Failed to create original agent: {e}")
            logger.error(f"Error creating original agent: {e}")
            raise

    async def create_original_team(self, request: OriginalTeamRequest) -> OriginalTeamResponse:
        """オリジナルチームの動的作成"""
        try:
            team_id = str(uuid.uuid4())
            team_key = f"dynamic_team_{team_id}"
            
            # 選択されたエージェントを取得
            selected_agents = []
            for agent_id in request.agent_selections:
                if agent_id in self.original_agents:
                    selected_agents.append(self.original_agents[agent_id])
                else:
                    raise ValueError(f"Agent {agent_id} not found")
            
            if not selected_agents:
                raise ValueError("No valid agents selected")
            
            # チーム名設定
            team_name = request.team_name or f"Custom {request.team_mode.capitalize()} Team"
            
            # モード別指示生成
            if request.team_mode == "route":
                instructions = [
                    f"あなたは{team_name}のルーターです",
                    "各専門エージェントにタスクを適切に振り分けてください",
                    "最適な専門家を選択して質問に回答してください"
                ]
            elif request.team_mode == "coordinate":
                instructions = [
                    f"あなたは{team_name}のコーディネーターです",
                    "各エージェントに専門的な分析を委譲し、結果を統合してください",
                    "各分野の専門性を活かして包括的な回答を生成してください"
                ]
            elif request.team_mode == "collaborate":
                instructions = [
                    f"あなたは{team_name}の協調チームです",
                    "全エージェントが協力して同じ問題に取り組んでください",
                    "各視点から包括的な分析を行ってください"
                ]
            else:
                raise ValueError(f"Unknown team mode: {request.team_mode}")
            
            # カスタム指示追加
            if request.custom_instructions:
                instructions.extend(request.custom_instructions)
            
            # Team作成
            team = Team(
                name=team_name,
                mode=request.team_mode,
                model=self.model,
                members=selected_agents,
                instructions=instructions,
                show_tool_calls=True,
                markdown=True,
                show_members_responses=True,
                debug_mode=True
            )
            
            # 保存
            self.dynamic_teams[team_key] = team
            
            # メンバー情報生成
            members_info = [
                {"id": agent_id, "name": agent.name, "role": agent.role}
                for agent_id, agent in zip(request.agent_selections, selected_agents)
            ]
            
            response = OriginalTeamResponse(
                status="success",
                team_key=team_key,
                team_name=team_name,
                mode=request.team_mode,
                members=members_info,
                created_at=datetime.now()
            )
            
            print(f"✅ Created original team: {team_name} ({team_key})")
            return response
            
        except Exception as e:
            print(f"❌ Failed to create original team: {e}")
            logger.error(f"Error creating original team: {e}")
            raise

    async def delete_original_team(self, team_key: str) -> dict:
        """オリジナルチームの削除"""
        try:
            if team_key in self.dynamic_teams:
                del self.dynamic_teams[team_key]
                print(f"✅ Deleted original team: {team_key}")
                return {"status": "success", "message": f"Team {team_key} deleted"}
            else:
                raise ValueError(f"Team {team_key} not found")
                
        except Exception as e:
            print(f"❌ Failed to delete original team: {e}")
            logger.error(f"Error deleting original team: {e}")
            raise

    def get_dynamic_team(self, team_key: str) -> Optional[Team]:
        """動的チームを取得"""
        return self.dynamic_teams.get(team_key)

    async def get_available_original_agent_types(self) -> AgentTypesInfo:
        """利用可能なオリジナルエージェントタイプ一覧取得"""
        agent_types = [
            {"type": "web_researcher", "name": "Web Researcher", "description": "Web検索と一般調査の専門家"},
            {"type": "academic_researcher", "name": "Academic Researcher", "description": "学術研究と論文分析の専門家"},
            {"type": "tech_analyst", "name": "Tech Analyst", "description": "技術トレンドとイノベーション分析の専門家"}
        ]
        
        descriptions = {
            "web_researcher": "Web検索を行い、最新の情報を提供します。DuckDuckGoツールを使用して情報を収集します。",
            "academic_researcher": "学術論文と研究文献を調査し、エビデンスベースの分析を提供します。ArXivとWebツールを使用します。",
            "tech_analyst": "技術コミュニティの動向とイノベーショントレンドを分析します。HackerNewsとWebツールを使用します。"
        }
        
        return AgentTypesInfo(
            agent_types=agent_types,
            descriptions=descriptions
        )

    async def get_available_original_teams(self) -> TeamsInfo:
        """利用可能なチーム一覧取得"""
        dynamic_teams = []
        for team_key, team in self.dynamic_teams.items():
            dynamic_teams.append({
                "team_key": team_key,
                "team_name": team.name,
                "mode": team.mode,
                "member_count": str(len(team.members))
            })
        
        mcp_teams = list(self.teams.keys()) if self.teams else []
        
        modes = [
            {"mode": "route", "name": "Route Mode", "description": "チームリーダーがタスクをルーティング"},
            {"mode": "coordinate", "name": "Coordinate Mode", "description": "リーダーがタスクを委譲し結果を統合"},
            {"mode": "collaborate", "name": "Collaborate Mode", "description": "全メンバーが協力してタスクに対処"}
        ]
        
        return TeamsInfo(
            dynamic_teams=dynamic_teams,
            mcp_teams=mcp_teams,
            modes=modes
        )

    # ==========================================
    # 完全カスタマイズ機能追加
    # ==========================================

    async def create_custom_agent(self, request):
        """完全カスタマイズ可能なオリジナルエージェント作成"""
        try:
            agent_id = str(uuid.uuid4())
            tools = []
            
            # ツールマップ（利用可能ツール）
            tool_map = {
                "duckduckgo": DuckDuckGoTools(),
                "arxiv": ArxivTools(), 
                "hackernews": HackerNewsTools(),
                "reasoning": ReasoningTools()
            }
            
            # テンプレートベースの場合
            if getattr(request, 'template', None):
                template_tools = {
                    "web_researcher": [DuckDuckGoTools()],
                    "academic_researcher": [ArxivTools(), DuckDuckGoTools()],
                    "tech_analyst": [HackerNewsTools(), DuckDuckGoTools()]
                }
                tools = template_tools.get(request.template, [])
            
            # ユーザー指定ツールの処理
            if hasattr(request, 'tools') and request.tools:
                tools = []
                for tool_name in request.tools:
                    if tool_name in tool_map:
                        tools.append(tool_map[tool_name])
                    else:
                        print(f"Warning: Unknown tool '{tool_name}'")
            
            # カスタムツールの追加
            if getattr(request, 'custom_tools', None):
                for tool_name in request.custom_tools:
                    if tool_name in tool_map:
                        tools.append(tool_map[tool_name])
            
            # エージェント作成
            agent = Agent(
                name=request.name,
                role=request.role,
                model=self.model,
                tools=tools,
                instructions=request.instructions,
                add_datetime_to_instructions=True,
                show_tool_calls=True,
                debug_mode=True,
                markdown=True
            )
            
            # 保存
            self.original_agents[agent_id] = agent
            
            tool_names = [tool.__class__.__name__ for tool in tools]
            
            response = {
                "status": "success",
                "agent_id": agent_id,
                "name": agent.name,
                "role": agent.role,
                "tools": tool_names,
                "created_at": datetime.now()
            }
            
            print(f"✅ Created custom agent: {agent.name} ({agent_id})")
            return response
            
        except Exception as e:
            print(f"❌ Failed to create custom agent: {e}")
            logger.error(f"Error creating custom agent: {e}")
            raise
    
    async def get_available_tools(self):
        """利用可能ツール一覧を取得"""
        tools = [
            {
                "tool_name": "duckduckgo",
                "description": "Web検索・一般情報検索",
                "category": "search",
                "example_usage": "最新のニュースやトレンド情報を検索"
            },
            {
                "tool_name": "arxiv", 
                "description": "学術論文・研究文献検索",
                "category": "research",
                "example_usage": "学術研究論文や研究動向を調査"
            },
            {
                "tool_name": "hackernews",
                "description": "Hacker News技術情報検索", 
                "category": "tech",
                "example_usage": "技術コミュニティの動向や技術議論を調査"
            },
            {
                "tool_name": "reasoning",
                "description": "論理的推論・分析支援",
                "category": "analysis",
                "example_usage": "複雑な問題の論理的分解と段階的分析"
            }
        ]
        return tools


# エージェントマネージャーのシングルトン インスタンス
agent_manager = AgnoAgentManager()