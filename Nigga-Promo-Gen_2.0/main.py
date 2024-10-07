import subprocess
import sys

def install_missing_modules():
    required_modules = [
        'colorama', 
        'aiohttp', 
        'faker', 
        'requests', 
        'fake_useragent', 
        'multiprocessing', 
        'itertools', 
        'dateutil',
    ]
    
    for module in required_modules:
        try:
            __import__(module)  
        except ImportError:
            try:
                print(f"Module {module} not found, installing...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", module])
                print(f"Successfully installed {module}")
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {module}. Error: {e}")

install_missing_modules()

import platform
import shutil
from colorama import Fore
import aiohttp
import asyncio
import random
from faker import Faker
import time
import os
import requests
from fake_useragent import UserAgent
from multiprocessing import Pool, cpu_count, Manager
import itertools
from data.logger import Console_UI
from dateutil import parser
from time import perf_counter
import datetime

log = Console_UI()
ua = UserAgent()
fake = Faker()
def getToken():
    with open("data/tokens.txt") as file:
        lines = file.read().splitlines()
        token = random.choice(lines)
        if ":" in token:
            data = token.split(":")
            token_value = data[-1]
            return token_value
        else:
            return token
token = getToken()
REQUEST_TIMEOUT = 30

def __LOGO__():
    logo = """
    @ https://ebyte.pro 
    """
    width = shutil.get_terminal_size().columns
    lines = logo.split('\n')
    banner = '\n'.join(line.center(width) for line in lines)
    print(Fore.CYAN + banner)

def __NAME__():
    return (fake.first_name() + fake.last_name()).lower()

def __CLS__():
    system = platform.system()
    if system == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def load_proxies():
    with open('./data/proxies.txt', 'r') as f:
        proxies = f.read().splitlines()
    return proxies

def check_token(token):
    auth = {"Authorization": token}
    r = requests.get("https://ptb.discord.com/api/v10/users/@me", headers=auth)
    if r.status_code in [201, 204, 200]:
        return auth
    else:
        log.warn("Invalid Token.")
        sys.exit()

async def check(promocode, valid_count, claimed_count):
    auth = check_token(token)

    async with aiohttp.ClientSession(headers=auth) as cs:
        proxies = load_proxies()
        proxy = random.choice(proxies)
        url = f"https://ptb.discord.com/api/v10/entitlements/gift-codes/{promocode}"

        try:
            async with cs.get(url, proxy=f"http://{proxy}") as rs:
                if rs.status in [200, 204, 201]:
                    data = await rs.json()
                    if data.get("uses") == data.get("max_uses"):
                        log.warn(f"Already Claimed -> {promocode}")
                        save("output/claimed.txt", f"https://discord.com/billing/promotions/{promocode}")
                        claimed_count.value += 1
                    else:
                        try:
                            now = datetime.datetime.utcnow()
                            exp_at = data.get("expires_at", "Unknown").split(".")[0]
                            parsed = parser.parse(exp_at)
                            days = abs((now - parsed).days)
                            title = data.get("promotion", {}).get("inbound_header_text", "Unknown")
                        except Exception as e:
                            log.warn(f"Error parsing promo details: {e}")
                            exp_at = "Failed To Fetch!"
                            days = "Failed To Parse!"
                            title = "Failed To Fetch!"

                        log.success(f"Valid -> {promocode} | Days Left: {days} | Expires At: {exp_at} | Title: {title}")
                        save("output/valid.txt", f"https://discord.com/billing/promotions/{promocode}")
                        valid_count.value += 1
                elif rs.status == 429:
                    try:
                        deta = await rs.json()
                        timetosleep = deta.get("retry_after", 60)
                        log.warn(f"Rate Limited For {timetosleep} Seconds!")
                        await asyncio.sleep(timetosleep)
                        await check(promocode, valid_count, claimed_count)
                    except Exception as e:
                        log.warn(f"Error handling rate limit: {e}")
                else:
                    log.warn(f"Invalid Code -> {promocode} with status code {rs.status}")

        except aiohttp.ClientError as e:
            log.warn(f"Client error: {e}")
        except Exception as e:
            log.warn(f"Unexpected error: {e}")

def sort_(file, item):
    with open(file, "r") as f:
        beamed = f.read().split("\n")
        try:
            beamed.remove("")
        except:
            pass
    return item in beamed

def save(file, data):
    with open(file, "a+") as f:
        if not sort_(file, data):
            f.write(data + "\n")
        else:
            pass

