import React, { useState, useRef, useCallback } from 'react';
import { Plus, Users, Bot, Trash2, Settings, Info } from 'lucide-react';
import { useChatStore } from '../store/chatStore';
import { CreateAgentModal } from './CreateAgentModal';
import { CreateTeamModal } from './CreateTeamModal';

export const Sidebar: React.FC = () => {
  const [showAgentModal, setShowAgentModal] = useState(false);
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);
  const [sidebarWidth, setSidebarWidth] = useState(320);
  const [isResizing, setIsResizing] = useState(false);
  const sidebarRef = useRef<HTMLDivElement>(null);
  
  const {
    currentSession,
    predefinedAgents,
    predefinedTeams,
    customAgents,
    customTeams,
    setSelectedAgent,
    setSelectedTeam,
    removeCustomAgent,
    removeCustomTeam
  } = useChatStore();

  const allAgents = [...predefinedAgents, ...customAgents];
  const allTeams = [...predefinedTeams, ...customTeams];

  const getTeamMembers = (teamAgentIds: string[]) => {
    return teamAgentIds.map(id => allAgents.find(agent => agent.id === id)).filter(Boolean);
  };

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    e.preventDefault();
  }, []);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const newWidth = e.clientX;
    if (newWidth >= 280 && newWidth <= 600) {
      setSidebarWidth(newWidth);
    }
  }, [isResizing]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    } else {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  return (
    <>
      <aside 
        ref={sidebarRef}
        className="bg-gray-900 border-r border-gray-800 flex flex-col relative"
        style={{ width: `${sidebarWidth}px`, minWidth: '280px', maxWidth: '600px' }}
      >
        <div className="p-4 border-b border-gray-800">
          <h2 className="text-lg font-semibold text-white mb-4">エージェント・チーム選択</h2>
          
          {/* Current Selection Display */}
          <div className="bg-gray-800 rounded-lg p-3 mb-4">
            <div className="text-sm text-gray-400 mb-1">現在アクティブ:</div>
            <div className="text-white font-medium">
              {currentSession.selectedAgent ? (
                <div className="flex items-center space-x-2">
                  <Bot className="h-4 w-4 text-blue-400" />
                  <span>{currentSession.selectedAgent.name}</span>
                </div>
              ) : currentSession.selectedTeam ? (
                <div className="flex items-center space-x-2">
                  <Users className="h-4 w-4 text-purple-400" />
                  <span>{currentSession.selectedTeam.name}</span>
                </div>
              ) : (
                <span className="text-gray-500">選択なし</span>
              )}
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto">
          {/* Individual Agents Section */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300 tracking-wide">
                個別エージェント
              </h3>
              <button
                onClick={() => setShowAgentModal(true)}
                className="p-1 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                title="カスタムエージェントを作成"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
            
            <div className="space-y-2">
              {allAgents.map((agent) => (
                <div
                  key={agent.id}
                  className="relative"
                  onMouseEnter={() => setHoveredAgent(agent.id)}
                  onMouseLeave={() => setHoveredAgent(null)}
                >
                  <div
                    className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                      currentSession.selectedAgent?.id === agent.id
                        ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                        : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                    }`}
                    onClick={() => setSelectedAgent(agent)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2 min-w-0 flex-1">
                        <Bot className="h-4 w-4 text-blue-400 flex-shrink-0" />
                        <div className="min-w-0 flex-1">
                          <div className="text-sm font-medium truncate">{agent.name}</div>
                          <div className="text-xs text-gray-500 truncate">{agent.role}</div>
                        </div>
                      </div>
                      {agent.isCustom && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeCustomAgent(agent.id);
                          }}
                          className="p-1 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                          title="カスタムエージェントを削除"
                        >
                          <Trash2 className="h-3 w-3" />
                        </button>
                      )}
                    </div>
                  </div>
                  
                  {/* ツールチップ */}
                  {hoveredAgent === agent.id && agent.instructions && (
                    <div className="absolute left-full ml-2 top-0 z-50 w-64 p-3 bg-gray-700 border border-gray-600 rounded-lg shadow-lg">
                      <div className="text-sm text-white font-medium mb-2">{agent.name}</div>
                      <div className="text-xs text-gray-300 mb-2">{agent.instructions}</div>
                      {agent.tools.length > 0 && (
                        <div className="text-xs text-gray-400">
                          <span className="font-medium">利用可能ツール:</span> {agent.tools.join(', ')}
                        </div>
                      )}
                      {/* 矢印 */}
                      <div className="absolute left-0 top-4 transform -translate-x-1 w-2 h-2 bg-gray-700 border-l border-t border-gray-600 rotate-45"></div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Teams Section */}
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <h3 className="text-sm font-medium text-gray-300 tracking-wide">
                エージェントチーム
              </h3>
              <button
                onClick={() => setShowTeamModal(true)}
                className="p-1 text-gray-400 hover:text-white hover:bg-gray-800 rounded transition-colors"
                title="カスタムチームを作成"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
            
            <div className="space-y-2">
              {allTeams.map((team) => (
                <div
                  key={team.id}
                  className={`p-3 rounded-lg cursor-pointer transition-all duration-200 group ${
                    currentSession.selectedTeam?.id === team.id
                      ? 'bg-purple-600 text-white shadow-lg shadow-purple-600/20'
                      : 'bg-gray-800 hover:bg-gray-700 text-gray-300'
                  }`}
                  onClick={() => setSelectedTeam(team)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 min-w-0 flex-1">
                      <Users className="h-4 w-4 text-purple-400 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <div className="text-sm font-medium truncate">{team.name}</div>
                        <div className="text-xs text-gray-500 truncate">
                          {team.mode} • {team.agents.length} エージェント
                        </div>
                        {/* チームメンバー表示 */}
                        <div className="text-xs text-gray-400 mt-1">
                          <span className="font-medium">メンバー:</span>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {getTeamMembers(team.agents).map((member, index) => (
                              <span
                                key={member?.id || index}
                                className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-700 text-gray-300"
                              >
                                <Bot className="h-3 w-3 mr-1" />
                                {member?.name || '不明'}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                    {team.isCustom && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeCustomTeam(team.id);
                        }}
                        className="p-1 text-gray-500 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all"
                        title="カスタムチームを削除"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* リサイズハンドル */}
        <div
          className={`absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-blue-500 transition-colors ${
            isResizing ? 'bg-blue-500' : 'bg-transparent'
          }`}
          onMouseDown={handleMouseDown}
          title="サイドバーの幅を調整"
        >
          <div className="absolute top-1/2 right-0 transform -translate-y-1/2 w-3 h-8 bg-gray-600 hover:bg-blue-500 rounded-l-md transition-colors flex items-center justify-center">
            <div className="w-0.5 h-4 bg-gray-400 mx-0.5"></div>
            <div className="w-0.5 h-4 bg-gray-400 mx-0.5"></div>
          </div>
        </div>
      </aside>

      <CreateAgentModal 
        isOpen={showAgentModal} 
        onClose={() => setShowAgentModal(false)} 
      />
      <CreateTeamModal 
        isOpen={showTeamModal} 
        onClose={() => setShowTeamModal(false)} 
      />
    </>
  );
};