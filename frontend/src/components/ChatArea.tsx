import React, { useState, useRef, useEffect } from 'react';
import { Send, Brain, Bot, User, Wrench } from 'lucide-react';
import { useChatStore } from '../store/chatStore';
import { apiClient } from '../api/client';

export const ChatArea: React.FC = () => {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const {
    currentSession,
    addMessage,
    updateMessage,
    toggleReasoningMode
  } = useChatStore();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [currentSession.messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message
    addMessage({
      type: 'user',
      content: userMessage,
      timestamp: new Date()
    });

    try {
      const agentId = currentSession.selectedAgent?.id;
      const teamId = currentSession.selectedTeam?.id;

      if (!agentId && !teamId) {
        addMessage({
          type: 'agent',
          content: 'メッセージを送信する前にエージェントまたはチームを選択してください。',
          timestamp: new Date(),
          agentName: 'システム'
        });
        return;
      }

      // Add streaming placeholder
      const responseId = Date.now().toString();
      addMessage({
        id: responseId,
        type: 'agent',
        content: '',
        timestamp: new Date(),
        agentName: currentSession.selectedAgent?.name || currentSession.selectedTeam?.name || 'Agent',
        isStreaming: true
      });

      await apiClient.sendMessage(
        userMessage,
        agentId,
        teamId,
        currentSession.isReasoningEnabled,
        (chunk) => {
          // Handle different chunk types
          if (chunk.type === 'content_chunk') {
            updateMessage(responseId, {
              content: chunk.content,
              isStreaming: true
            });
          } else if (chunk.type === 'reasoning_chunk') {
            addMessage({
              type: 'reasoning',
              content: chunk.content,
              timestamp: new Date(),
              agentName: 'Reasoning Process'
            });
          } else if (chunk.type === 'answer_chunk') {
            updateMessage(responseId, {
              content: chunk.content,
              isStreaming: false
            });
          } else if (chunk.type === 'tool_call') {
            addMessage({
              type: 'tool',
              content: `使用ツール: ${chunk.tool_name}`,
              timestamp: new Date(),
              agentName: 'システム'
            });
          }
        }
      );

    } catch (error) {
      console.error('Error sending message:', error);
      addMessage({
        type: 'agent',
        content: '申し訳ございません。メッセージの処理中にエラーが発生しました。もう一度お試しください。',
        timestamp: new Date(),
        agentName: 'システム'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getMessageIcon = (type: string) => {
    switch (type) {
      case 'user': return <User className="h-4 w-4" />;
      case 'reasoning': return <Brain className="h-4 w-4" />;
      case 'tool': return <Wrench className="h-4 w-4" />;
      default: return <Bot className="h-4 w-4" />;
    }
  };

  const getMessageColors = (type: string) => {
    switch (type) {
      case 'user': 
        return 'bg-blue-600 text-white';
      case 'reasoning': 
        return 'bg-purple-900 text-purple-100 border-l-4 border-purple-500';
      case 'tool': 
        return 'bg-orange-900 text-orange-100 border-l-4 border-orange-500';
      default: 
        return 'bg-gray-800 text-gray-100';
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-gray-950">
      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {currentSession.messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div className="max-w-md">
              <Bot className="h-16 w-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-300 mb-2">
                チャット準備完了
              </h3>
              <p className="text-gray-500">
                サイドバーからエージェントまたはチームを選択して会話を開始してください。
                詳細な思考プロセスを見るには推論モードを有効にしてください。
              </p>
            </div>
          </div>
        ) : (
          currentSession.messages.map((message) => (
            <div key={message.id} className="flex space-x-3">
              <div className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                message.type === 'user' ? 'bg-blue-600' : 
                message.type === 'reasoning' ? 'bg-purple-600' :
                message.type === 'tool' ? 'bg-orange-600' : 'bg-gray-700'
              }`}>
                {getMessageIcon(message.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="text-sm font-medium text-gray-300">
                    {message.type === 'user' ? 'あなた' : message.agentName || 'エージェント'}
                  </span>
                  <span className="text-xs text-gray-500">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                  {message.isStreaming && (
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }} />
                      <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }} />
                    </div>
                  )}
                </div>
                
                <div className={`p-3 rounded-lg ${getMessageColors(message.type)}`}>
                  <div className="whitespace-pre-wrap break-words">
                    {message.content || (message.isStreaming ? '考え中...' : '')}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t border-gray-800 bg-gray-900 p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-start space-x-3">
            <div className="flex-1">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  currentSession.selectedAgent || currentSession.selectedTeam
                    ? "メッセージを入力してください..."
                    : "最初にエージェントまたはチームを選択してください..."
                }
                className="w-full px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                rows={2}
                disabled={(!currentSession.selectedAgent && !currentSession.selectedTeam) || isLoading}
              />
              
              <div className="flex items-center justify-between mt-2">
                <label className="flex items-center space-x-2 text-sm">
                  <input
                    type="checkbox"
                    checked={currentSession.isReasoningEnabled}
                    onChange={toggleReasoningMode}
                    className="rounded bg-gray-700 border-gray-600 text-purple-600 focus:ring-purple-500 focus:ring-offset-gray-900"
                  />
                  <span className="text-gray-300">推論モードを有効にする</span>
                  <Brain className="h-4 w-4 text-purple-400" />
                </label>
                
                <div className="text-xs text-gray-500">
                  Enterで送信、Shift+Enterで改行
                </div>
              </div>
            </div>
            
            <button
              onClick={handleSend}
              disabled={!input.trim() || isLoading || (!currentSession.selectedAgent && !currentSession.selectedTeam)}
              className="px-4 py-3 bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors flex items-center space-x-2"
            >
              <Send className="h-4 w-4" />
              <span className="hidden sm:inline">
                {isLoading ? '送信中...' : '送信'}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};