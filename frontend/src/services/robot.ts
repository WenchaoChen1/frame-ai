import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface Robot {
  id: number;
  name: string;
  description?: string;
  avatar?: string;
  default_provider: string;
  default_model: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  is_global: boolean;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface DatabaseConfig {
  id: number;
  robot_id: number;
  db_type: 'postgresql' | 'mysql' | 'mssql' | 'databricks' | 'redshift';
  host: string;
  port: number;
  database_name: string;
  username: string;
  created_at: string;
  updated_at: string;
}

export interface DatabaseConfigCreate {
  db_type: 'postgresql' | 'mysql' | 'mssql' | 'databricks' | 'redshift';
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
}

export interface DatabaseTestRequest {
  db_type: 'postgresql' | 'mysql' | 'mssql' | 'databricks' | 'redshift';
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
}

export interface DatabaseTestResponse {
  success: boolean;
  message: string;
}

export interface TableColumn {
  name: string;
  type: string;
  nullable: boolean;
  description?: string;
}

export interface TableSchema {
  name: string;
  columns: TableColumn[];
  description?: string;
}

export interface DatabaseSchemaResponse {
  tables: TableSchema[];
}

// 元数据相关接口
export interface ColumnMetadata {
  name: string;
  description?: string;
  selected: boolean;
}

export interface TableMetadata {
  name: string;
  description?: string;
  selected: boolean;
  columns: ColumnMetadata[];
}

export interface DatabaseMetadataCreate {
  tables: TableMetadata[];
}

export interface DatabaseMetadataResponse {
  id: number;
  robot_id: number;
  tables: TableMetadata[];
  created_at: string;
  updated_at: string;
}

export interface RobotCreate {
  name: string;
  description?: string;
  avatar?: string;
  default_provider: string;
  default_model: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  is_global?: boolean;
}

export interface RobotUpdate {
  name?: string;
  description?: string;
  avatar?: string;
  default_provider?: string;
  default_model?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  is_global?: boolean;
}

export interface Conversation {
  id: number;
  user_id: number;
  robot_id?: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export const robotService = {
  // 获取机器人列表
  async getRobots(): Promise<Robot[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 获取机器人详情
  async getRobot(robotId: number): Promise<Robot> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots/${robotId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 创建机器人
  async createRobot(data: RobotCreate): Promise<Robot> {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/api/robots`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // 更新机器人
  async updateRobot(robotId: number, data: RobotUpdate): Promise<Robot> {
    const token = localStorage.getItem('token');
    const response = await axios.put(`${API_URL}/api/robots/${robotId}`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // 删除机器人
  async deleteRobot(robotId: number): Promise<void> {
    const token = localStorage.getItem('token');
    await axios.delete(`${API_URL}/api/robots/${robotId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  // 获取机器人的对话列表
  async getRobotConversations(robotId: number): Promise<Conversation[]> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots/${robotId}/conversations`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 获取机器人的数据库配置
  async getDatabaseConfig(robotId: number): Promise<DatabaseConfig | null> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots/${robotId}/database`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 创建或更新数据库配置
  async createOrUpdateDatabaseConfig(robotId: number, data: DatabaseConfigCreate): Promise<DatabaseConfig> {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/api/robots/${robotId}/database`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // 删除数据库配置
  async deleteDatabaseConfig(robotId: number): Promise<void> {
    const token = localStorage.getItem('token');
    await axios.delete(`${API_URL}/api/robots/${robotId}/database`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
  },

  // 测试数据库连接
  async testDatabaseConnection(robotId: number, data: DatabaseTestRequest): Promise<DatabaseTestResponse> {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/api/robots/${robotId}/database/test`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // 获取数据库结构
  async getDatabaseSchema(robotId: number): Promise<DatabaseSchemaResponse> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots/${robotId}/database/schema`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },

  // 保存数据库元数据（表和字段的选择及描述）
  async saveDatabaseMetadata(robotId: number, data: DatabaseMetadataCreate): Promise<DatabaseMetadataResponse> {
    const token = localStorage.getItem('token');
    const response = await axios.post(`${API_URL}/api/robots/${robotId}/database/metadata`, data, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  },

  // 获取数据库元数据
  async getDatabaseMetadata(robotId: number): Promise<DatabaseMetadataResponse | null> {
    const token = localStorage.getItem('token');
    const response = await axios.get(`${API_URL}/api/robots/${robotId}/database/metadata`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    return response.data;
  },
};

