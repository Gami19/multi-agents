import React, { useState } from 'react';
import { X, Bot } from 'lucide-react';
import { useChatStore } from '../store/chatStore';

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const availableTools = [
  { id: 'duckduckgo', name: 'DuckDuckGo 検索', description: 'ウェブ検索機能' },
  { id: 'arxiv', name: 'ArXiv', description: '学術論文検索' },
  { id: 'hackernews', name: 'HackerNews', description: 'テクノロジーニュースと議論' },
  { id: 'reasoning', name: '推論', description: '高度な推論機能' }
];

export const CreateAgentModal: React.FC<CreateAgentModalProps> = ({ isOpen, onClose }) => {
  const [formData, setFormData] = useState({
    name: '',
    role: '',
    instructions: '',
    tools: [] as string[]
  });

  const { addCustomAgent } = useChatStore();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.name.trim() && formData.role.trim()) {
      addCustomAgent(formData);
      setFormData({ name: '', role: '', instructions: '', tools: [] });
      onClose();
    }
  };

  const toggleTool = (toolId: string) => {
    setFormData(prev => ({
      ...prev,
      tools: prev.tools.includes(toolId)
        ? prev.tools.filter(id => id !== toolId)
        : [...prev.tools, toolId]
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 rounded-lg max-w-md w-full max-h-screen overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-2">
            <Bot className="h-6 w-6 text-blue-400" />
            <h2 className="text-xl font-semibold text-white">カスタムエージェントを作成</h2>
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
              エージェント名 *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="エージェント名を入力"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              役割 *
            </label>
            <input
              type="text"
              value={formData.role}
              onChange={(e) => setFormData(prev => ({ ...prev, role: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="例: 研究アシスタント、コードヘルパー"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              指示
            </label>
            <textarea
              value={formData.instructions}
              onChange={(e) => setFormData(prev => ({ ...prev, instructions: e.target.value }))}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              rows={3}
              placeholder="エージェントの動作と機能を説明してください"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              利用可能なツール
            </label>
            <div className="space-y-2">
              {availableTools.map((tool) => (
                <label
                  key={tool.id}
                  className="flex items-center p-3 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition-colors"
                >
                  <input
                    type="checkbox"
                    checked={formData.tools.includes(tool.id)}
                    onChange={() => toggleTool(tool.id)}
                    className="mr-3 text-blue-600 focus:ring-blue-500 bg-gray-600 border-gray-500"
                  />
                  <div className="flex-1">
                    <div className="text-white font-medium">{tool.name}</div>
                    <div className="text-sm text-gray-400">{tool.description}</div>
                  </div>
                </label>
              ))}
            </div>
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
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors"
            >
              エージェントを作成
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};