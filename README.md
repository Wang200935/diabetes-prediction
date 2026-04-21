# 糖尿病風險評估中心

這個專案是一個可部署的糖尿病風險評估網站，提供：

- 問答式健康資料蒐集
- 風險推估 API
- 前端結果頁、風險視覺化、建議卡片
- 模型 artifact 管理
- Raspberry Pi + Cloudflare Tunnel + 自己網域部署範本
- 開發文檔與維護文檔

這個 repo 的目標不是只有在本機 demo，而是整理成可以持續維護、可更新模型、可部署到樹莓派的實際專案。

## 專案結構

```text
app/                        FastAPI 服務與推論邏輯
artifacts/                  已匯出的模型與 metadata
deploy/raspberry_pi/        樹莓派與 Cloudflare Tunnel 部署範本
docs/                       開發與維護文件
scripts/                    訓練、檢查、部署、更新腳本
web/                        前端頁面與靜態資源
security_audit_output/      安全與效能測試輸出
```

## 功能概覽

### 前端頁面
- `/`：首頁
- `/assessment`：問答頁
- `/result`：結果頁
- `/about`：模型說明頁

### API
- `GET /health`
- `POST /api/predict`

### 問答特色
- BMI 小工具
- 實際年齡輸入，後端自動轉成模型 bucket
- 多頁式體驗，不把首頁、問答、結果混在同一頁

## 本機開發

### 1. 安裝依賴

```bash
cd /Users/wang/文件/健康專題
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 重新產出模型

```bash
python scripts/train_and_export.py
```

### 3. 啟動網站

```bash
uvicorn app.main:app --reload
```

### 4. 打開網站

```text
http://127.0.0.1:8000
```

## 模型與 artifact

主要檔案：

- `artifacts/model_bundle.joblib`
- `artifacts/model_metadata.json`
- `artifacts/feature_schema.json`

重訓後要確認：

1. artifact 有更新
2. `/api/predict` 正常
3. 結果頁顯示合理
4. `result_summary` 和 `risk_level` 不矛盾

## 開發與維護文件

- [開發文檔](./docs/development_guide.md)
- [維護文檔](./docs/maintenance_guide.md)
- [樹莓派 + Cloudflare Tunnel 部署說明](./deploy/raspberry_pi/DEPLOY_RPI_CLOUDFLARE.md)

## Raspberry Pi + Cloudflare Tunnel

這個專案已經準備好樹莓派部署所需的：

- `.env.example`
- app systemd service
- cloudflared systemd service
- cloudflared 設定範本
- bootstrap / install / update / check 腳本

相關檔案：

- `deploy/raspberry_pi/health-project.service`
- `deploy/raspberry_pi/cloudflared-health-project.service`
- `deploy/raspberry_pi/cloudflared-config.yml.example`
- `scripts/bootstrap_rpi.sh`
- `scripts/install_rpi_services.sh`
- `scripts/update_rpi_app.sh`
- `scripts/check_rpi_services.sh`

## 安全與效能

專案內已保留最近一次本機安全與效能檢查輸出：

- `security_audit_output/report.md`
- `security_audit_output/findings.json`
- `security_audit_output/repro_steps.md`
- `security_audit_output/perf_summary.md`

如果你有改：
- CORS
- 安全標頭
- `/api/predict` 限流/併發
- schema 驗證

建議重新跑：

```bash
python security_audit_output/artifacts/run_security_checks.py
python security_audit_output/artifacts/run_perf_tests.py
```

## 注意事項

- `scripts/train_and_export.py` 會優先找本機資料集目錄
- 若找不到才會退回 `kagglehub`
- 目前 deployable 模型會比較候選模型後，自動選 accuracy 較高者
- 如果你之後更動模型特徵、risk bands、輸入欄位，請同步更新：
  - `app/domain.py`
  - `app/schemas.py`
  - `app/modeling.py`
  - `web/app.js`
