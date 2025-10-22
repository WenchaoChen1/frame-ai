/**
 * 单次搜索测试组件
 */
import React, { useState } from 'react';
import { Card, Input, Button, Space, InputNumber, message } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { searchProducts } from '../services/productRagApi';
import { SearchResponse } from '../types';
import SearchResults from './SearchResults';

const SearchTest: React.FC = () => {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      message.warning('请输入查询词');
      return;
    }

    setLoading(true);
    try {
      const response = await searchProducts({
        query: query.trim(),
        top_k: topK,
      });
      setSearchResponse(response);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div>
      <Card title="单次召回测试">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <Space size="middle" style={{ width: '100%' }}>
            <Input
              placeholder="输入查询词，例如：安全帽"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              style={{ width: 400 }}
              prefix={<SearchOutlined />}
            />
            <Space>
              <span>返回结果数:</span>
              <InputNumber
                min={1}
                max={100}
                value={topK}
                onChange={(value) => setTopK(value || 10)}
                style={{ width: 100 }}
              />
            </Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleSearch}
              loading={loading}
            >
              搜索
            </Button>
          </Space>

          <div style={{ color: '#666', fontSize: '12px' }}>
            提示：输入商品相关的关键词，系统将返回最相似的商品列表
          </div>
        </Space>
      </Card>

      {searchResponse && (
        <Card title="搜索结果" style={{ marginTop: 16 }}>
          <SearchResults
            results={searchResponse.results}
            searchTime={searchResponse.search_time_ms}
            query={searchResponse.query}
            loading={loading}
          />
        </Card>
      )}
    </div>
  );
};

export default SearchTest;

