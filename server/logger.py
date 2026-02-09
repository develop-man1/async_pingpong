import os
from pathlib import Path
from datetime import datetime
from config import LOG_DIR, SERVER_LOG_FILE
from utils import current_date, current_time

Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

LOG_PATH = os.path.join(LOG_DIR, SERVER_LOG_FILE)


def log_request(
    request_text: str,
    response_text: str | None = None,
    ignored: bool = False,
    request_time: datetime | None = None,
    response_time: datetime | None = None
) -> None:
    
    
    req_time_str = request_time.strftime("%H:%M:%S.") + f"{request_time.microsecond // 1000:03d}" if request_time else current_time()
    resp_time_str = response_time.strftime("%H:%M:%S.") + f"{response_time.microsecond // 1000:03d}" if response_time else current_time()

    if ignored:
        resp_time_str = "(проигнорировано)"
        response_text = "(проигнорировано)"
    else:
        response_text = response_text or ""

    log_line = f"{current_date()};{req_time_str};{request_text};{resp_time_str};{response_text}"

    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(log_line + "\n")