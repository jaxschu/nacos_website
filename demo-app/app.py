from flask import Flask, jsonify
app = Flask(__name__)

# 模拟应用信息与“敏感配置”仅为测试，不是真实凭证
APP_INFO = {
    "name": "demo-app",
    "version": "0.1.0",
    "owner": "tester"
}

ENV_VARS = {
    "DATABASE_URL": "postgresql://testuser:TestPass123@db:5432/testdb",
    "SOME_API_KEY": "AKIA_EXAMPLE_KEY",
    "normal_var": "hello"
}

@app.route("/")
def home():
    return "demo-app running"

@app.route("/actuator/health")
def health():
    return jsonify({"status": "UP"})

@app.route("/actuator/info")
def info():
    return jsonify(APP_INFO)

@app.route("/actuator/env")
def env():
    # 小心：这是故意暴露用于本地测试的“配置”
    return jsonify(ENV_VARS)
