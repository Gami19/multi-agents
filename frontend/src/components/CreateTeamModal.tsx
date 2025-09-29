import React, { useState } from 'react';
import { X, Users } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

interface CreateTeamModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const teamModes = [
  { id: 'route', name: 'ルート', description: '最適なエージェントにクエリをルーティング' },
  { id: 'coordinate', name: 'コーディネート', description: '複数のエージェントを連携して問題解決' },
  { id: 'collaborate', name: 'コラボレーション', description: 'エージェント同士が協力して回答を発展' }
] as const;

export const CreateTeamModal: React.FC<CreateTeamModalProps> = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    mode: 'route' as 'route' | 'coordinate' | 'collaborate',
    agents: [] as string[],
    instructions: ''
  });

  const { addCustomTeam, customAgents, predefinedAgents } = useChatStore();
  const allAgents = [...predefinedAgents, ...customAgents];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && formData.agents.length > 0) {
      addCustomTeam(formData);
      setFormData({ name: '', mode: 'route', agents: [], instructions: '' });
      onClose();
    }
  };

  const toggleAgent = (agentId: string) => {
    setFormData(prev => ({
      ...prev,
      agents: prev.agents.includes(agentId)
        ? prev.agents.filter(id => id !== agentId)
        : [...prev.agents, agentId]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg max-w-md w-full max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-2">
            <Users className="h-6 w-6 text-purple-400" />
            <h2 className="text-xl font-semibold text-white">カスタムチームを作成</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              チーム名 *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="チーム名を入力"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              チームモード *
            </label>
            <div className="space-y-2">
              {teamModes.map((mode) => (
                <label
                  key={mode.id}
                  className="flex items-center p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                >
                  <input
                    type="radio"
                    name="mode"
                    value={mode.id}
                    checked={formData.mode === mode.id}
                    onChange={(e) => setFormData(prev => ({ 
                      ...prev, 
                      mode: e.target.value as 'route' | 'coordinate' | 'collaborate'
                    }))}
                    className="mr-3 text-purple-600 focus:ring-purple-500"
                  />
                  <div className="flex-1">
                    <div className="text-white font-medium">{mode.name}</div>
                    <div className="text-sm text-gray-400">{mode.description}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              エージェントを選択 * ({formData.agents.length} 選択済み)
            </label>
            <div className="space-y-2 max-h-40 overflow-y-auto">
              {allAgents.map((agent) => (
                <label
                  key={agent.id}
                  className="flex items-center p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={formData.agents.includes(agent.id)}
                    onChange={() => toggleAgent(agent.id)}
                    className="mr-3 text-purple-600 focus:ring-purple-500 bg-gray-600 border-gray-500"
                  />
                  <div className="flex-1">
                    <div className="text-white font-medium">{agent.name}</div>
                    <div className="text-sm text-gray-400">{agent.role}</div>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              カスタム指示
            </label>
            <textarea
              value={formData.instructions}
              onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              rows={3}
              placeholder="チーム協働のための追加指示"
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-500 text-white rounded-lg transition-colors"
            >
              キャンセル
            </button>
            <button
              type="submit"
              disabled={formData.agents.length === 0}
              className="flex-1 px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
            >
              チームを作成
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};