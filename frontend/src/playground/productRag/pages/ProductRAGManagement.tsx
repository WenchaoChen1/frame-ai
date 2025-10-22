/**
 * 商品测试管理页面
 */
import React, { useState } from 'react';
import { Typography, Tabs } from 'antd';
import { DatabaseOutlined, SearchOutlined } from '@ant-design/icons';
import ProductList from '../components/ProductList';
import IndexManagement from '../components/IndexManagement';

const { Title } = Typography;
const { TabPane } = Tabs;

const ProductRAGManagement: React.FC = () => {
  const [refreshTrigger, setRefreshTrigger] = useState(0);
  const [selectedIndexName, setSelectedIndexName] = useState<string>('');
  const [activeTab, setActiveTab] = useState('1');

  const handleUploadSuccess = () => {
    // 触发刷新
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleDataCleared = () => {
    // 触发刷新
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleIndexSelected = (indexName: string) => {
    setSelectedIndexName(indexName);
    // 切换到查询测试Tab
    setActiveTab('2');
  };

  const handleIndexChange = (indexName: string) => {
    setSelectedIndexName(indexName);
  };

  return (
    <div style={{ padding: '16px', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ marginBottom: '12px' }}>
        <Title level={3} style={{ marginBottom: '4px' }}>商品测试</Title>
      </div>

      <div style={{ flex: 1, overflow: 'hidden' }}>
        <Tabs 
          activeKey={activeTab} 
          onChange={setActiveTab}
          style={{ height: '100%' }}
          tabBarStyle={{ marginBottom: 16 }}
        >
          <TabPane
            tab={
              <span>
                <DatabaseOutlined />
                商品知识库
              </span>
            }
            key="1"
          >
            <div style={{ height: 'calc(100vh - 180px)', overflow: 'auto' }}>
              <IndexManagement 
                onIndexSelected={handleIndexSelected}
                onUploadSuccess={handleUploadSuccess}
              />
            </div>
          </TabPane>

          <TabPane
            tab={
              <span>
                <SearchOutlined />
                查询测试
              </span>
            }
            key="2"
          >
            <div style={{ height: 'calc(100vh - 180px)', overflow: 'hidden' }}>
              <ProductList 
                indexName={selectedIndexName}
                refreshTrigger={refreshTrigger} 
                onDataCleared={handleDataCleared}
                onIndexChange={handleIndexChange}
              />
            </div>
          </TabPane>
        </Tabs>
      </div>
    </div>
  );
};

export default ProductRAGManagement;

