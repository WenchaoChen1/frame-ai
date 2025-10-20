import axios from 'axios';

// 开发模式开关（生产环境请设置为 false）
const DEBUG_MODE = import.meta.env.DEV;

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器：添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      if (DEBUG_MODE) {
        console.log('🔑 API请求:', config.url);
      }
    } else if (DEBUG_MODE && config.url !== '/auth/login' && config.url !== '/auth/register') {
      console.warn('⚠️ API请求未携带token:', config.url);
    }
    return config;
  },
  (error) => {
    if (DEBUG_MODE) {
      console.error('❌ 请求拦截器错误:', error);
    }
    return Promise.reject(error);
  }
);

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (DEBUG_MODE) {
        console.error('❌ 401 未授权:', {
          url: error.config?.url,
          detail: error.response?.data?.detail
        });
      }
      
      // 清除无效的认证信息
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      
      // 只在非登录页面时重定向
      // 使用 window.location.replace 避免产生历史记录
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        if (DEBUG_MODE) {
          console.log('🔄 清除认证信息，重定向到登录页');
        }
        window.location.replace('/login');
      }
    }
    return Promise.reject(error);
  }
);

export default api;

