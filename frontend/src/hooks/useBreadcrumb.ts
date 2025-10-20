/**
 * 面包屑导航 Hook
 */
import { useMemo } from 'react';
import { useLocation, matchPath } from 'react-router-dom';
import { routes } from '../router/routes';
import { RouteConfig } from '../types/route';

interface BreadcrumbItem {
  title: string;
  path?: string;
  icon?: React.ReactNode;
}

/**
 * 获取当前路由的面包屑
 */
export const useBreadcrumb = (): BreadcrumbItem[] => {
  const location = useLocation();
  
  return useMemo(() => {
    const breadcrumbs: BreadcrumbItem[] = [];
    
    // 递归匹配路由
    const matchRoute = (
      routes: RouteConfig[],
      parentPath = '',
      parentBreadcrumbs: BreadcrumbItem[] = []
    ) => {
      for (const route of routes) {
        const fullPath = parentPath + (route.path.startsWith('/') ? route.path : '/' + route.path);
        const match = matchPath(fullPath, location.pathname);
        
        if (match) {
          const currentBreadcrumbs = [...parentBreadcrumbs];
          
          // 添加当前路由到面包屑（如果配置了显示）
          if (route.meta?.breadcrumb !== false && route.meta?.title) {
            currentBreadcrumbs.push({
              title: route.meta.title,
              path: fullPath,
              icon: route.meta.icon,
            });
          }
          
          // 如果有子路由，继续匹配
          if (route.children) {
            const childMatch = matchRoute(route.children, fullPath, currentBreadcrumbs);
            if (childMatch.length > 0) {
              return childMatch;
            }
          }
          
          return currentBreadcrumbs;
        }
      }
      
      return [];
    };
    
    const matched = matchRoute(routes);
    return matched;
  }, [location.pathname]);
};

