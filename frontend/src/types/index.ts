export interface Agent {
  id: string;
  name: string;
  role: string;
  instructions: string;
  tools: string[];
  isCustom: boolean;
}

export interface Team {
  id: string;
  name: string;
  mode: 'route' | 'coordinate' | 'collaborate';
  agents: string[];
  instructions: string;
  isCustom: boolean;
}

export interface Message {
  id: string;
  type: 'user' | 'agent' | 'reasoning' | 'tool';
  content: string;
  timestamp: Date;
  agentName?: string;
  isStreaming?: boolean;
}

export interface HealthStatus {
  status: 'healthy' | 'unhealthy' | 'unknown';
  lastChecked: Date;
}

export interface ChatSession {
  id: string;
  selectedAgent?: Agent;
  selectedTeam?: Team;
  messages: Message[];
  isReasoningEnabled: boolean;
}