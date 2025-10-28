# 鍓嶇鐜鍙橀噺閰嶇疆淇鎬荤粨

## 闂鎻忚堪

鍓嶇鐨?.env 閰嶇疆娌℃湁鐢熸晥锛屼富瑕侀棶棰樺寘鎷細
1. 缂哄皯 .env 鍜?.env.example 鏂囦欢
2. vite.config.ts 娌℃湁璇诲彇鐜鍙橀噺
3. robot.ts 浣跨敤浜嗘湭瀹氫箟鐨勭幆澧冨彉閲?
4. Docker 鏋勫缓鏃舵病鏈変紶閫掔幆澧冨彉閲?

## 淇鍐呭

### 1. 鍒涘缓鐜鍙橀噺鏂囦欢

- 鏍圭洰褰?.env.example
- frontend/.env.example
- frontend/.env

### 2. 鏇存柊閰嶇疆鏂囦欢

- frontend/vite.config.ts - 娣诲姞 loadEnv 鏀寔
- frontend/src/services/robot.ts - 淇 API_URL 閰嶇疆
- frontend/Dockerfile - 娣诲姞鏋勫缓鍙傛暟
- frontend/Dockerfile.dev - 娣诲姞杩愯鏃剁幆澧冨彉閲?
- docker-compose.yml - 娣诲姞 build.args
- docker-compose.dev.yml - 鏇存柊寮€鍙戠幆澧冮厤缃?

## 浣跨敤鏂规硶

### 鏈湴寮€鍙?

```bash
cd frontend
cp .env.example .env
npm run dev
```

璁块棶锛歨ttp://localhost:9101

### Docker 寮€鍙戠幆澧?

```bash
cp .env.example .env
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

璁块棶锛歨ttp://localhost:3000

### Docker 鐢熶骇鐜

```bash
cp .env.example .env
docker-compose up --build
```

璁块棶锛歨ttp://localhost

## 鐜鍙橀噺璇存槑

### 鍓嶇 Vite 鍙橀噺

| 鍙橀噺鍚?| 榛樿鍊?| 璇存槑 |
|--------|--------|------|
| VITE_PORT | 9101 | 寮€鍙戞湇鍔″櫒绔彛 |
| VITE_HOST | 0.0.0.0 | 寮€鍙戞湇鍔″櫒鍦板潃 |
| VITE_API_PROXY_TARGET | http://localhost:8000 | API 浠ｇ悊鐩爣锛堝紑鍙戯級 |
| VITE_API_URL | 绌?| API URL锛堢敓浜э紝鐣欑┖鐢ㄧ浉瀵硅矾寰勶級 |

## 楠岃瘉

### 鏈湴寮€鍙戦獙璇?
```bash
cd frontend
npm run dev
```

### 鐜鍙橀噺楠岃瘉
鍦ㄦ祻瑙堝櫒鎺у埗鍙拌緭鍏ワ細
```javascript
console.log(import.meta.env)
```

## 鐩稿叧鏂囨。

璇︾粏閰嶇疆璇存槑璇峰弬鑰冿細ENV_CONFIG.md
