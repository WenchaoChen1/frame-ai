/**
 * 路由守卫组件
 * 用于统一处理路由鉴权逻辑
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { RouteConfig } from '../types/route';

interface RouteGuardProps {
  route: RouteConfig;
  children: React.ReactNode;
}

/**
 * 路由守卫
 * - 检查登录状态
 * - 检查角色权限
 * - 处理重定向
 */
const RouteGuard: React.FC<RouteGuardProps> = ({ route, children }) => {
  const location = useLocation();
  const { isAuthenticated, user } = useAuthStore();
  const { meta } = route;

  // 如果路由需要登录但用户未登录
  if (meta?.requireAuth && !isAuthenticated) {
    console.warn('⚠️ 路由守卫: 未登录，重定向到登录页', route.path);
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // 如果路由有角色限制
  if (meta?.roles && meta.roles.length > 0) {
    // 检查用户角色（假设用户信息中有 role 字段）
    const userRole = (user as any)?.role || 'user';
    
    if (!meta.roles.includes(userRole)) {
      console.warn('⚠️ 路由守卫: 权限不足', {
        path: route.path,
        requiredRoles: meta.roles,
        userRole,
      });
      return <Navigate to="/chat" replace />;
    }
  }

  // 如果已登录用户访问登录页，重定向到首页
  if (isAuthenticated && (route.path === '/login' || route.path === '/register')) {
    console.log('✅ 路由守卫: 已登录，重定向到首页');
    return <Navigate to="/chat" replace />;
  }

  // 通过所有检查，渲染子组件
  return <>{children}</>;
};

export default RouteGuard;

