import { create } from 'zustand';
import { Agent, Team, ChatSession, Message } from '../types';

interface ChatStore {
  currentSession: ChatSession;
  customAgents: Agent[];
  customTeams: Team[];
  predefinedAgents: Agent[];
  predefinedTeams: Team[];
  
  // Actions
  addMessage: (message: Omit<Message, 'id'> & { id?: string }) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setSelectedAgent: (agent: Agent | undefined) => void;
  setSelectedTeam: (team: Team | undefined) => void;
  toggleReasoningMode: () => void;
  addCustomAgent: (agent: Omit<Agent, 'id' | 'isCustom'>) => void;
  addCustomTeam: (team: Omit<Team, 'id' | 'isCustom'>) => void;
  removeCustomAgent: (id: string) => void;
  removeCustomTeam: (id: string) => void;
}

const defaultPredefinedAgents: Agent[] = [
  {
    id: 'aws-docs',
    name: 'AWS ドキュメント エージェント',
    role: 'AWS エキスパート',
    instructions: 'AWSドキュメントに関するユーザーの依頼を理解し、自律的に情報の取得、検索、推奨を行う',
    tools: ['search', 'documentation'],
    isCustom: false
  },
  {
    id: 'arxiv',
    name: 'Arxiv エージェント',
    role: '論文アシスタント',
    instructions: '学術論文サイト「arXiv」上の論文を自律的に検索し、その内容を取得を行う',
    tools: ['arxiv', 'reasoning'],
    isCustom: false
  }
];

const defaultPredefinedTeams: Team[] = [
  {
    id: 'mcp-route',
    name: 'MCP ルートチーム',
    mode: 'route',
    agents: ['aws-docs', 'arxiv'],
    instructions: '最適なエージェントにクエリをルーティングします',
    isCustom: false
  },
  {
    id: 'mcp-coordinate',
    name: 'MCP コーディネートチーム',
    mode: 'coordinate',
    agents: ['aws-docs', 'arxiv'],
    instructions: '複数のエージェントを連携させて複雑な問題を解決します',
    isCustom: false
  },
  {
    id: 'mcp-collaborate',
    name: 'MCP コラボレーションチーム',
    mode: 'collaborate',
    agents: ['aws-docs', 'arxiv'],
    instructions: 'エージェント同士が協力し、お互いの回答を発展させます',
    isCustom: false
  }
];

export const useChatStore = create<ChatStore>((set, get) => ({
  currentSession: {
    id: 'default',
    messages: [],
    isReasoningEnabled: false
  },
  customAgents: [],
  customTeams: [],
  predefinedAgents: defaultPredefinedAgents,
  predefinedTeams: defaultPredefinedTeams,

  addMessage: (message) => {
    const newMessage: Message = {
      ...message,
      id: message.id || Date.now().toString() + Math.random().toString(36).substr(2, 9)
    };
    
    set((state) => ({
      currentSession: {
        ...state.currentSession,
        messages: [...state.currentSession.messages, newMessage]
      }
    }));
  },

  updateMessage: (id, updates) => {
    set((state) => ({
      currentSession: {
        ...state.currentSession,
        messages: state.currentSession.messages.map(msg =>
          msg.id === id ? { ...msg, ...updates } : msg
        )
      }
    }));
  },

  setSelectedAgent: (agent) => {
    set((state) => ({
      currentSession: {
        ...state.currentSession,
        selectedAgent: agent,
        selectedTeam: undefined
      }
    }));
  },

  setSelectedTeam: (team) => {
    set((state) => ({
      currentSession: {
        ...state.currentSession,
        selectedTeam: team,
        selectedAgent: undefined
      }
    }));
  },

  toggleReasoningMode: () => {
    set((state) => ({
      currentSession: {
        ...state.currentSession,
        isReasoningEnabled: !state.currentSession.isReasoningEnabled
      }
    }));
  },

  addCustomAgent: (agentData) => {
    const newAgent: Agent = {
      ...agentData,
      id: Date.now().toString(),
      isCustom: true
    };
    
    set((state) => ({
      customAgents: [...state.customAgents, newAgent]
    }));
  },

  addCustomTeam: (teamData) => {
    const newTeam: Team = {
      ...teamData,
      id: Date.now().toString(),
      isCustom: true
    };
    
    set((state) => ({
      customTeams: [...state.customTeams, newTeam]
    }));
  },

  removeCustomAgent: (id) => {
    set((state) => ({
      customAgents: state.customAgents.filter(agent => agent.id !== id)
    }));
  },

  removeCustomTeam: (id) => {
    set((state) => ({
      customTeams: state.customTeams.filter(team => team.id !== id)
    }));
  }
}));