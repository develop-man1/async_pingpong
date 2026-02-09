import os
from pathlib import Path
from datetime import datetime
from config import LOG_DIR, CLIENT_LOG_TEMPLATE

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)


def get_client_log_path(client_id: int) -> str:
    
    return os.path.join(LOG_DIR, CLIENT_LOG_TEMPLATE.format(client_id))


def log_client_event(client_id: int, request_text: str = "", response_text: str = "", request_time: datetime | None = None, response_time: datetime | None = None, timeout: bool = False, keepalive: bool = False) -> None:
    
    log_path = get_client_log_path(client_id)

    date_str = datetime.now().strftime("%Y-%m-%d")
    req_time_str = request_time.strftime("%H:%M:%S.") + f"{request_time.microsecond // 1000:03d}" if request_time else ""
    resp_time_str = response_time.strftime("%H:%M:%S.") + f"{response_time.microsecond // 1000:03d}" if response_time else ""

    if timeout:
        resp_time_str = resp_time_str or datetime.now().strftime("%H:%M:%S.") + f"{datetime.now().microsecond // 1000:03d}"
        response_text = "(таймаут)"

    if keepalive:
        request_text = ""
        req_time_str = ""

    log_line = f"{date_str};{req_time_str};{request_text};{resp_time_str};{response_text}"

    with open(log_path, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")