async def __UUID__(session):
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "user-agent": f"{ua.random}",
    }
    try:
        async with session.get(f"https://www.chess.com/member/{__NAME__()}", headers=headers, timeout=REQUEST_TIMEOUT) as r:
            text = await r.text()
            uuid = text.split('data-user-uuid="')[1].split('"')[0]
            log.info(f"Genning Promo --> {uuid[:15]}...")
            return uuid
    except asyncio.TimeoutError:
        log.warn("Timeout occurred while fetching UUID.")
        return None
    except Exception as e:
        log.warn(f"Error fetching UUID: {e}")
        return None

async def __GEN__(session, proxy, success_count, fail_count, valid_count, claimed_count):
    proxy_url = f"http://{proxy}"
    st = perf_counter()

    uuid = await __UUID__(session)
    if uuid is None:
        fail_count.value += 1
        return

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.chess.com",
        "user-agent": f"{ua.random}",
    }
    jData = {
        "userUuid": uuid,
        "campaignId": "4daf403e-66eb-11ef-96ab-ad0a069940ce",
    }

    try:
        async with session.post(
            "https://www.chess.com/rpc/chesscom.partnership_offer_codes.v1.PartnershipOfferCodesService/RetrieveOfferCode",
            json=jData,
            proxy=proxy_url,
            timeout=REQUEST_TIMEOUT
        ) as r:
            response = await r.json()
            code = response.get("codeValue")

            if code:
                promo = f'https://promos.discord.gg/{code}'
                log.success(f"Got Promo --> {promo}", round(perf_counter() - st, 2))
                await check(code, valid_count, claimed_count)

                with open('./output/promos.txt', 'a') as f:
                    f.write(f'\n{promo}')
                success_count.value += 1
            else:
                fail_count.value += 1
                log.warn("Failed to retrieve valid promo code.")

    except asyncio.TimeoutError:
        log.warn("Timeout occurred while retrieving promo.")
        fail_count.value += 1
    except Exception as e:
        log.warn(f"Error retrieving promo: {e}")
        fail_count.value += 1

async def gather_promos_for_process(proxy_batch, promo_count, success_count, fail_count, valid_count, claimed_count):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as session:
        tasks = []
        for proxy in proxy_batch:
            tasks.append(__GEN__(session, proxy, success_count, fail_count, valid_count, claimed_count))
        await asyncio.gather(*tasks)

def process_worker(proxies, promo_count, success_count, fail_count, valid_count, claimed_count):
    loop = asyncio.get_event_loop()
    proxy_batch = random.sample(proxies, promo_count)
    loop.run_until_complete(gather_promos_for_process(proxy_batch, promo_count, success_count, fail_count, valid_count, claimed_count))

def distribute_work_across_cpus(promo_count, proxies, success_count, fail_count, valid_count, claimed_count):
    num_cpus = cpu_count()
    log.info(f"Using {num_cpus} CPUs for processing...")
    promos_per_cpu = promo_count // num_cpus
    remainder = promo_count % num_cpus
    tasks = [promos_per_cpu] * num_cpus
    if remainder:
        tasks[-1] += remainder
    with Pool(num_cpus) as pool:
        pool.starmap(process_worker, zip(itertools.repeat(proxies), tasks, itertools.repeat(success_count), itertools.repeat(fail_count), itertools.repeat(valid_count), itertools.repeat(claimed_count)))

def __MAIN__():
    __CLS__()
    __LOGO__()

    proxies = load_proxies()
    promo_count = int(log.input("Promos --> "))

    total_start_time = perf_counter()

    with Manager() as manager:
        success_count = manager.Value('i', 0)
        fail_count = manager.Value('i', 0)
        valid_count = manager.Value('i', 0)
        claimed_count = manager.Value('i', 0)

        try:
            distribute_work_across_cpus(promo_count, proxies, success_count, fail_count, valid_count, claimed_count)
        except Exception as e:
            log.fail(f"An unexpected error occurred: {e}")

        total_time_taken = round(perf_counter() - total_start_time, 2)

        log.info(f"Total Promos Genned: {success_count.value}")
        log.warn(f"Total Failures: {fail_count.value}")
        log.info(f"Total Valid Promos: {valid_count.value}")
        log.warn(f"Total Claimed Promos: {claimed_count.value}")
        log.success(f"Total Time Taken: {total_time_taken}s")

if __name__ == '__main__':
    __MAIN__()
