import React from 'react';
import { Settings, Activity } from 'lucide-react';
import { useHealthCheck } from '../hooks/useHealthCheck';

export const Header: React.FC = () => {
  const healthStatus = useHealthCheck();

  const getHealthColor = () => {
    switch (healthStatus.status) {
      case 'healthy': return 'bg-green-500';
      case 'unhealthy': return 'bg-red-500';
      default: return 'bg-gray-400';
    }
  };

  const getHealthText = () => {
    switch (healthStatus.status) {
      case 'healthy': return 'システム正常';
      case 'unhealthy': return 'システム異常';
      default: return 'ステータス不明';
    }
  };

  return (
    <header className="bg-gray-900 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Activity className="h-8 w-8 text-blue-400" />
            <h1 className="text-2xl font-bold text-white">Agno エージェントチャット</h1>
          </div>
          <div className="hidden md:flex items-center space-x-2 text-sm text-gray-400">
            <span>•</span>
            <span>マルチエージェントプラットフォーム</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 text-sm">
            <div className={`w-2 h-2 rounded-full ${getHealthColor()} animate-pulse`} />
            <span className="text-gray-300 hidden sm:inline">
              {getHealthText()}
            </span>
            <span className="text-gray-500 text-xs hidden md:inline">
              最終確認: {healthStatus.lastChecked.toLocaleTimeString()}
            </span>
          </div>
          
          <button 
            className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            title="設定"
          >
            <Settings className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  );
};