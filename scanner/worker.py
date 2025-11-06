# worker.py
import redis, json, requests, time
from datetime import datetime

r = redis.Redis(host="localhost", port=6379, db=0)
QUEUE = "tasks"
OUTFILE = "results.json"
KEYWORDS = ['password','secret','ak','sk','accesskey','secretkey','api_key','DATABASE_URL','SOME_API_KEY']

def check_task(task):
    url = task.get("url")
    name = task.get("name")
    res = {"name": name, "url": url, "time": datetime.utcnow().isoformat(), "status": None, "keywords": [], "snippet": None}
    try:
        resp = requests.get(url, timeout=8)
        res['status'] = resp.status_code
        text = resp.text or ""
        res['snippet'] = text[:1000]
        lowered = text.lower()
        found = []
        for k in KEYWORDS:
            if k.lower() in lowered:
                found.append(k)
        res['keywords'] = found
    except Exception as e:
        res['status'] = "error"
        res['snippet'] = str(e)
    return res

def worker_loop():
    print("Worker started, listening for tasks...")
    while True:
        job = r.blpop(QUEUE, timeout=5)
        if not job:
            time.sleep(1)
            continue
        _, raw = job
        task = json.loads(raw)
        print("Got task:", task)
        result = check_task(task)
        print("Result:", result)
        # append result to file
        with open(OUTFILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    worker_loop()
