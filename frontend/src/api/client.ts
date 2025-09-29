import { Message } from '../types';

export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  async checkHealth(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }

  async sendMessage(
    content: string,
    agentId?: string,
    teamId?: string,
    reasoning: boolean = false,
    onChunk?: (chunk: any) => void
  ): Promise<void> {
    const endpoint = agentId 
      ? `/agents/${agentId}/chat${reasoning ? '/reasoning' : ''}`
      : `/teams/${teamId}/chat${reasoning ? '/reasoning' : ''}`;

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query: content })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Handle streaming response
    if (response.headers.get('content-type')?.includes('text/event-stream')) {
      const eventSource = new EventSource(`${this.baseUrl}${endpoint}`);
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onChunk?.(data);
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      eventSource.onerror = () => {
        eventSource.close();
      };

      return;
    }

    // Handle regular response
    const data = await response.json();
    onChunk?.(data);
  }

  async getAgents() {
    const response = await fetch(`${this.baseUrl}/agents`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }

  async getTeams() {
    const response = await fetch(`${this.baseUrl}/teams`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  }
}

export const apiClient = new ApiClient();