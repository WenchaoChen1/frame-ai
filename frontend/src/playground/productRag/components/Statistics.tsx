/**
 * 统计信息组件
 */
import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Button, message, Popconfirm, Space, Alert } from 'antd';
import {
  ShoppingOutlined,
  DatabaseOutlined,
  ApiOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { getStats, clearAllData } from '../services/productRagApi';
import { StatsResponse } from '../types';

interface StatisticsProps {
  refreshTrigger?: number;
  onDataCleared?: () => void;
}

const Statistics: React.FC<StatisticsProps> = ({ refreshTrigger = 0, onDataCleared }) => {
  const [stats, setStats] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [clearing, setClearing] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const response = await getStats();
      setStats(response);
    } catch (error: any) {
      message.error(error.response?.data?.detail || '获取统计信息失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, [refreshTrigger]);

  const handleClearData = async () => {
    setClearing(true);
    try {
      await clearAllData();
      message.success('数据已清空');
      await fetchStats();
      if (onDataCleared) {
        onDataCleared();
      }
    } catch (error: any) {
      message.error(error.response?.data?.detail || '清空数据失败');
    } finally {
      setClearing(false);
    }
  };

  return (
    <div>
      <Card
        title="统计信息"
        extra={
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchStats}
            loading={loading}
          >
            刷新
          </Button>
        }
      >
        <Row gutter={16}>
          <Col span={6}>
            <Card>
              <Statistic
                title="总商品数"
                value={stats?.total_products || 0}
                prefix={<ShoppingOutlined />}
                loading={loading}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="ES向量总数"
                value={stats?.total_vectors || 0}
                prefix={<DatabaseOutlined />}
                loading={loading}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="ES索引"
                value={stats?.index_name || '-'}
                prefix={<ApiOutlined />}
                loading={loading}
                valueStyle={{ fontSize: '16px' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="嵌入模型"
                value={stats?.embedding_model || '-'}
                loading={loading}
                valueStyle={{ fontSize: '16px' }}
              />
            </Card>
          </Col>
        </Row>

        <div style={{ marginTop: 24 }}>
          <Alert
            message="数据管理"
            description={
              <Space direction="vertical" size="small" style={{ width: '100%' }}>
                <div>
                  数据库中有 {stats?.total_products || 0} 个商品，
                  Elasticsearch 中有 {stats?.total_vectors || 0} 个向量
                </div>
                <div style={{ marginTop: 8 }}>
                  <Popconfirm
                    title="确定要清空所有数据吗？"
                    description="此操作将删除数据库中的商品记录和 Elasticsearch 索引，不可恢复！"
                    onConfirm={handleClearData}
                    okText="确定"
                    cancelText="取消"
                    okButtonProps={{ danger: true }}
                  >
                    <Button
                      danger
                      icon={<DeleteOutlined />}
                      loading={clearing}
                    >
                      清空所有数据
                    </Button>
                  </Popconfirm>
                </div>
              </Space>
            }
            type="info"
            showIcon
          />
        </div>
      </Card>
    </div>
  );
};

export default Statistics;

