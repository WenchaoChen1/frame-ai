/**
 * 批量搜索测试组件
 */
import React, { useState } from 'react';
import { Card, Input, Button, Space, InputNumber, message, Collapse, Typography } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import { batchSearchProducts } from '../services/productRagApi';
import { BatchSearchResponse } from '../types';
import SearchResults from './SearchResults';

const { TextArea } = Input;
const { Panel } = Collapse;
const { Text } = Typography;

const BatchSearchTest: React.FC = () => {
  const [queries, setQueries] = useState('');
  const [topK, setTopK] = useState(10);
  const [loading, setLoading] = useState(false);
  const [batchResponse, setBatchResponse] = useState<BatchSearchResponse | null>(null);

  const handleBatchSearch = async () => {
    // 解析查询词（每行一个）
    const queryList = queries
      .split('\n')
      .map((q) => q.trim())
      .filter((q) => q.length > 0);

    if (queryList.length === 0) {
      message.warning('请输入至少一个查询词');
      return;
    }

    if (queryList.length > 20) {
      message.warning('最多支持20个查询词');
      return;
    }

    setLoading(true);
    try {
      const response = await batchSearchProducts({
        queries: queryList,
        top_k: topK,
      });
      setBatchResponse(response);
      message.success(`批量搜索完成，共 ${queryList.length} 个查询`);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '批量搜索失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Card title="批量召回测试">
        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
          <TextArea
            placeholder="输入多个查询词，每行一个，例如：&#10;安全帽&#10;防护服&#10;安全鞋"
            value={queries}
            onChange={(e) => setQueries(e.target.value)}
            rows={6}
            style={{ width: '100%' }}
          />

          <Space size="middle">
            <Space>
              <span>每个查询返回:</span>
              <InputNumber
                min={1}
                max={100}
                value={topK}
                onChange={(value) => setTopK(value || 10)}
                style={{ width: 100 }}
              />
              <span>个结果</span>
            </Space>
            <Button
              type="primary"
              icon={<SearchOutlined />}
              onClick={handleBatchSearch}
              loading={loading}
            >
              批量搜索
            </Button>
          </Space>

          <div style={{ color: '#666', fontSize: '12px' }}>
            提示：最多支持20个查询词，每个查询词一行
          </div>
        </Space>
      </Card>

      {batchResponse && (
        <Card 
          title={`批量搜索结果 (总耗时: ${batchResponse.total_time_ms.toFixed(2)} ms)`}
          style={{ marginTop: 16 }}
        >
          <Collapse accordion>
            {batchResponse.results.map((result, index) => (
              <Panel
                header={
                  <Space>
                    <Text strong>查询 {index + 1}:</Text>
                    <Text>{result.query}</Text>
                    <Text type="secondary">
                      ({result.total} 个结果, {result.search_time_ms.toFixed(2)} ms)
                    </Text>
                  </Space>
                }
                key={index}
              >
                <SearchResults
                  results={result.results}
                  searchTime={result.search_time_ms}
                  query={result.query}
                />
              </Panel>
            ))}
          </Collapse>
        </Card>
      )}
    </div>
  );
};

export default BatchSearchTest;

