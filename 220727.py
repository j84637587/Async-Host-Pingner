import os
import re
import ctypes
from datetime import datetime
import asyncio
import json
import time

IP_regex = "^((25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])$"
ttl_pattern = re.compile("ttl=(\d+)")
bytes_pattern = re.compile("(\d+)\sbytes")
out = open("out.json", "w+")

# def validIP(ip: str) -> bool:
#     """
#     驗證字串是否為ip格式

#     Args:
#         ip (str): ip字串

#     Returns:
#         bool: 字串是否為ip格式
#     """
#     return re.search(IP_regex, str)

# def validHostname(hostname: str) -> bool:
#     if len(hostname) > 255:
#         return False
#     if hostname[-1] == ".":
#         hostname = hostname[:-1] # strip exactly one dot from the right, if present
#     allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
#     return all(allowed.match(x) for x in hostname.split("."))

def readIPs() -> list:
    """
    讀取IP並過濾掉不符合的項目

    Returns:
        list[str]: IP串列
    """
    with open("ips.txt") as file:
        lines = file.readlines()
        ips = []
        for idx, line in enumerate(lines):
            line = line.rstrip()
            ips.append(line)
            # if True: #validIP(line) or :
            #     ips.append(line)
            # else:
            #     print(f"Line {idx+1} is not a valid ip, skip this time!")
        return ips


logs = []


def logger(ip: str, rtn: int, ttl: str, bytes: str, stderr: str) -> None:
    """
    紀錄事件並輸出

    Args:
        ip (str): 要記錄的IP
        rtn (int): Ping回傳值
        ttl (str): 要記錄的ttl(time to live)
        bytes (str): 要記錄的bytes
        stderr (str): 錯誤訊息
    """
    now = datetime.now()
    dts = now.strftime("%d/%m/%Y %H:%M:%S")
    if rtn == 0:
        r = f"[{dts}] IP: {ip:30} is up      TTL: {ttl:4}    Bytes: {bytes:5}"
    else:
        stderr = stderr.rstrip("\n")
        r = f"[{dts}] IP: {ip:30} is down    " + (f"Error: {stderr}" if stderr != "" else "")
    logs.append(r)
    out.seek(0)
    out.truncate(0)
    json.dump(logs, out, indent=4)
    print(r)


async def ping(ip: str) -> None:
    """
    Ping 指定 ip

    Args:
        ip (str): 要ping的ip
    """
    proc = await asyncio.create_subprocess_shell(
        f"ping -c 1 -s 12 {ip}",  # 設置ttl(-t)並不會改變回傳封包的ttl
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    if proc.returncode == 0:
        bytes = bytes_pattern.search(stdout).group(1)
        ttl = ttl_pattern.search(stdout).group(1)
    else:
        bytes = ttl = 0
    logger(ip, proc.returncode, ttl, bytes, stderr)


async def main(ips: list) -> None:
    """
    主函式

    Args:
        ips (list): ip清單
    """
    # 非同步Ping IP
    tasks = []
    for ip in ips:
        tasks.append(asyncio.create_task(ping(ip)))

    
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 檢查權限
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if not is_admin:
        print("You do not have administrator rights! Program terminated.")
        exit()

    # 讀取IP檔
    ips = readIPs()
    
    while True:
        asyncio.run(main(ips))
        time.sleep(10)