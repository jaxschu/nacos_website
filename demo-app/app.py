from flask import Flask, jsonify, request, render_template_string
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

BASIC_CONFIG = {
    "siteName": "demo-app site",
    "theme": "light",
    "features": [
        "health-check",
        "info-endpoint",
        "env-exposure"
    ]
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

@app.route("/config")
def config():
    """Return a basic configuration for the website."""
    return jsonify(BASIC_CONFIG)

@app.route("/preview")
def preview():
    """
    Intentionally vulnerable: renders user input directly as a Jinja template.
    Attackers can craft payloads such as {{ config.items() }} to read secrets.
    """
    template = request.args.get("template", "")
    if not template:
        return "missing template parameter", 400
    return render_template_string(template)
