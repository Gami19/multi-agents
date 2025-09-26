"""推論サービス"""
from typing import List, Dict
from agno.agent import Agent
from models.enums import AgentServiceType

async def create_reasoning_tools(agent_type: AgentServiceType) -> List[Dict]:
    """推論モード用のツールを動的に作成"""
    
    reasoning_tools = [
        {
            "name": "step_by_step_analysis",
            "description": f"Perform step-by-step analysis for {agent_type.value} queries",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "step": {"type": "string", "description": "Current analysis step"},
                    "reasoning": {"type": "string", "description": "Detailed reasoning for this step"},
                    "conclusion": {"type": "string", "description": "Conclusion from this step"}
                },
                "required": ["step", "reasoning"]
            }
        },
        {
            "name": "validate_approach",
            "description": "Validate the current approach and consider alternatives",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "current_approach": {"type": "string", "description": "Description of current approach"},
                    "alternatives": {"type": "array", "items": {"type": "string"}, "description": "Alternative approaches to consider"},
                    "validation": {"type": "string", "description": "Validation of the approach"}
                },
                "required": ["current_approach", "validation"]
            }
        },
        {
            "name": "synthesize_findings",
            "description": "Synthesize multiple findings into a coherent response",
            "inputSchema": {
                "type": "object", 
                "properties": {
                    "findings": {"type": "array", "items": {"type": "string"}, "description": "List of findings to synthesize"},
                    "synthesis": {"type": "string", "description": "Synthesized conclusion"},
                    "confidence": {"type": "string", "enum": ["low", "medium", "high"], "description": "Confidence level"}
                },
                "required": ["findings", "synthesis"]
            }
        }
    ]
    
    return reasoning_tools

async def enhance_agent_with_reasoning(agent: Agent, agent_type: AgentServiceType) -> Agent:
    """エージェントに推論ツールを追加"""
    
    reasoning_tools = await create_reasoning_tools(agent_type)
    
    # 既存のツールに推論ツールを追加
    enhanced_tools = agent.tools + reasoning_tools if hasattr(agent, 'tools') else reasoning_tools
    
    # エージェントのシステムプロンプトを推論モード用に拡張
    reasoning_prompt = f"""
You are now in reasoning mode. Use the provided reasoning tools to:

1. **step_by_step_analysis**: Break down complex problems into manageable steps
2. **validate_approach**: Question your assumptions and consider alternatives  
3. **synthesize_findings**: Combine insights into a coherent response

For {agent_type.value} queries, follow this process:
- First, analyze the query step by step
- Validate your approach and consider alternatives
- Use domain-specific tools as needed
- Finally, synthesize your findings into a clear response

Be thorough in your reasoning and transparent about your thought process.
"""

    # エージェントの設定を更新
    if hasattr(agent, 'instructions'):
        if isinstance(agent.instructions, list):
            agent.instructions.append(reasoning_prompt)
        else:
            agent.instructions = [agent.instructions, reasoning_prompt]
    else:
        agent.instructions = reasoning_prompt
    
    agent.tools = enhanced_tools
    
    return agent