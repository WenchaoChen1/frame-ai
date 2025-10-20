/**
 * 面包屑导航组件
 */
import React from 'react';
import { Breadcrumb as AntBreadcrumb } from 'antd';
import { Link } from 'react-router-dom';
import { HomeOutlined } from '@ant-design/icons';
import { useBreadcrumb } from '../../hooks/useBreadcrumb';

const Breadcrumb: React.FC = () => {
  const breadcrumbs = useBreadcrumb();
  
  // 如果没有面包屑或只有一级，不显示
  if (breadcrumbs.length <= 1) {
    return null;
  }
  
  return (
    <AntBreadcrumb
      style={{ margin: '16px 24px' }}
      items={[
        {
          title: (
            <Link to="/chat">
              <HomeOutlined />
            </Link>
          ),
        },
        ...breadcrumbs.map((item, index) => {
          const isLast = index === breadcrumbs.length - 1;
          
          return {
            title: isLast ? (
              <span>
                {item.icon && <span style={{ marginRight: 4 }}>{item.icon}</span>}
                {item.title}
              </span>
            ) : (
              <Link to={item.path || '#'}>
                {item.icon && <span style={{ marginRight: 4 }}>{item.icon}</span>}
                {item.title}
              </Link>
            ),
          };
        }),
      ]}
    />
  );
};

export default Breadcrumb;

