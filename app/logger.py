import json, sys, time, uuid

def log(level: str, message: str, **kwargs):
    event = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": level.upper(),
        "message": message,
        "event_id": str(uuid.uuid4()),
        **kwargs
    }
    sys.stdout.write(json.dumps(event, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def info(message: str, **kwargs): log("INFO", message, **kwargs)
def warn(message: str, **kwargs): log("WARNING", message, **kwargs)
def error(message: str, **kwargs): log("ERROR", message, **kwargs)
