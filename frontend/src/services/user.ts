import api from './api';
import { User } from './auth';

export interface UserCreateData {
  username: string;
  email: string;
  password: string;
  role?: string;
}

export interface UserUpdateData {
  username?: string;
  email?: string;
  role?: string;
}

export interface UsersResponse {
  users: User[];
  total: number;
}

export interface ProfileUpdateData {
  username?: string;
  email?: string;
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
  confirm_password: string;
}

export interface PasswordResetData {
  new_password: string;
  confirm_password: string;
}

export const userService = {
  /**
   * 获取所有用户列表
   */
  async getAllUsers(): Promise<User[]> {
    const response = await api.get<User[]>('/users');
    return response.data;
  },

  /**
   * 获取单个用户信息
   */
  async getUser(id: number): Promise<User> {
    const response = await api.get<User>(`/users/${id}`);
    return response.data;
  },

  /**
   * 创建新用户
   */
  async createUser(data: UserCreateData): Promise<User> {
    const response = await api.post<User>('/users', data);
    return response.data;
  },

  /**
   * 更新用户信息
   */
  async updateUser(id: number, data: UserUpdateData): Promise<User> {
    const response = await api.put<User>(`/users/${id}`, data);
    return response.data;
  },

  /**
   * 删除用户
   */
  async deleteUser(id: number): Promise<void> {
    await api.delete(`/users/${id}`);
  },

  /**
   * 修改用户角色
   */
  async updateUserRole(id: number, role: string): Promise<User> {
    const response = await api.patch<User>(`/users/${id}/role`, { role });
    return response.data;
  },

  /**
   * 修改个人资料
   */
  async updateProfile(data: ProfileUpdateData): Promise<User> {
    const response = await api.put<User>('/users/me/profile', data);
    return response.data;
  },

  /**
   * 修改密码
   */
  async changePassword(data: PasswordChangeData): Promise<void> {
    await api.post('/users/me/change-password', data);
  },

  /**
   * 重置用户密码（管理员）
   */
  async resetPassword(userId: number, data: PasswordResetData): Promise<void> {
    await api.post(`/users/${userId}/reset-password`, data);
  },
};

