import React from 'react';
import { Card, Empty, Typography } from 'antd';
import { ToolOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

const ToolManagement: React.FC = () => {
  return (
    <div style={{ padding: 24 }}>
      <Card>
        <Empty
          image={<ToolOutlined style={{ fontSize: 80, color: '#1890ff' }} />}
          imageStyle={{
            height: 120,
          }}
          description={
            <div>
              <Title level={3}>工具管理</Title>
              <Paragraph type="secondary">
                该功能正在开发中，敬请期待...
              </Paragraph>
            </div>
          }
        >
          <div style={{ marginTop: 16, color: '#999' }}>
            <p>🔧 未来功能规划：</p>
            <ul style={{ textAlign: 'left', display: 'inline-block' }}>
              <li>AI工具配置与管理</li>
              <li>插件系统</li>
              <li>自定义工具集成</li>
              <li>工具使用统计</li>
            </ul>
          </div>
        </Empty>
      </Card>
    </div>
  );
};

export default ToolManagement;

