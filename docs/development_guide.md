# 開發文檔

## 1. 專案目標
這個專案是一個以 FastAPI 提供後端、靜態 HTML/CSS/JS 提供前端的糖尿病風險評估網站。  
主要功能是讓使用者填答健康問卷，透過已訓練好的模型輸出風險結果、注意訊號與建議方向。

## 2. 專案結構

```text
app/        FastAPI 服務與模型推論邏輯
artifacts/  已訓練模型與 metadata
scripts/    訓練、測試、部署、維護腳本
web/        前端頁面與樣式
deploy/     Raspberry Pi / Cloudflare Tunnel 部署範本
docs/       開發與維護文檔
```

## 3. 啟動方式

### 本機開發
```bash
cd /Users/wang/文件/健康專題
source .venv/bin/activate
uvicorn app.main:app --reload
```

### 本機模型重訓
```bash
source .venv/bin/activate
python scripts/train_and_export.py
```

## 4. 主要程式責任

### `app/main.py`
- 啟動 FastAPI
- 定義頁面路由與 API 路由
- 套用安全標頭
- 套用 CORS 與 Trusted Host
- 控制 `/api/predict` 的資源保護

### `app/modeling.py`
- 載入已訓練模型 artifact
- 將使用者輸入轉成模型需要格式
- 執行推論
- 整理成結果頁可用的結構

### `app/domain.py`
- 特徵欄位定義
- 欄位中文名稱
- 風險分級區間
- 年齡轉 bucket 邏輯

### `app/recommendations.py`
- 依結果與輸入欄位生成注意訊號與建議

### `web/`
- `home.html`: 首頁
- `assessment.html`: 問答頁
- `result.html`: 結果頁
- `about.html`: 說明頁
- `app.js`: 頁面互動與 API 串接
- `styles.css`: 全站樣式

## 5. 開發規則

### 功能修改順序
1. 先改後端 schema / model logic
2. 再改前端表單
3. 最後跑 API 與頁面回歸檢查

### 如果改模型
必做：
1. 更新 `scripts/train_and_export.py`
2. 重新產出 `artifacts/`
3. 驗證 `/api/predict`
4. 檢查結果頁文案與分級是否仍合理

### 如果改表單欄位
必做：
1. 更新 `app/schemas.py`
2. 更新 `app/domain.py`
3. 更新 `web/app.js`
4. 檢查 `input_summary` 與 `recommendations`

## 6. 開發後必做檢查

### 路由
- `/`
- `/assessment`
- `/result`
- `/about`
- `/health`
- `POST /api/predict`

### 重要回歸點
- 首頁不要出現開發者導向資訊
- 問答頁要有 BMI 工具
- 年齡要能直接輸入
- 結果頁的 `預測結果` 與 `風險等級` 不能互相矛盾
- 結果頁的風險儀表要和 risk band 一致

## 7. 修改後的最小驗證方式

```bash
source .venv/bin/activate
python -m py_compile app/*.py scripts/*.py
python scripts/smoke_test.py
```

如果有改 API 或安全設定，再補：

```bash
python security_audit_output/artifacts/run_security_checks.py
python security_audit_output/artifacts/run_perf_tests.py
```

## 8. 不要做的事
- 不要把 `.venv`、暫存 log、測試輸出直接推上 Git
- 不要把模型內部設定直接丟給一般使用者頁面
- 不要讓前端自己處理模型 bucket 邏輯，這類轉換應留在後端
