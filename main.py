import os
import re
import ctypes
from datetime import datetime
import asyncio
import json
import time

ttl_pattern = re.compile("ttl=(\d+)")
bytes_pattern = re.compile("(\d+)\sbytes")
timems_pattern = re.compile("time\=(.*)\sms")
out = open("out.json", "w+")

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
        return ips


logs = []


def logger(ip: str, rtn: int, ttl: str, bytes: str, timems: str, stderr: str) -> None:
    """
    紀錄事件並輸出

    Args:
        ip (str): 要記錄的IP
        rtn (int): Ping回傳值
        ttl (str): 要記錄的ttl(time to live)
        bytes (str): 要記錄的bytes
        timems (str): timems
        stderr (str): 錯誤訊息
    """
    now = datetime.now()
    dts = now.strftime("%d/%m/%Y %H:%M:%S")
    if rtn == 0:
        r = f"[{dts}] IP: {ip:30} is up      TTL: {ttl:4}    Bytes: {bytes:5}    Time: {timems:6} ms"
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
        f"ping -c 1 {ip}",  # 設置ttl(-t)並不會改變回傳封包的ttl
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()
    stderr = stderr.decode()
    if proc.returncode == 0:
        bytes = bytes_pattern.search(stdout).group(1)
        ttl = ttl_pattern.search(stdout).group(1)
        
        a = timems_pattern.search(stdout)
        try:
            timems = a.group(1)
        except AttributeError as error:
            print("<<<<<<", stdout, ">>>>>>>>")
    else:
        bytes = ttl = timems = 0
    logger(ip, proc.returncode, ttl, bytes, timems, stderr)


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