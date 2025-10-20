import React, { useEffect, useRef } from 'react';
import { Avatar, Card, Table, Collapse, Tag } from 'antd';
import { UserOutlined, RobotOutlined, DatabaseOutlined, CodeOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { useConversationStore } from '../../store/conversationStore';

const { Panel } = Collapse;

const MessageList: React.FC = () => {
  const messages = useConversationStore((state) => state.messages);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 渲染查询结果表格
  const renderQueryResult = (queryResult: any) => {
    if (!queryResult || !queryResult.columns || !queryResult.rows) {
      return null;
    }

    const columns = queryResult.columns.map((col: string) => ({
      title: col,
      dataIndex: col,
      key: col,
      ellipsis: true,
    }));

    const dataSource = queryResult.rows.map((row: any[], index: number) => {
      const record: any = { key: index };
      queryResult.columns.forEach((col: string, colIndex: number) => {
        record[col] = row[colIndex];
      });
      return record;
    });

    return (
      <div style={{ marginTop: 16 }}>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          marginBottom: 8,
          gap: 8
        }}>
          <DatabaseOutlined style={{ color: '#52c41a' }} />
          <span style={{ fontWeight: 600, color: '#333' }}>查询结果</span>
          <Tag color="blue">{queryResult.row_count} 行</Tag>
        </div>
        <Table
          columns={columns}
          dataSource={dataSource}
          size="small"
          pagination={{ 
            pageSize: 10,
            showSizeChanger: false,
            showTotal: (total) => `共 ${total} 条`
          }}
          scroll={{ x: 'max-content' }}
          style={{ 
            background: '#fafafa',
            borderRadius: 4
          }}
        />
      </div>
    );
  };

  return (
    <div style={{ 
      flex: 1, 
      overflow: 'auto', 
      padding: '24px',
      background: '#fafafa'
    }}>
      {messages.map((message, index) => (
        <div
          key={message.id || index}
          style={{
            display: 'flex',
            justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
            marginBottom: 16,
          }}
        >
          <div style={{ 
            display: 'flex', 
            maxWidth: message.role === 'assistant' && message.query_result ? '90%' : '70%',
            flexDirection: message.role === 'user' ? 'row-reverse' : 'row',
            gap: 12
          }}>
            <Avatar 
              icon={message.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
              style={{ 
                background: message.role === 'user' ? '#1890ff' : '#52c41a',
                flexShrink: 0
              }}
            />
            <Card
              size="small"
              style={{
                background: message.role === 'user' ? '#e6f7ff' : '#fff',
                borderRadius: 8,
                width: '100%'
              }}
            >
              {/* SQL 查询标识 */}
              {message.sql_query && (
                <div style={{ marginBottom: 12 }}>
                  <Tag icon={<DatabaseOutlined />} color="success">
                    SQL 查询
                  </Tag>
                </div>
              )}

              {/* 消息内容 */}
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {message.content}
              </ReactMarkdown>

              {/* SQL 查询详情（可折叠） */}
              {message.sql_query && (
                <Collapse 
                  ghost 
                  style={{ marginTop: 16 }}
                  expandIconPosition="end"
                >
                  <Panel 
                    header={
                      <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <CodeOutlined />
                        <span>查看 SQL</span>
                      </span>
                    } 
                    key="1"
                  >
                    <pre style={{
                      background: '#f5f5f5',
                      padding: 12,
                      borderRadius: 4,
                      overflow: 'auto',
                      fontSize: 13,
                      fontFamily: 'Monaco, Consolas, monospace',
                      margin: 0
                    }}>
                      {message.sql_query}
                    </pre>
                  </Panel>
                </Collapse>
              )}

              {/* 查询结果表格 */}
              {message.query_result && renderQueryResult(message.query_result)}

              {/* 模型信息 */}
              {message.model && (
                <div style={{ 
                  fontSize: 12, 
                  color: '#999', 
                  marginTop: 12,
                  borderTop: '1px solid #f0f0f0',
                  paddingTop: 8
                }}>
                  {message.provider} / {message.model}
                </div>
              )}
            </Card>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;

