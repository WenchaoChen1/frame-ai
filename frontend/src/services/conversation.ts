import api from './api';
import { Message } from './message';

export interface Conversation {
  id: number;
  user_id: number;
  robot_id?: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ConversationCreate {
  title?: string;
  robot_id?: number;
}

export const conversationService = {
  async getConversations(): Promise<Conversation[]> {
    const response = await api.get<Conversation[]>('/conversations');
    return response.data;
  },

  async getConversation(id: number): Promise<Conversation> {
    const response = await api.get<Conversation>(`/conversations/${id}`);
    return response.data;
  },

  async createConversation(data: ConversationCreate): Promise<Conversation> {
    const response = await api.post<Conversation>('/conversations', data);
    return response.data;
  },

  async deleteConversation(id: number): Promise<void> {
    await api.delete(`/conversations/${id}`);
  },

  async updateTitle(id: number, title: string): Promise<void> {
    await api.patch(`/conversations/${id}/title`, null, {
      params: { title },
    });
  },
};

