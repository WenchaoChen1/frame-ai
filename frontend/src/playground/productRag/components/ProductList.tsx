/**
 * 商品列表组件 - 支持向量搜索
 */
import React, { useState, useEffect } from 'react';
import { Table, Card, message, Button, Input, Space, InputNumber, Tag, Select, Drawer, Descriptions } from 'antd';
import { SearchOutlined, DatabaseOutlined } from '@ant-design/icons';
import type { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import { getProducts, searchProducts, getAllIndices } from '../services/productRagApi';
import { Product, SearchResult, IndexInfo } from '../types';

interface ProductListProps {
  indexName?: string;
  refreshTrigger?: number;
  onDataCleared?: () => void;
  onIndexChange?: (indexName: string) => void;
}

const ProductList: React.FC<ProductListProps> = ({ 
  indexName: propIndexName,
  refreshTrigger = 0, 
  onDataCleared,
  onIndexChange
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [searching, setSearching] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [topK, setTopK] = useState(1000);
  const [searchMode, setSearchMode] = useState(false); // 是否处于搜索模式
  const [searchTime, setSearchTime] = useState(0);
  const [totalCount, setTotalCount] = useState(0); // 总商品数，用于计算召回率
  const [indices, setIndices] = useState<IndexInfo[]>([]);
  const [localIndexName, setLocalIndexName] = useState<string>(propIndexName || '');
  const [loadingIndices, setLoadingIndices] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<Product | SearchResult | null>(null);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });

  // 使用本地状态或prop传入的索引名称
  const indexName = propIndexName !== undefined ? propIndexName : localIndexName;

  // 获取所有索引列表
  const fetchIndices = async () => {
    setLoadingIndices(true);
    try {
      const response = await getAllIndices();
      setIndices(response.indices);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取知识库列表失败');
    } finally {
      setLoadingIndices(false);
    }
  };

  const fetchProducts = async (page: number = 1, pageSize: number = 20) => {
    if (!indexName) {
      message.warning('请先选择知识库');
      return;
    }

    setLoading(true);
    try {
      const response = await getProducts(page, pageSize, indexName);
      setProducts(response.items);
      setTotalCount(response.total); // 保存总商品数
      setPagination({
        current: response.page,
        pageSize: response.page_size,
        total: response.total,
      });
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取商品列表失败');
    } finally {
      setLoading(false);
    }
  };

  // 执行向量搜索
  const handleSearch = async () => {
    if (!indexName) {
      message.warning('请先选择知识库');
      return;
    }

    if (!searchQuery.trim()) {
      message.warning('请输入搜索关键词');
      return;
    }

    setSearching(true);
    try {
      const response = await searchProducts({
        query: searchQuery.trim(),
        top_k: topK,
      }, indexName);
      setSearchResults(response.results);
      setSearchMode(true);
      setSearchTime(response.search_time_ms);
      message.success(`找到 ${response.total} 个相似商品，耗时 ${response.search_time_ms.toFixed(2)}ms`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '搜索失败');
    } finally {
      setSearching(false);
    }
  };

  // 清除搜索，返回列表模式
  const handleClearSearch = () => {
    setSearchQuery('');
    setSearchMode(false);
    setSearchResults([]);
    setSearchTime(0);
  };

  // 处理知识库选择变化
  const handleIndexChange = (value: string) => {
    setLocalIndexName(value);
    if (onIndexChange) {
      onIndexChange(value);
    }
    // 清除搜索状态
    handleClearSearch();
  };

  // 处理行点击
  const handleRowClick = (record: Product | SearchResult) => {
    setSelectedProduct(record);
    setDetailDrawerVisible(true);
  };

  useEffect(() => {
    // 初始化时获取索引列表
    fetchIndices();
  }, []);

  useEffect(() => {
    if (!searchMode && indexName) {
      fetchProducts();
    }
  }, [refreshTrigger, searchMode, indexName]);

  // 同步propIndexName到localIndexName
  useEffect(() => {
    if (propIndexName !== undefined && propIndexName !== localIndexName) {
      setLocalIndexName(propIndexName);
    }
  }, [propIndexName]);

  const handleTableChange = (newPagination: TablePaginationConfig) => {
    fetchProducts(newPagination.current || 1, newPagination.pageSize || 20);
  };

  // 列表模式的列定义
  const listColumns: ColumnsType<Product> = [
    {
      title: '商品ID',
      dataIndex: 'id',
      key: 'id',
      width: 180,
      ellipsis: true,
    },
    {
      title: '商品名称',
      dataIndex: 'goods_name',
      key: 'goods_name',
      ellipsis: true,
      width: 300,
    },
    {
      title: '品牌',
      dataIndex: 'brand_name',
      key: 'brand_name',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: '产品规格',
      dataIndex: 'product_specifications',
      key: 'product_specifications',
      ellipsis: true,
      render: (text) => text || '-',
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => new Date(text).toLocaleString('zh-CN'),
    },
  ];

  // 计算召回率（基于召回商品数占总数的比例）
  const calculateRecallRate = (totalResults: number) => {
    if (totalCount === 0) return 0;
    // 召回率 = 当前召回的商品数 / 总商品数
    const recallRate = (totalResults / totalCount) * 100;
    return recallRate;
  };

  // 搜索模式的列定义（包含排名、相似度和召回率）
  const searchColumns: ColumnsType<SearchResult> = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 60,
      fixed: 'left',
      render: (rank) => <Tag color="blue">#{rank}</Tag>,
    },
    {
      title: '相似度',
      dataIndex: 'score',
      key: 'score',
      width: 100,
      render: (score) => (
        <Tag color={score > 0.8 ? 'green' : score > 0.6 ? 'orange' : 'default'}>
          {(score * 100).toFixed(2)}%
        </Tag>
      ),
      sorter: (a, b) => b.score - a.score,
    },
    {
      title: '召回率',
      key: 'recall_rate',
      width: 100,
      render: () => {
        const recallRate = calculateRecallRate(searchResults.length);
        return (
          <Tag color={recallRate > 50 ? 'green' : recallRate > 20 ? 'blue' : 'default'}>
            {recallRate.toFixed(2)}%
          </Tag>
        );
      },
    },
    {
      title: '商品ID',
      dataIndex: 'product_id',
      key: 'product_id',
      width: 180,
      ellipsis: true,
    },
    {
      title: '商品名称',
      dataIndex: 'goods_name',
      key: 'goods_name',
      ellipsis: true,
      width: 300,
    },
    {
      title: '品牌',
      dataIndex: 'brand_name',
      key: 'brand_name',
      width: 120,
      render: (text) => text || '-',
    },
    {
      title: '产品规格',
      dataIndex: 'product_specifications',
      key: 'product_specifications',
      ellipsis: true,
      render: (text) => text || '-',
    },
    {
      title: '匹配内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (text) => text || '-',
    },
  ];

  // 计算总召回率
  const overallRecallRate = totalCount > 0 ? ((searchResults.length / totalCount) * 100).toFixed(2) : '0.00';
  
  const cardTitle = searchMode 
    ? `向量搜索结果 (总计: ${totalCount} 商品，召回: ${searchResults.length} 个，召回率: ${overallRecallRate}%，耗时 ${searchTime.toFixed(2)}ms)`
    : indexName 
      ? `商品列表 - ${indexName} (总计: ${pagination.total})`
      : '商品列表 (请先选择知识库)';

  return (
    <Card 
      title={cardTitle}
      extra={
        <Space>
          {searchMode && (
            <Button onClick={handleClearSearch}>
              返回列表
            </Button>
          )}
        </Space>
      }
    >
      {/* 知识库选择和搜索框 - 统一在一行 */}
      <Space style={{ marginBottom: 16, width: '100%', display: 'flex', flexWrap: 'wrap', gap: '12px' }} size="middle">
        {/* 知识库选择 */}
        <Space size="small">
          <DatabaseOutlined style={{ fontSize: '16px', color: '#1890ff' }} />
          <span style={{ fontWeight: 500 }}>选择知识库:</span>
          <Select
            style={{ width: 300 }}
            placeholder="请选择知识库"
            value={indexName || undefined}
            onChange={handleIndexChange}
            loading={loadingIndices}
            options={indices.map(idx => ({
              label: `${idx.name} (${idx.docs_count} 个商品)`,
              value: idx.name
            }))}
            showSearch
            filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
            }
          />
        </Space>

        {/* 搜索框 */}
        <Input
          placeholder="输入商品关键词进行向量化搜索..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onPressEnter={handleSearch}
          style={{ width: 400 }}
          prefix={<SearchOutlined />}
          disabled={!indexName}
        />
        <InputNumber
          min={1}
          max={1000}
          value={topK}
          onChange={(value) => setTopK(value || 1000)}
          addonBefore="返回结果数:"
          style={{ width: 180 }}
          disabled={!indexName}
        />
        <Button
          type="primary"
          icon={<SearchOutlined />}
          loading={searching}
          onClick={handleSearch}
          disabled={!indexName}
        >
          搜索
        </Button>
      </Space>

      {/* 提示信息 */}
      <div style={{ marginBottom: 16, color: '#666', fontSize: '12px' }}>
        {!indexName ? (
          <span style={{ color: '#ff4d4f' }}>⚠️ 提示: 请先从商品知识库Tab选择一个知识库，或在上传数据时指定知识库名称</span>
        ) : searchMode ? (
          <span>💡 提示: 输入商品相关文字，系统将通过向量相似度匹配最相关的商品列表</span>
        ) : (
          <span>💡 提示: 输入商品名称或关键词，系统将自动向量化并返回最相似的商品列表</span>
        )}
      </div>

      {/* 数据表格 */}
      {searchMode ? (
        <Table
          columns={searchColumns}
          dataSource={searchResults}
          rowKey="product_id"
          loading={searching}
          pagination={false}
          scroll={{ x: 1400, y: 500 }}
          bordered
          size="small"
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            style: { cursor: 'pointer' }
          })}
        />
      ) : (
        <Table
          columns={listColumns}
          dataSource={products}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          scroll={{ x: 1200, y: 500 }}
          bordered
          size="small"
          onRow={(record) => ({
            onClick: () => handleRowClick(record),
            style: { cursor: 'pointer' }
          })}
        />
      )}

      {/* 商品详情抽屉 */}
      <Drawer
        title="商品详情"
        placement="right"
        width={1000}
        onClose={() => setDetailDrawerVisible(false)}
        open={detailDrawerVisible}
      >
        {selectedProduct && (
          <Descriptions bordered column={1} size="small">
            <Descriptions.Item label="商品ID">
              {'product_id' in selectedProduct ? selectedProduct.product_id : selectedProduct.id}
            </Descriptions.Item>
            <Descriptions.Item label="商品名称">
              {selectedProduct.goods_name}
            </Descriptions.Item>
            {selectedProduct.goods_alias && (
              <Descriptions.Item label="商品别名">
                {selectedProduct.goods_alias}
              </Descriptions.Item>
            )}
            {selectedProduct.brand_name && (
              <Descriptions.Item label="品牌">
                {selectedProduct.brand_name}
              </Descriptions.Item>
            )}
            {selectedProduct.product_specifications && (
              <Descriptions.Item label="产品规格">
                {selectedProduct.product_specifications}
              </Descriptions.Item>
            )}
            {'score' in selectedProduct && (
              <>
                <Descriptions.Item label="相似度">
                  <Tag color={selectedProduct.score > 0.8 ? 'green' : selectedProduct.score > 0.6 ? 'orange' : 'default'}>
                    {(selectedProduct.score * 100).toFixed(2)}%
                  </Tag>
                </Descriptions.Item>
                <Descriptions.Item label="排名">
                  <Tag color="blue">#{selectedProduct.rank}</Tag>
                </Descriptions.Item>
                {selectedProduct.content && (
                  <Descriptions.Item label="匹配内容">
                    {selectedProduct.content}
                  </Descriptions.Item>
                )}
              </>
            )}
            {'created_at' in selectedProduct && (
              <Descriptions.Item label="创建时间">
                {new Date(selectedProduct.created_at).toLocaleString('zh-CN')}
              </Descriptions.Item>
            )}
            
            {/* 原始数据 */}
            {'original_data' in selectedProduct && selectedProduct.original_data && (
              <Descriptions.Item label="完整数据" span={1}>
                <pre style={{ 
                  maxHeight: '400px', 
                  overflow: 'auto', 
                  background: '#f5f5f5', 
                  padding: '12px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  margin: 0
                }}>
                  {JSON.stringify(selectedProduct.original_data, null, 2)}
                </pre>
              </Descriptions.Item>
            )}
          </Descriptions>
        )}
      </Drawer>
    </Card>
  );
};

export default ProductList;

