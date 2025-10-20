import { create } from 'zustand';
import { User } from '../services/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (token: string, user: User) => void;
  updateUser: (user: User) => void;
  logout: () => void;
  initAuth: () => void;
}

// 从 localStorage 获取初始状态
const getInitialState = () => {
  const token = localStorage.getItem('token');
  const userStr = localStorage.getItem('user');
  
  if (token && userStr) {
    try {
      const user = JSON.parse(userStr);
      return {
        token,
        user,
        isAuthenticated: true,
      };
    } catch (e) {
      // JSON 解析失败，清除无效数据
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  }
  
  return {
    token: null,
    user: null,
    isAuthenticated: false,
  };
};

export const useAuthStore = create<AuthState>((set) => ({
  ...getInitialState(),
  
  setAuth: (token: string, user: User) => {
    // 同时保存到 localStorage 和状态
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(user));
    set({ token, user, isAuthenticated: true });
  },
  
  updateUser: (user: User) => {
    // 更新用户信息
    localStorage.setItem('user', JSON.stringify(user));
    set({ user });
  },
  
  logout: () => {
    // 清除所有认证信息
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    set({ token: null, user: null, isAuthenticated: false });
  },
  
  initAuth: () => {
    // 手动初始化认证状态（用于应用启动时）
    const state = getInitialState();
    set(state);
  },
}));

