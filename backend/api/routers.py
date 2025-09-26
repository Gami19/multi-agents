"""APIエンドポイント管理"""
import json
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from models.schemas import (
    QueryRequest, OriginalAgentRequest, OriginalAgentResponse,
    OriginalTeamRequest, OriginalTeamResponse, DynamicTeamQueryRequest,
    DynamicTeamQueryResponse, AgentTypesInfo, TeamsInfo,
    CustomAgentRequest, CustomAgentResponse, AvailableToolsInfo
)
from models.enums import AgentServiceType
from models.enums import AgentServiceType
from services.agent_manager import agent_manager
from services.stream_processor import stream_with_debug_logging
from agno.tools.reasoning import ReasoningTools

def setup_routes(app: FastAPI):
    """FastAPIアプリケーションにルートを設定"""
    
    @app.get("/")
    async def root():
        """ルートエンドポイント"""
        return {
            "message": "Agno Multi-Agent API is running",
            "version": "1.0.0",
            "available_agents": list(agent_manager.agents.keys()) if agent_manager.initialized else [],
            "endpoints": {
                "health": "/health",
                "aws_documentation": "/aws_documentation/query",
                "arxiv": "/arxiv/query", 
                "brave_search": "/brave_search/query"
            }
        }

    @app.get("/health")
    async def health_check():
        """ヘルスチェックエンドポイント"""
        available_agents = [name for name, agent in agent_manager.agents.items() if agent is not None]
        available_teams = [name for name, team in agent_manager.teams.items() if team is not None]

        agent_status = {}
        for service_type in AgentServiceType:
            if service_type in agent_manager.agents:
                agent_status[service_type] = "available" if agent_manager.agents[service_type] else "unavailable"
            else:
                agent_status[service_type] = "not initialized"
        
        team_status = {}
        for team_key in agent_manager.teams.keys():
            team_status[team_key] = "available" if agent_manager.teams[team_key] else "unavailable"
        
        return {
            "status": "healthy",
            "initialized": agent_manager.initialized,
            "available_agents": available_agents,
            "agent_status": agent_status,
            "available_teams": available_teams,
            "team_status": team_status
        }

    @app.post("/aws_documentation/query")
    async def aws_documentation_query(request: QueryRequest):
        """AWS Documentationエンドポイント"""
        return await _handle_agent_query(
            AgentServiceType.AWS_DOCUMENTATION,
            request,
            "AWS Documentation agent not available"
        )

    @app.post("/arxiv/query")
    async def arxiv_query(request: QueryRequest):
        """ArXivエンドポイント"""
        return await _handle_agent_query(
            AgentServiceType.ARXIV,
            request,
            "ArXiv agent not available"
        )

    @app.post("/brave_search/query")
    async def brave_search_query(request: QueryRequest):
        """Brave Searchエンドポイント"""
        return await _handle_agent_query(
            AgentServiceType.BRAVE_SEARCH,
            request,
            "Brave Search agent not available"
        )

    @app.post("/duckduckgo/query")
    async def duckduckgo_query(request: QueryRequest):
        """DuckDuckGo検索エンドポイント"""
        return await _handle_agent_query(
            AgentServiceType.DUCKDUCKGO,
            request,
            "DuckDuckGo agent not available"
        )

    @app.post("/hackernews/query")
    async def hackernews_query(request: QueryRequest):
        """HackerNewsエンドポイント"""
        return await _handle_agent_query(
            AgentServiceType.HACKERNEWS,
            request,
            "HackerNews agent not available"
        )

    @app.post("/multi_agent/query")
    async def multi_agent_query(request: QueryRequest):
        """マルチエージェントチームエンドポイント"""
        return await _handle_team_query(request)

    @app.get("/team/modes")
    async def get_team_modes():
        """チームモード情報エンドポイント"""
        return {
            "available_modes": [
                {
                    "mode": "route",
                    "name": "Route Mode",
                    "description": "チームリーダーが適切なメンバーにタスクをルーティング",
                    "teams": ["mcp_route", "original_route"]
                },
                {
                    "mode": "coordinate", 
                    "name": "Coordinate Mode",
                    "description": "リーダーがタスクを委譲し、結果を統合",
                    "teams": ["mcp_coordinate", "original_coordinate"]
                },
                {
                    "mode": "collaborate",
                    "name": "Collaborate Mode", 
                    "description": "全メンバーが同じタスクに取り組み、結果を統合",
                    "teams": ["mcp_collaborate", "original_collaborate"]
                }
            ],
            "available_teams": list(agent_manager.teams.keys()) if agent_manager.initialized else []
        }

    @app.post("/original_agents/create", response_model=OriginalAgentResponse)
    async def create_original_agent(request: OriginalAgentRequest):
        """オリジナルエージェント作成エンドポイント"""
        try:
            return await agent_manager.create_original_agent(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/original_agents/available", response_model=AgentTypesInfo)
    async def get_available_original_agents():
        """利用可能なオリジナルエージェントタイプ一覧取得"""
        try:
            return await agent_manager.get_available_original_agent_types()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/original_teams/create", response_model=OriginalTeamResponse)
    async def create_original_team(request: OriginalTeamRequest):
        """オリジナルチーム作成エンドポイント"""
        try:
            return await agent_manager.create_original_team(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/original_teams/available", response_model=TeamsInfo)
    async def get_available_original_teams():
        """利用可能なチーム一覧取得"""
        try:
            return await agent_manager.get_available_original_teams()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/original_teams/{team_key}")
    async def delete_original_team(team_key: str):
        """オリジナルチーム削除エンドポイント"""
        try:
            result = await agent_manager.delete_original_team(team_key)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/dynamic_team/query")
    async def dynamic_team_query(request: DynamicTeamQueryRequest):
        """動的チームクエリ実行エンドポイント"""
        try:
            if not agent_manager.initialized:
                raise HTTPException(status_code=503, detail="Agent system not initialized")
            
            team = agent_manager.get_dynamic_team(request.team_key)
            if not team:
                raise HTTPException(status_code=404, detail=f"Dynamic team {request.team_key} not found")
            
            print(f"�� Dynamic Team Query: {request.query} (Team: {request.team_key}, Reasoning: {request.reasoning_mode})")
            
            # 既存の _handle_team_query と同じストリーミング処理
            return await _handle_dynamic_team_query(request, team)
            
        except Exception as e:
            print(f"❌ Dynamic Team Error: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))


    # ===============================================
    # 完全カスタマイズ機能エンドポイント
    # ===============================================
    
    @app.post("/custom_agents/create", response_model=CustomAgentResponse)
    async def create_custom_agent(request: CustomAgentRequest):
        """完全カスタマイズ可能なエージェント作成エンドポイント"""
        try:
            return await agent_manager.create_custom_agent(request)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/custom_agents/tools")
    async def get_available_tools():
        """利用可能ツール一覧取得エンドポイント"""
        try:
            return await agent_manager.get_available_tools()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete("/original_teams/{team_key}")
    async def delete_original_team(team_key: str):
        """オリジナルチーム削除エンドポイント"""
        try:
            result = await agent_manager.delete_original_team(team_key)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

async def _handle_agent_query(service_type: AgentServiceType, request: QueryRequest, error_message: str):
    """個別エージェントクエリの共通処理"""
    try:
        agent = agent_manager.agents.get(service_type)
        if not agent:
            raise HTTPException(status_code=503, detail=error_message)
        
        print(f"🚀 [{service_type}] Query: {request.query} (Reasoning mode: {request.reasoning_mode})")
        
        return StreamingResponse(
            stream_with_debug_logging(agent, request.query, service_type, request.reasoning_mode),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
    except Exception as e:
        print(f"❌ [{service_type}] Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _handle_team_query(request: QueryRequest):
    """マルチエージェントクエリの処理"""
    try:
        if not agent_manager.initialized:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        # チームキーの決定
        team_key = f"{request.agent_type.value}_{request.multi_agent_mode.value}"
        team = agent_manager.get_team(team_key)
        
        if not team:
            raise HTTPException(status_code=404, detail=f"Team {team_key} not found")
        
        print(f"🚀 Multi-Agent Query: {request.query} (Team: {team_key}, Reasoning: {request.reasoning_mode})")
        
        async def stream_team_response():
            try:
                # 推論モードの場合はチームにReasoningToolsを追加
                if request.reasoning_mode:
                    if hasattr(team, 'tools') and team.tools is not None:
                        team.tools = team.tools + [ReasoningTools(add_instructions=True)]
                    else:
                        team.tools = [ReasoningTools(add_instructions=True)]
                
                # チームのレスポンスをストリーミング
                response = await team.arun(request.query, stream=True)
                
                tools_used = []
                debug_info = {"tool_calls": []}
                reasoning_text = ""
                answer_text = ""
                
                if hasattr(response, '__aiter__'):
                    async for chunk in response:
                        # チームチャンクの処理
                        async for data_line in _process_team_chunk(
                            chunk, team_key, request.reasoning_mode,
                            tools_used, debug_info, reasoning_text, answer_text
                        ):
                            yield data_line

                # 完了通知
                completion_data = {
                    "type": "completion",
                    "tools_used": tools_used,
                    "debug_info": debug_info,
                    "mode_used": team_key,
                    "reasoning_content": reasoning_text,
                    "answer_content": answer_text,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(completion_data)}\n\n"
                
                print(f"✅ [Team: {team_key}] Complete")
                
            except Exception as e:
                print(f"❌ [Team: {team_key}] Error: {str(e)}")
                error_data = {
                    "type": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            stream_team_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*"
            }
        )
        
    except Exception as e:
        print(f"❌ Multi-Agent Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _handle_dynamic_team_query(request: DynamicTeamQueryRequest, team):
    """動的チームクエリのストリーミング処理"""
    async def stream_dynamic_team_response():
        try:
            # 推論モードの場合はチームにReasoningToolsを追加
            if request.reasoning_mode:
                if hasattr(team, 'tools') and team.tools is not None:
                    team.tools = team.tools + [ReasoningTools(add_instructions=True)]
                else:
                    team.tools = [ReasoningTools(add_instructions=True)]
            
            # チームのレスポンスをストリーミング
            response = await team.arun(request.query, stream=True)
            
            tools_used = []
            debug_info = {"tool_calls": []}
            reasoning_text = ""
            answer_text = ""
            
            if hasattr(response, '__aiter__'):
                async for chunk in response:
                    # チームチャンクの処理
                    async for data_line in _process_team_chunk(
                        chunk, request.team_key, request.reasoning_mode,
                        tools_used, debug_info, reasoning_text, answer_text
                    ):
                        yield data_line

            # 完了通知
            completion_data = {
                "type": "completion",
                "tools_used": tools_used,
                "debug_info": debug_info,
                "mode_used": request.team_key,
                "reasoning_content": reasoning_text,
                "answer_content": answer_text,
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(completion_data)}\n\n"
            
            print(f"✅ [Dynamic Team: {request.team_key}] Complete")
            
        except Exception as e:
            print(f"❌ [Dynamic Team: {request.team_key}] Error: {str(e)}")
            error_data = {
                "type": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
    
    return StreamingResponse(
        stream_dynamic_team_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
    )


# チームストリーミング処理のヘルパー関数
async def _process_team_chunk(chunk, team_key, reasoning_mode, tools_used, debug_info, reasoning_text, answer_text):
    """チームチャンクの処理（完全版）"""
    if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
        for tool_call in chunk.tool_calls:
            tool_name = tool_call.get('name', 'Unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'Unknown')
            tool_args = tool_call.get('arguments', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'arguments', {})
            
            print(f"🔧 [Team: {team_key}] Using tool: {tool_name}")
            
            tools_used.append({"name": tool_name, "arguments": tool_args})
            debug_info["tool_calls"].append({"name": tool_name, "arguments": tool_args})
            
            # ReasoningToolsの場合は特別な処理
            if tool_name == 'think' or tool_name == 'reasoning':
                if tool_args:
                    reasoning_text = f" 推論: {tool_args.get('thought', tool_args.get('reasoning', '思考中...'))}"
                    if 'title' in tool_args:
                        reasoning_text = f"🤔 {tool_args['title']}: {tool_args.get('thought', tool_args.get('reasoning', '思考中...'))}"
                    if 'confidence' in tool_args:
                        reasoning_text += f" (信頼度: {tool_args['confidence']})"
                    
                    reasoning_data = {
                        'type': 'reasoning_chunk',
                        'content': reasoning_text,
                        'timestamp': datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(reasoning_data)}\n\n"
            else:
                tool_reasoning = f" ツール実行: {tool_name}"
                if tool_args:
                    tool_reasoning += f"\n   引数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}"
                tool_reasoning += "\n"
                
                reasoning_data = {
                    'type': 'reasoning_chunk',
                    'content': tool_reasoning,
                    'timestamp': datetime.now().isoformat()
                }
                yield f"data: {json.dumps(reasoning_data)}\n\n"
    
    # AgnoのRunContentEvent固有の推論内容を処理
    if hasattr(chunk, 'reasoning_content') and chunk.reasoning_content:
        reasoning_text += str(chunk.reasoning_content)
        reasoning_data = {
            "type": "reasoning_chunk",
            "content": str(chunk.reasoning_content),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(reasoning_data)}\n\n"
    
    # AgnoのReasoningStepEvent固有の推論ステップを処理
    if hasattr(chunk, 'reasoning_steps') and chunk.reasoning_steps:
        for step in chunk.reasoning_steps:
            if isinstance(step, dict):
                step_content = step.get('content', str(step))
            else:
                step_content = str(step)
            
            reasoning_text += f"🤔 推論ステップ: {step_content}\n"
            
            reasoning_data = {
                "type": "reasoning_chunk",
                "content": f"🤔 推論ステップ: {step_content}",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(reasoning_data)}\n\n"
    
    # AgnoのReasoningStepEvent固有の推論メッセージを処理
    if hasattr(chunk, 'reasoning_messages') and chunk.reasoning_messages:
        for msg in chunk.reasoning_messages:
            if isinstance(msg, dict):
                msg_content = msg.get('content', str(msg))
            else:
                msg_content = str(msg)
            
            reasoning_text += f"💭 推論メッセージ: {msg_content}\n"
            
            reasoning_data = {
                "type": "reasoning_chunk",
                "content": f"💭 推論メッセージ: {msg_content}",
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(reasoning_data)}\n\n"
    
    # コンテンツの処理（RunContentEvent固有のcontent）
    if hasattr(chunk, 'content') and chunk.content:
        content = chunk.content
        
        # ツール実行ログを抽出
        tool_execution_pattern = r'([a-zA-Z_]+\([^)]*\)\s+completed\s+in\s+[\d.]+\s*s\.)'
        tool_executions = re.findall(tool_execution_pattern, content)
        
        # ツール実行ログを推論として送信
        for tool_execution in tool_executions:
            tool_reasoning = f"⚡ {tool_execution}\n"
            reasoning_text += tool_reasoning
            
            reasoning_data = {
                'type': 'reasoning_chunk',
                'content': tool_reasoning,
                'timestamp': datetime.now().isoformat()
            }
            yield f"data: {json.dumps(reasoning_data)}\n\n"
        
        # ツール実行ログを除去してクリーンなコンテンツを作成
        clean_content = re.sub(tool_execution_pattern, '', content)
        
        # 空でない場合のみ送信
        if clean_content.strip():
            preview = clean_content[:50].replace('\n', ' ')
            print(f" [Team: {team_key}] Chunk: {preview}{'...' if len(clean_content) > 50 else ''}")
            
            # 推論モードの場合は推論と回答を区別
            if reasoning_mode:
                reasoning_keywords = ["**Initial Analysis**", "**Approach Planning**", "**Information Gathering**", "**Validation**", "**思考**", "**推論**", "**分析**"]
                answer_keywords = ["**Final Synthesis**", "**Answer**", "**Conclusion**", "**回答**", "**結論**"]
                
                if any(keyword in clean_content for keyword in reasoning_keywords):
                    reasoning_text += clean_content + "\n"
                    reasoning_data = {
                        "type": "reasoning_chunk",
                        "content": clean_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(reasoning_data)}\n\n"
                elif any(keyword in clean_content for keyword in answer_keywords):
                    answer_text += clean_content
                    answer_data = {
                        "type": "answer_chunk",
                        "content": clean_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(answer_data)}\n\n"
                else:
                    answer_text += clean_content
                    answer_data = {
                        "type": "answer_chunk",
                        "content": clean_content,
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"data: {json.dumps(answer_data)}\n\n"
            else:
                answer_text += clean_content
                answer_data = {
                    "type": "answer_chunk",
                    "content": clean_content,
                    "timestamp": datetime.now().isoformat()
                }
                yield f"data: {json.dumps(answer_data)}\n\n"