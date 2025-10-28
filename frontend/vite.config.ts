import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量，只加载 VITE_ 前缀的变量
  const env = loadEnv(mode, process.cwd(), 'VITE_')
  
  return {
    plugins: [react()],
    server: {
      host: env.VITE_HOST || '0.0.0.0',
      port: parseInt(env.VITE_PORT || '9101', 10),
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,  // 如果使用自签名证书，设置为 false
          ws: true,       // 支持 WebSocket
          configure: (proxy, _options) => {
            // 代理错误处理和日志
            proxy.on('error', (err, _req, _res) => {
              console.error('代理错误:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('代理请求:', req.method, req.url);
            });
          }
        }
      }
    },
    // 路径别名配置
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    }
  }
})

