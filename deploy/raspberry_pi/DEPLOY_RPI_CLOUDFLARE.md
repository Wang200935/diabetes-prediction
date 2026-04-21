# Raspberry Pi + Cloudflare Tunnel + 自己網域部署說明

## 1. 適用場景
這份說明是給：
- Raspberry Pi 上部署網站
- 透過 Cloudflare Tunnel 對外提供服務
- 使用自己的網域

## 2. 準備條件
- 一台 Raspberry Pi（建議 Raspberry Pi 4 以上）
- 你的網域已接到 Cloudflare
- 可安裝 `cloudflared`
- Raspberry Pi 能連外網

## 3. 建議安裝位置
```text
/opt/health-project
```

## 4. 第一步：部署專案
```bash
sudo mkdir -p /opt/health-project
sudo chown -R $USER:$USER /opt/health-project
cd /opt/health-project
git clone https://github.com/Wang200935/diabetes-prediction.git app
cd app
bash scripts/bootstrap_rpi.sh
```

## 5. 第二步：設定環境變數
把 `.env.example` 複製到：

```text
/opt/health-project/shared/.env
```

至少要改：
- `APP_ALLOWED_ORIGINS`
- `APP_ALLOWED_HOSTS`
- artifact 路徑
- `APP_BIND_PORT`

## 6. 第三步：放置 artifact
把模型檔放到：

```text
/opt/health-project/shared/artifacts/
```

至少包含：
- `model_bundle.joblib`
- `model_metadata.json`
- `feature_schema.json`

## 7. 第四步：安裝 cloudflared
請依 Cloudflare 官方文件在樹莓派安裝 `cloudflared`。

完成後登入：
```bash
cloudflared tunnel login
```

建立 named tunnel：
```bash
cloudflared tunnel create health-project
```

## 8. 第五步：設定 tunnel
複製範本：

```bash
sudo cp deploy/raspberry_pi/cloudflared-config.yml.example /etc/cloudflared/health-project.yml
```

編輯：
- `tunnel`
- `credentials-file`
- `hostname`

如果你要保留原本 `wangchatai.dpdns.org` 這個網站，同時再新增健康網站，建議這樣設：

```yaml
ingress:
  - hostname: wangchatai.dpdns.org
    service: http://127.0.0.1:8318
  - hostname: health.wangchatai.dpdns.org
    service: http://127.0.0.1:8320
  - hostname: grok.wangchatai.dpdns.org
    service: http://127.0.0.1:8000
  - service: http_status:404
```

其中：
- `8318` 是 CPAMC bridge，會把根網域導向 CPAMC 的 `/management.html#/`
- `8320` 是這個健康網站

如果你只有健康網站，才用下面這種簡單設定：

```text
http://127.0.0.1:8320
```

如果你要讓根網域自動進 CPAMC 管理頁，可另外安裝：

```bash
sudo cp deploy/raspberry_pi/cpamc-bridge.service /etc/systemd/system/cpamc-bridge.service
sudo systemctl daemon-reload
sudo systemctl enable --now cpamc-bridge
```

## 8.1 單純健康網站時的 tunnel 指向

讓它指向：
```text
http://127.0.0.1:8320
```

## 9. 第六步：安裝 systemd
```bash
bash scripts/install_rpi_services.sh
```

啟動：
```bash
sudo systemctl enable --now health-project
sudo systemctl enable --now cloudflared-health-project
```

## 10. 第七步：檢查
```bash
bash scripts/check_rpi_services.sh
```

如果本機健康檢查正常，再用你的網域打開網站。

## 11. 更新流程
```bash
cd /opt/health-project/app
bash scripts/update_rpi_app.sh
```

若這次需要重訓：
```bash
RETRAIN=true bash scripts/update_rpi_app.sh
```
