/**
 * 商品RAG API服务
 */
import api from '../../../services/api';
import {
  ProductListResponse,
  SearchRequest,
  SearchResponse,
  BatchSearchRequest,
  BatchSearchResponse,
  StatsResponse,
  IndexListResponse,
} from '../types';

const BASE_URL = '/product-rag';

/**
 * 上传商品JSON文件
 */
export const uploadProductFile = async (file: File, indexName?: string) => {
  const formData = new FormData();
  formData.append('file', file);

  const params: Record<string, string> = {};
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.post(`${BASE_URL}/upload`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    params,
  });

  return response.data;
};

/**
 * 获取商品列表
 */
export const getProducts = async (
  page: number = 1,
  pageSize: number = 20,
  indexName?: string
): Promise<ProductListResponse> => {
  const params: Record<string, any> = {
    page,
    page_size: pageSize,
  };
  
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.get(`${BASE_URL}/products`, {
    params,
  });

  return response.data;
};

/**
 * 单次搜索
 */
export const searchProducts = async (
  request: SearchRequest,
  indexName?: string
): Promise<SearchResponse> => {
  const params: Record<string, string> = {};
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.post(`${BASE_URL}/search`, request, {
    params,
  });
  return response.data;
};

/**
 * 批量搜索
 */
export const batchSearchProducts = async (
  request: BatchSearchRequest,
  indexName?: string
): Promise<BatchSearchResponse> => {
  const params: Record<string, string> = {};
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.post(`${BASE_URL}/batch-search`, request, {
    params,
  });
  return response.data;
};

/**
 * 获取统计信息
 */
export const getStats = async (indexName?: string): Promise<StatsResponse> => {
  const params: Record<string, string> = {};
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.get(`${BASE_URL}/stats`, {
    params,
  });
  return response.data;
};

/**
 * 清空所有数据
 */
export const clearAllData = async (indexName?: string) => {
  const params: Record<string, string> = {};
  if (indexName) {
    params.index_name = indexName;
  }

  const response = await api.delete(`${BASE_URL}/clear`, {
    params,
  });
  return response.data;
};

/**
 * 获取所有索引列表
 */
export const getAllIndices = async (): Promise<IndexListResponse> => {
  const response = await api.get(`${BASE_URL}/indices`);
  return response.data;
};

/**
 * 删除指定索引
 */
export const deleteIndex = async (indexName: string) => {
  const response = await api.delete(`${BASE_URL}/indices/${indexName}`);
  return response.data;
};

