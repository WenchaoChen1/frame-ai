/**
 * 商品RAG类型定义
 */

export interface Product {
  id: string;
  sell_spu_id?: string;
  goods_name: string;
  goods_alias?: string;
  brand_name?: string;
  product_specifications?: string;
  original_data: Record<string, any>;
  created_at: string;
}

export interface ProductListResponse {
  total: number;
  items: Product[];
  page: number;
  page_size: number;
}

export interface SearchRequest {
  query: string;
  top_k: number;
}

export interface SearchResult {
  rank: number;
  product_id: string;
  goods_name: string;
  goods_alias?: string;
  brand_name?: string;
  product_specifications?: string;
  score: number;
  content: string;
}

export interface SearchResponse {
  query: string;
  total: number;
  results: SearchResult[];
  search_time_ms: number;
}

export interface BatchSearchRequest {
  queries: string[];
  top_k: number;
}

export interface BatchSearchResponse {
  results: SearchResponse[];
  total_time_ms: number;
}

export interface StatsResponse {
  total_products: number;
  total_vectors: number;
  index_name: string;
  embedding_model: string;
}

export interface IndexInfo {
  name: string;
  docs_count: number;
  store_size: string;
  health: string;
  status: string;
  created_at?: string;
}

export interface IndexListResponse {
  total: number;
  indices: IndexInfo[];
}

