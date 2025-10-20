import api from './api';

export interface LoginAuditRecord {
  id: number;
  user_id?: number;
  username: string;
  login_time: string;
  login_status: string;
  ip_address?: string;
  user_agent?: string;
  device_info?: string;
  location?: string;
}

export const loginAuditService = {
  /**
   * 获取所有登录审计记录（仅管理员）
   */
  async getAllLoginAudits(skip: number = 0, limit: number = 100): Promise<LoginAuditRecord[]> {
    const response = await api.get<LoginAuditRecord[]>('/login-audits', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * 获取当前用户的登录审计记录
   */
  async getMyLoginAudits(skip: number = 0, limit: number = 50): Promise<LoginAuditRecord[]> {
    const response = await api.get<LoginAuditRecord[]>('/login-audits/me', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * 获取指定用户的登录审计记录
   */
  async getUserLoginAudits(userId: number, skip: number = 0, limit: number = 50): Promise<LoginAuditRecord[]> {
    const response = await api.get<LoginAuditRecord[]>(`/login-audits/user/${userId}`, {
      params: { skip, limit }
    });
    return response.data;
  },
};

