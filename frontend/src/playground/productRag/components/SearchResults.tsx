/**
 * 搜索结果展示组件
 */
import React from 'react';
import { Table, Tag, Typography, Space } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import { SearchResult } from '../types';

const { Text } = Typography;

interface SearchResultsProps {
  results: SearchResult[];
  searchTime?: number;
  query?: string;
  loading?: boolean;
}

const SearchResults: React.FC<SearchResultsProps> = ({
  results,
  searchTime,
  query,
  loading = false,
}) => {
  const columns: ColumnsType<SearchResult> = [
    {
      title: '排名',
      dataIndex: 'rank',
      key: 'rank',
      width: 70,
      render: (rank: number) => (
        <Tag color={rank <= 3 ? 'gold' : 'default'}>#{rank}</Tag>
      ),
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
      title: '相似度分数',
      dataIndex: 'score',
      key: 'score',
      width: 120,
      render: (score: number) => (
        <Text strong style={{ color: score > 0.8 ? '#52c41a' : '#1890ff' }}>
          {score.toFixed(4)}
        </Text>
      ),
      sorter: (a, b) => b.score - a.score,
    },
  ];

  return (
    <div>
      {query && searchTime !== undefined && (
        <Space style={{ marginBottom: 16 }}>
          <Text type="secondary">
            查询词: <Text strong>{query}</Text>
          </Text>
          <Text type="secondary">|</Text>
          <Text type="secondary">
            找到 {results.length} 个结果
          </Text>
          <Text type="secondary">|</Text>
          <Text type="secondary">
            耗时: {searchTime.toFixed(2)} ms
          </Text>
        </Space>
      )}

      <Table
        columns={columns}
        dataSource={results}
        rowKey={(record) => `${record.product_id}-${record.rank}`}
        loading={loading}
        pagination={false}
        scroll={{ x: 900 }}
      />
    </div>
  );
};

export default SearchResults;

