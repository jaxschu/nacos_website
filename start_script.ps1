# 1. 挂载 tmpfs 作为 Docker 存储（解决内核 xattr 限制）
sudo mkdir -p /mnt/docker-storage
sudo mount -t tmpfs tmpfs /mnt/docker-storage

# 2. 启动 Docker 守护进程
sudo dockerd --iptables=false --bridge=none --data-root=/mnt/docker-storage &>/tmp/dockerd.log &
sleep 5

# 3. 创建本地 override 文件（强制 host 网络）
cat > docker-compose.override.yml <<'EOF'
services:
  nacos:
    network_mode: host
    ports: []
  demo-app:
    network_mode: host
    ports: []
  redis:
    network_mode: host
    ports: []
EOF

# 4. 启动所有服务
docker compose up -d

# 5. 验证
docker ps
curl http://localhost:8080/actuator/health
redis-cli ping
# Nacos 控制台：http://localhost:8848/nacos  账号/密码：nacos/nacos