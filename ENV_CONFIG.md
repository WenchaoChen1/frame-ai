# 鍓嶇鐜鍙橀噺閰嶇疆璇存槑

## 姒傝堪

鏈」鐩娇鐢ㄧ幆澧冨彉閲忔潵閰嶇疆鍓嶇搴旂敤锛屾敮鎸佸紑鍙戝拰鐢熶骇涓ょ妯″紡銆?

## 鏂囦欢璇存槑

1. **椤圭洰鏍圭洰褰?.env.example** - Docker Compose 鐜鍙橀噺妯℃澘
2. **frontend/.env.example** - 鍓嶇 Vite 鐜鍙橀噺妯℃澘
3. **frontend/.env** - 鏈湴寮€鍙戠幆澧冨彉閲忥紙涓嶆彁浜ゅ埌 Git锛?

## 蹇€熷紑濮?

### 1. 鏈湴寮€鍙戯紙涓嶄娇鐢?Docker锛?

```bash
cd frontend
cp .env.example .env
npm run dev
```

璁块棶: http://localhost:9101

### 2. Docker 寮€鍙戠幆澧?

```bash
cp .env.example .env
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

璁块棶: http://localhost:3000

### 3. Docker 鐢熶骇鐜

```bash
cp .env.example .env
docker-compose up --build
```

璁块棶: http://localhost

## 鐜鍙橀噺璇存槑

### 鍓嶇 Vite 鐜鍙橀噺锛坒rontend/.env锛?

| 鍙橀噺鍚?| 榛樿鍊?| 璇存槑 |
|--------|--------|------|
| VITE_PORT | 9101 | 寮€鍙戞湇鍔″櫒绔彛 |
| VITE_HOST | 0.0.0.0 | 寮€鍙戞湇鍔″櫒鐩戝惉鍦板潃 |
| VITE_API_PROXY_TARGET | http://localhost:8000 | API 浠ｇ悊鐩爣锛堝紑鍙戞ā寮忥級 |
| VITE_API_URL | 绌?| API URL锛堢敓浜фā寮忥紝鐣欑┖浣跨敤鐩稿璺緞锛?|

## 宸ヤ綔鍘熺悊

### 寮€鍙戞ā寮?
1. Vite 浠?frontend/.env 璇诲彇鐜鍙橀噺
2. 浣跨敤浠ｇ悊灏?/api 璇锋眰杞彂鍒板悗绔?
3. 浠ｇ爜鏀寔鐑噸杞?

### 鐢熶骇妯″紡
1. Docker 鏋勫缓鏃朵粠鏍圭洰褰?.env 璇诲彇鍙橀噺
2. 閫氳繃 docker-compose.yml 鐨?build.args 浼犻€掔粰 Dockerfile
3. Vite 鏋勫缓鏃跺皢鐜鍙橀噺缂栬瘧鍒伴潤鎬佹枃浠朵腑
4. Nginx 鎻愪緵闈欐€佹枃浠舵湇鍔★紝API 璇锋眰閫氳繃鐩稿璺緞璁块棶

## 娉ㄦ剰浜嬮」

1. 涓嶈鎻愪氦 .env 鏂囦欢鍒?Git锛堝凡鍦?.gitignore 涓厤缃級
2. 鐢熶骇鐜蹇呴』淇敼榛樿瀵嗛挜锛圫ECRET_KEY 绛夛級
3. Vite 鐜鍙橀噺蹇呴』浠?VITE_ 寮€澶存墠鑳藉湪瀹㈡埛绔唬鐮佷腑浣跨敤
4. 鐢熶骇鐜寤鸿浣跨敤鐩稿璺緞锛圴ITE_API_URL 鐣欑┖锛?
5. 寮€鍙戠幆澧冧娇鐢ㄤ唬鐞嗛伩鍏?CORS 闂
