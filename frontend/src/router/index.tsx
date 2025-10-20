/**
 * 路由生成器
 * 根据路由配置生成 React Router 路由
 */
import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { RouteConfig } from '../types/route';
import RouteGuard from './RouteGuard';
import { routes } from './routes';

/**
 * 递归渲染路由
 */
const renderRoutes = (routes: RouteConfig[]): React.ReactNode => {
  return routes.map((route, index) => {
    const { path, element, redirect, children } = route;
    const key = route.name || `route-${index}`;

    // 如果有重定向
    if (redirect) {
      return <Route key={key} path={path} element={<Navigate to={redirect} replace />} />;
    }

    // 如果有子路由
    if (children && children.length > 0) {
      return (
        <Route
          key={key}
          path={path}
          element={
            <RouteGuard route={route}>
              {element}
            </RouteGuard>
          }
        >
          {renderRoutes(children)}
        </Route>
      );
    }

    // 普通路由
    return (
      <Route
        key={key}
        path={path}
        element={
          <RouteGuard route={route}>
            {element}
          </RouteGuard>
        }
      />
    );
  });
};

/**
 * 路由容器组件
 */
const AppRouter: React.FC = () => {
  return <Routes>{renderRoutes(routes)}</Routes>;
};

export default AppRouter;
export { routes };

