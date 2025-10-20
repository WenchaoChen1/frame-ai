import api from './api';

export interface KnowledgeBase {
  id: number;
  name: string;
  description?: string;
  vector_store_type: 'elasticsearch' | 'pgvector';
  vector_store_config_id?: number | null;
  embedding_provider: 'openai' | 'claude' | 'ollama';
  embedding_model: string;
  chunk_size: number;
  chunk_overlap: number;
  is_public: boolean;
  user_id: number;
  document_count: number;
  total_chunks: number;
  created_at: string;
  updated_at: string;
}

export interface KnowledgeBaseCreate {
  name: string;
  description?: string;
  vector_store_type?: 'elasticsearch' | 'pgvector';
  vector_store_config_id?: number | null;
  embedding_provider?: 'openai' | 'claude' | 'ollama';
  embedding_model?: string;
  chunk_size?: number;
  chunk_overlap?: number;
  is_public?: boolean;
}

export interface EmbeddingProvider {
  id: string;
  name: string;
  models: EmbeddingModel[];
}

export interface EmbeddingModel {
  id: string;
  name: string;
  description: string;
  dimensions: number;
}

export interface VectorStoreConfig {
  id: number;
  name: string;
  type: string;
  url: string;
  status: string;
}

export interface Document {
  id: number;
  knowledge_base_id: number;
  filename: string;
  file_type: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  chunk_count: number;
  character_count: number;
  uploaded_at: string;
  processed_at?: string;
}

export interface Chunk {
  id: number;
  document_id?: number;
  chunk_index: number;
  content: string;
  character_count: number;
  metadata?: any;
  created_at: string;
}

export interface ChunkListResponse {
  total: number;
  chunks: Chunk[];
}

export interface SearchResult {
  content: string;
  score: number;
  document_id: number;
  document_name: string;
  chunk_index: number;
  metadata?: any;
}

// 获取知识库列表
export const getKnowledgeBases = async (): Promise<KnowledgeBase[]> => {
  const response = await api.get('/knowledge-bases');
  return response.data;
};

// 创建知识库
export const createKnowledgeBase = async (data: KnowledgeBaseCreate): Promise<KnowledgeBase> => {
  const response = await api.post('/knowledge-bases', data);
  return response.data;
};

// 获取知识库详情
export const getKnowledgeBase = async (id: number): Promise<KnowledgeBase> => {
  const response = await api.get(`/knowledge-bases/${id}`);
  return response.data;
};

// 更新知识库
export const updateKnowledgeBase = async (
  id: number,
  data: Partial<KnowledgeBaseCreate>
): Promise<KnowledgeBase> => {
  const response = await api.put(`/knowledge-bases/${id}`, data);
  return response.data;
};

// 删除知识库
export const deleteKnowledgeBase = async (id: number): Promise<void> => {
  await api.delete(`/knowledge-bases/${id}`);
};

// 上传文档
export const uploadDocument = async (kbId: number, file: File): Promise<Document> => {
  const formData = new FormData();
  formData.append('file', file);
  
  // 注意：不要手动设置 Content-Type，让浏览器自动添加 boundary 参数
  const response = await api.post(`/knowledge-bases/${kbId}/documents`, formData);
  return response.data;
};

// 获取文档列表
export const getDocuments = async (kbId: number): Promise<Document[]> => {
  const response = await api.get(`/knowledge-bases/${kbId}/documents`);
  return response.data;
};

// 删除文档
export const deleteDocument = async (docId: number): Promise<void> => {
  await api.delete(`/knowledge-bases/documents/${docId}`);
};

// 获取文档分块列表
export const getDocumentChunks = async (docId: number): Promise<ChunkListResponse> => {
  const response = await api.get(`/knowledge-bases/documents/${docId}/chunks`);
  return response.data;
};

// 批量导入文档
export const batchImportDocuments = async (
  kbId: number,
  directoryPath: string,
  fileExtensions?: string[]
): Promise<any> => {
  const response = await api.post(`/knowledge-bases/${kbId}/batch-import`, {
    directory_path: directoryPath,
    file_extensions: fileExtensions,
  });
  return response.data;
};

// 搜索知识库
export const searchKnowledgeBases = async (
  query: string,
  topK?: number,
  knowledgeBaseIds?: number[]
): Promise<{ query: string; results: SearchResult[]; total: number }> => {
  const response = await api.post('/knowledge-bases/search', {
    query,
    top_k: topK,
    knowledge_base_ids: knowledgeBaseIds,
  });
  return response.data;
};

// 机器人关联知识库
export const associateKnowledgeBases = async (
  robotId: number,
  knowledgeBaseIds: number[]
): Promise<any> => {
  const response = await api.post(`/robots/${robotId}/knowledge-bases`, {
    knowledge_base_ids: knowledgeBaseIds,
  });
  return response.data;
};

// 获取机器人的知识库
export const getRobotKnowledgeBases = async (robotId: number): Promise<any> => {
  const response = await api.get(`/robots/${robotId}/knowledge-bases`);
  return response.data;
};

// 取消机器人与知识库的关联
export const disassociateKnowledgeBase = async (
  robotId: number,
  kbId: number
): Promise<void> => {
  await api.delete(`/robots/${robotId}/knowledge-bases/${kbId}`);
};

// 获取嵌入模型提供商
export const getEmbeddingProviders = async (provider?: string): Promise<{ providers: EmbeddingProvider[] }> => {
  const url = provider ? `/providers/embeddings?provider=${provider}` : '/providers/embeddings';
  const response = await api.get(url);
  return response.data;
};

// 获取向量存储配置
export const getVectorStoreConfigs = async (): Promise<{ vector_stores: VectorStoreConfig[] }> => {
  const response = await api.get('/providers/vector-stores');
  return response.data;
};

