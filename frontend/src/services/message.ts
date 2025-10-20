import api from './api';

export interface QueryResult {
  columns: string[];
  rows: any[][];
  row_count: number;
}

export interface Message {
  id: number;
  conversation_id: number;
  role: 'user' | 'assistant';
  content: string;
  provider?: string;
  model?: string;
  created_at: string;
  sql_query?: string;
  query_result?: QueryResult;
  needs_database?: boolean;
}

export interface MessageCreate {
  content: string;
  provider: string;
  model: string;
}

export interface StreamEvent {
  type: 'user_message' | 'content' | 'done' | 'error' | 'sql_generated' | 'query_executing' | 'query_result' | 'status' | 'stopped';
  data: any;
}

export const messageService = {
  async getMessages(conversationId: number): Promise<Message[]> {
    const response = await api.get<Message[]>(
      `/conversations/${conversationId}/messages`
    );
    return response.data;
  },

  async sendMessageStream(
    conversationId: number,
    message: MessageCreate,
    onEvent: (event: StreamEvent) => void
  ): Promise<void> {
    const token = localStorage.getItem('token');
    const response = await fetch(
      `/api/conversations/${conversationId}/messages/stream`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(message),
      }
    );

    if (!response.ok) {
      throw new Error('发送消息失败');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('无法读取响应流');
    }

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n\n');

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onEvent(data);
          } catch (e) {
            console.error('解析SSE数据失败:', e);
          }
        }
      }
    }
  },
};

