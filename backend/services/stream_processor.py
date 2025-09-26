"""ストリーミング処理サービス"""
from typing import AsyncGenerator
import json
import re
import traceback
from datetime import datetime
from agno.agent import Agent
from agno.tools.reasoning import ReasoningTools

from models.enums import AgentServiceType
from config.logging_config import get_logger

logger = get_logger(__name__)

async def stream_with_debug_logging(
    agent: Agent, 
    query: str, 
    service_type: AgentServiceType, 
    reasoning_mode: bool = False
) -> AsyncGenerator[str, None]:
    """デバッグログ付きストリーミング処理（推論モード対応・改善版）"""
    
    try:
        # 推論モードが有効な場合はReasoningToolsを追加
        if reasoning_mode:
            if hasattr(agent, 'tools') and agent.tools is not None:
                reasoning_tools = ReasoningTools(add_instructions=True)
                agent.tools = agent.tools + [reasoning_tools]
            else:
                agent.tools = [ReasoningTools(add_instructions=True)]
            
            yield f"data: {json.dumps({'type': 'reasoning_mode_active', 'content': 'Reasoning mode activated', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        response = await agent.arun(query, stream=True)
        
        tools_used = []
        debug_info = {"tool_calls": []}
        reasoning_content = ""
        answer_content = ""
        
        # ストリーミングチャンクを処理
        if hasattr(response, '__aiter__'):
            async for chunk in response:
                # チャンク処理とストリーミング送信の両方を行う
                chunk_result = await _process_streaming_chunk(
                    chunk, service_type, tools_used, debug_info, reasoning_content, answer_content, reasoning_mode
                )
                # 辞書から個別の値を取得
                tools_used = chunk_result['tools_used']
                debug_info = chunk_result['debug_info']  
                reasoning_content = chunk_result['reasoning_content']
                answer_content = chunk_result['answer_content']
                
                # ストリーミングデータをフロントエンドに送信
                streaming_data = chunk_result['streaming_response']
                if streaming_data:
                    yield streaming_data

        # 最終完了通知
        completion_data = {
            "type": "completion",
            "tools_used": tools_used,
            "debug_info": debug_info,
            "reasoning_content": reasoning_content,
            "answer_content": answer_content,
            "total_tools": len(tools_used),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(completion_data)}\n\n"
        
        logger.info(f"[{service_type}] Stream completed - Tools: {len(tools_used)}, Reasoning: {len(reasoning_content)} chars")
        
    except Exception as e:
        print(f"❌ [{service_type}] Stream error: {str(e)}")
        traceback.print_exc()
        error_data = {
            "type": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        yield f"data: {json.dumps(error_data)}\n\n"
        raise

async def _process_streaming_chunk(chunk, service_type, tools_used, debug_info, reasoning_content, answer_content, reasoning_mode):
    """ストリーミングチャンクの処理とポンス送信"""
    try:
        streaming_response = ""
        
        # ツール呼び出し処理
        if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
            for tool_call in chunk.tool_calls:
                tool_name = tool_call.get('name', 'Unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'Unknown')
                tool_args = tool_call.get('arguments', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'arguments', {})
                
                print(f" [{service_type}] Using tool: {tool_name}")
                
                tools_used.append({"name": tool_name, "arguments": tool_args})
                debug_info["tool_calls"].append({"name": tool_name, "arguments": tool_args})

        # コンテンツ処理とストリーミング送信
        if hasattr(chunk, 'content') and chunk.content:
            content = chunk.content
            answer_content += content
            
            if content.strip():
                preview = content[:50].replace('\n', ' ')
                print(f" [{service_type}] Chunk: {preview}{'...' if len(content) > 50 else ''}")
                
                # フロントエンドに送信するストリーミングデータ
                chunk_data = {
                    "type": "content_chunk",
                    "content": content,
                    "timestamp": datetime.now().isoformat()
                }
                streaming_response = f"data: {json.dumps(chunk_data)}\n\n"
        
        return {
            'tools_used': tools_used,
            'debug_info': debug_info,
            'reasoning_content': reasoning_content,
            'answer_content': answer_content,
            'streaming_response': streaming_response
        }
        
    except Exception as e:
        logger.error(f"[{service_type}] Error processing chunk: {e}")
        return {
            'tools_used': tools_used,
            'debug_info': debug_info,
            'reasoning_content': reasoning_content,
            'answer_content': answer_content,
            'streaming_response': ""
        }

async def process_chunk(chunk, service_type: AgentServiceType, content_parts: list, tools_used: list, debug_info: dict):
    """ストリーミングチャンクを処理（必要最小限のログ）"""
    try:
        # ツール呼び出し情報のログ
        if hasattr(chunk, 'tool_calls') and chunk.tool_calls:
            for tool_call in chunk.tool_calls:
                tool_name = tool_call.get('name', 'Unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'Unknown')
                tool_args = tool_call.get('arguments', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'arguments', {})
                
                print(f"�� [{service_type}] Using tool: {tool_name}")
                
                tools_used.append({"name": tool_name, "arguments": tool_args})
                debug_info["tool_calls"].append({"name": tool_name, "arguments": tool_args})
        
        # コンテンツのチャンク表示
        if hasattr(chunk, 'content') and chunk.content:
            content_parts.append(chunk.content)
            if len(chunk.content) > 0:
                preview = chunk.content[:50].replace('\n', ' ')
                print(f"�� [{service_type}] Chunk: {preview}{'...' if len(chunk.content) > 50 else ''}")
                
    except Exception as e:
        logger.error(f"[{service_type}] Error processing chunk: {e}")

async def process_response(response, service_type: AgentServiceType, content_parts: list, tools_used: list, debug_info: dict):
    """通常のレスポンスを処理（必要最小限のログ）"""
    try:
        # ツール呼び出し情報の処理
        if hasattr(response, 'tool_calls') and response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('name', 'Unknown') if isinstance(tool_call, dict) else getattr(tool_call, 'name', 'Unknown')
                tool_args = tool_call.get('arguments', {}) if isinstance(tool_call, dict) else getattr(tool_call, 'arguments', {})
                
                print(f"🔧 [{service_type}] Using tool: {tool_name}")
                tools_used.append({"name": tool_name, "arguments": tool_args})
                debug_info["tool_calls"].append({"name": tool_name, "arguments": tool_args})
        
        # コンテンツの処理
        if hasattr(response, 'content'):
            content_parts.append(str(response.content))
            
    except Exception as e:
        logger.error(f"[{service_type}] Error processing response: {e}")