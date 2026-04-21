# 維護文檔

## 1. 維護目標
這份文件是給「上線後維護網站」用的，不只是開發時參考。  
重點是讓你之後可以穩定做到：
- 更新程式
- 重啟服務
- 替換模型
- 看 log
- 檢查 Tunnel
- 排查故障

## 2. 建議的 Raspberry Pi 目錄結構

```text
/opt/health-project/
├── app/              Git 專案
├── venv/             Python 虛擬環境
├── shared/
│   ├── .env
│   ├── artifacts/
│   └── dataset/
└── logs/
```

## 3. 第一次部署順序

1. 把專案 clone 到樹莓派
2. 跑：

```bash
bash scripts/bootstrap_rpi.sh
```

3. 編輯：
```text
/opt/health-project/shared/.env
```

4. 把模型 artifact 放到：
```text
/opt/health-project/shared/artifacts/
```

建議網站本機只綁：
```text
127.0.0.1:8320
```

5. 安裝 systemd：

```bash
bash scripts/install_rpi_services.sh
```

6. 啟動服務：

```bash
sudo systemctl enable --now health-project
sudo systemctl enable --now cloudflared-health-project
```

## 4. 日常更新流程

平常更新程式時，建議固定這樣做：

```bash
cd /opt/health-project/app
bash scripts/update_rpi_app.sh
```

如果這次有改模型：

```bash
RETRAIN=true bash scripts/update_rpi_app.sh
```

## 5. 模型更新流程

如果你有新的模型 artifact，有兩種方式：

### 方式 A：在本機訓練好再上傳
1. 在開發機重訓
2. 上傳新的 `artifacts/model_bundle.joblib`
3. 上傳 `model_metadata.json`
4. 重啟 `health-project`

### 方式 B：在樹莓派重訓
前提是樹莓派本機有資料集。

```bash
source /opt/health-project/venv/bin/activate
cd /opt/health-project/app
python scripts/train_and_export.py
sudo systemctl restart health-project
```

## 6. 常用維護指令

### 查看服務狀態
```bash
bash scripts/check_rpi_services.sh
```

### 查看網站服務 log
```bash
sudo journalctl -u health-project -n 100 --no-pager
```

### 查看 cloudflared log
```bash
sudo journalctl -u cloudflared-health-project -n 100 --no-pager
```

### 重啟網站
```bash
sudo systemctl restart health-project
```

### 重啟 tunnel
```bash
sudo systemctl restart cloudflared-health-project
```

## 7. Cloudflare Tunnel 維護重點

你需要維護的東西有兩個：

1. Cloudflare DNS
2. `/etc/cloudflared/health-project.yml`

如果網域變了，就改：
- `.env` 裡的 `APP_ALLOWED_ORIGINS`
- `APP_ALLOWED_HOSTS`
- `cloudflared` 設定檔裡的 `hostname`

改完後：

```bash
sudo systemctl restart cloudflared-health-project
sudo systemctl restart health-project
```

## 8. 常見故障排查

### 網站打不開
先查：
```bash
sudo systemctl status health-project
sudo systemctl status cloudflared-health-project
```

### 網域打不開但本機可以
先查：
- Cloudflare DNS
- Tunnel service 狀態
- `cloudflared` 設定檔 hostname 是否正確
- `.env` 裡的 `APP_BIND_PORT` 是否和 tunnel 指向的 port 一致

### `/api/predict` 很慢或大量失敗
先查：
- CPU 是否滿載
- 是否有人大量打 `/api/predict`
- 目前 `.env` 裡的資源限制參數是否太保守

相關參數：
- `PREDICT_CONCURRENCY_LIMIT`
- `PREDICT_ACQUIRE_TIMEOUT_SECONDS`
- `PREDICT_EXEC_TIMEOUT_SECONDS`
- `PREDICT_RATE_LIMIT_MAX_REQUESTS`

## 9. 上線後定期維護建議

### 每週
- 檢查服務是否正常
- 看一次最近 log

### 每月
- 更新 Python 套件
- 重新跑健康檢查
- 檢查域名與 Tunnel 是否正常

### 每次大改版後
- 重新跑：
  - `scripts/smoke_test.py`
  - `security_audit_output/artifacts/run_security_checks.py`
  - `security_audit_output/artifacts/run_perf_tests.py`

## 10. 維護原則
- 不要直接在 production 機器上隨手改 Python 程式碼
- 先在開發環境測好，再更新到樹莓派
- 更新完一定要重啟服務並看 log
- 模型 artifact 與程式碼版本最好同步記錄
