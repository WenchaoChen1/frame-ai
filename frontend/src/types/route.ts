/**
 * 路由类型定义
 */
import { ReactNode } from 'react';

// 路由元数据
export interface RouteMeta {
  title?: string;           // 页面标题
  icon?: ReactNode;         // 菜单图标
  requireAuth?: boolean;    // 是否需要登录
  roles?: string[];         // 允许访问的角色列表
  hideInMenu?: boolean;     // 是否在菜单中隐藏
  keepAlive?: boolean;      // 是否缓存页面
  breadcrumb?: boolean;     // 是否显示面包屑
}

// 路由配置
export interface RouteConfig {
  path: string;             // 路由路径
  name?: string;            // 路由名称（用于权限控制）
  element?: ReactNode;      // 路由组件
  meta?: RouteMeta;         // 路由元数据
  children?: RouteConfig[]; // 子路由
  redirect?: string;        // 重定向路径
}

// 用户角色枚举
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest'
}

