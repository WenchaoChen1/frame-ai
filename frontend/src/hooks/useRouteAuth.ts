/**
 * 路由权限相关的 Hooks
 */
import { useMemo } from 'react';
import { useAuthStore } from '../store/authStore';
import { routes, filterRoutesByRole, getMenuRoutes } from '../router/routes';
import { RouteConfig } from '../types/route';

/**
 * 获取当前用户可访问的路由
 */
export const useAccessRoutes = () => {
  const { user } = useAuthStore();
  
  return useMemo(() => {
    const userRole = (user as any)?.role || 'user';
    return filterRoutesByRole(routes, userRole);
  }, [user]);
};

/**
 * 获取当前用户可见的菜单
 */
export const useMenus = () => {
  const accessRoutes = useAccessRoutes();
  
  return useMemo(() => {
    return getMenuRoutes(accessRoutes);
  }, [accessRoutes]);
};

/**
 * 检查用户是否有权限访问指定路由
 */
export const useRouteAccess = (routeName: string) => {
  const { user, isAuthenticated } = useAuthStore();
  
  return useMemo(() => {
    if (!isAuthenticated) return false;
    
    const userRole = (user as any)?.role || 'user';
    
    // 递归查找路由
    const findRoute = (routes: RouteConfig[]): RouteConfig | null => {
      for (const route of routes) {
        if (route.name === routeName) {
          return route;
        }
        if (route.children) {
          const found = findRoute(route.children);
          if (found) return found;
        }
      }
      return null;
    };
    
    const route = findRoute(routes);
    if (!route) return false;
    
    // 检查角色权限
    if (route.meta?.roles && route.meta.roles.length > 0) {
      return route.meta.roles.includes(userRole);
    }
    
    return true;
  }, [routeName, user, isAuthenticated]);
};

