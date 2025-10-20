import { create } from 'zustand';
import { Conversation } from '../services/conversation';
import { Message } from '../services/message';

interface ConversationState {
  conversations: Conversation[];
  currentConversation: Conversation | null;
  messages: Message[];
  isLoading: boolean;
  
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (conversation: Conversation | null) => void;
  setMessages: (messages: Message[] | ((prev: Message[]) => Message[])) => void;
  addMessage: (message: Message) => void;
  updateLastMessage: (content: string) => void;
  setLoading: (loading: boolean) => void;
}

export const useConversationStore = create<ConversationState>((set) => ({
  conversations: [],
  currentConversation: null,
  messages: [],
  isLoading: false,
  
  setConversations: (conversations) => set({ conversations }),
  
  setCurrentConversation: (conversation) => 
    set({ currentConversation: conversation, messages: conversation?.messages || [] }),
  
  setMessages: (messages) => 
    set((state) => ({
      messages: typeof messages === 'function' ? messages(state.messages) : messages
    })),
  
  addMessage: (message) => 
    set((state) => ({ messages: [...state.messages, message] })),
  
  updateLastMessage: (content) =>
    set((state) => {
      const messages = [...state.messages];
      if (messages.length > 0) {
        const lastMessage = messages[messages.length - 1];
        lastMessage.content = content;
      }
      return { messages };
    }),
  
  setLoading: (loading) => set({ isLoading: loading }),
}));

