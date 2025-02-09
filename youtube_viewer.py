"""
MIT License

Copyright (c) 2021 MShawon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import concurrent.futures.thread
import os
import platform
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from random import choice, uniform
from time import gmtime, sleep, strftime

import requests
import undetected_chromedriver as uc
from fake_headers import Headers
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

os.system("")


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


print(bcolors.OKGREEN + """

Yb  dP  dP"Yb  88   88 888888 88   88 88""Yb 888888                   
 YbdP  dP   Yb 88   88   88   88   88 88__dP 88__                     
  8P   Yb   dP Y8   8P   88   Y8   8P 88""Yb 88""                     
 dP     YbodP  `YbodP'   88   `YbodP' 88oodP 888888  

                        Yb    dP 88 888888 Yb        dP 888888 88""Yb 
                         Yb  dP  88 88__    Yb  db  dP  88__   88__dP 
                          YbdP   88 88""     YbdPYbdP   88""   88"Yb  
                           YP    88 888888    YP  YP    888888 88  Yb 
""" + bcolors.ENDC)

print(bcolors.OKCYAN + """
           [ GitHub : https://github.com/MShawon/YouTube-Viewer ]
""" + bcolors.ENDC)

SCRIPT_VERSION = '1.3.1'

api_url = 'https://api.github.com/repos/MShawon/YouTube-Viewer/releases/latest'
response = requests.get(api_url, timeout=30)

RELEASE_VERSION = response.json()['tag_name']

if SCRIPT_VERSION != RELEASE_VERSION:
    print(bcolors.BOLD + 'Update Available!!! ' +
          f'YouTube Viewer version {SCRIPT_VERSION} needs to update to {RELEASE_VERSION} version.' + bcolors.ENDC)


proxy = None
driver = None
status = None
reload_proxy = False
auth_required = False

view = []
duration_dict = {}
checked = {}

VIEWPORT = ['2560,1440', '1920,1080', '1440,900',
            '1536,864', '1366,768', '1280,1024', '1024,768']

print(bcolors.WARNING + 'Getting Chrome Driver...' + bcolors.ENDC)

OSNAME = platform.system()

"""
Getting Chrome version code has been taken from 
https://github.com/yeongbin-jo/python-chromedriver-autoinstaller
Thanks goes to him.
"""
if OSNAME == 'Linux':
    OSNAME = 'lin'
    with subprocess.Popen(['google-chrome', '--version'], stdout=subprocess.PIPE) as proc:
        version = proc.stdout.read().decode('utf-8').replace('Google Chrome', '').strip()
elif OSNAME == 'Darwin':
    OSNAME = 'mac'
    process = subprocess.Popen(
        ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '--version'], stdout=subprocess.PIPE)
    version = process.communicate()[0].decode(
        'UTF-8').replace('Google Chrome', '').strip()
elif OSNAME == 'Windows':
    OSNAME = 'win'
    process = subprocess.Popen(
        ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL
    )
    version = process.communicate()[0].decode('UTF-8').strip().split()[-1]
else:
    print('{} OS is not supported.'.format(OSNAME))
    sys.exit()

major_version = version.split('.')[0]

uc.TARGET_VERSION = major_version

uc.install()

try:
    os.makedirs('extension')
except OSError:
    pass


class UrlsError(Exception):
    pass


class SearchError(Exception):
    pass


class QueryError(Exception):
    pass


def timestamp():
    date_fmt = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    return bcolors.OKGREEN + f'[{date_fmt}] '


def load_url():
    links = []
    print(bcolors.WARNING + 'Loading urls...' + bcolors.ENDC)
    filename = 'urls.txt'
    load = open(filename)
    loaded = [items.rstrip().strip() for items in load]
    load.close()

    for lines in loaded:
        links.append(lines)

    print(bcolors.OKGREEN +
          f'{len(links)} url loaded from urls.txt' + bcolors.ENDC)

    return links


def load_search():
    search = []
    print(bcolors.WARNING + 'Loading queries...' + bcolors.ENDC)
    filename = 'search.txt'
    load = open(filename, encoding="utf-8")
    loaded = [items.rstrip().strip() for items in load]
    loaded = [[i.strip() for i in items.split('::::')] for items in loaded]
    load.close()

    for lines in loaded:
        search.append(lines)

    print(bcolors.OKGREEN +
          f'{len(search)} query loaded from search.txt' + bcolors.ENDC)

    return search


def gather_proxy():
    proxies = []
    print(bcolors.OKGREEN + 'Scraping proxies ...' + bcolors.ENDC)

    link_list = ['https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
                 'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
                 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt',
                 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt',
                 'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt',
                 'https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt']

    for link in link_list:
        response = requests.get(link)
        output = response.content.decode()
        proxy = output.split('\n')
        proxies = proxies + proxy
        print(bcolors.OKGREEN +
              f'{len(proxy)} proxies gathered from {link}' + bcolors.ENDC)

    return proxies


def load_proxy():
    proxies = []

    filename = input(bcolors.OKBLUE +
                     'Enter your proxy file name: ' + bcolors.ENDC)
    load = open(filename)
    loaded = [items.rstrip().strip() for items in load]
    load.close()

    for lines in loaded:
        proxies.append(lines)

    return proxies


def check_proxy(agent, proxy, proxy_type):
    if category == 'f':
        headers = {
            'User-Agent': f'{agent}',
        }

        proxyDict = {
            "http": f"{proxy_type}://{proxy}",
            "https": f"{proxy_type}://{proxy}",
        }
        response = requests.get(
            'https://www.youtube.com/', headers=headers, proxies=proxyDict, timeout=30)
        status = response.status_code

    else:
        status = 200

    return status


def get_driver(agent, proxy, proxy_type, pluginfile):
    options = webdriver.ChromeOptions()
    options.headless = background
    options.add_argument(f"--window-size={choice(VIEWPORT)}")
    options.add_argument("--log-level=3")
    options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument(f"user-agent={agent}")
    options.add_argument("--mute-audio")
    options.add_argument("--disable-web-security")
    webdriver.DesiredCapabilities.CHROME['loggingPrefs'] = {
        'driver': 'OFF', 'server': 'OFF', 'browser': 'OFF'}

    if auth_required:
        proxy = proxy.replace('@', ':')
        proxy = proxy.split(':')
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            },
            "minimum_chrome_version":"22.0.0"
        }
        """

        background_js = """
        var config = {
                mode: "fixed_servers",
                rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
                }
            };

        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }

        chrome.webRequest.onAuthRequired.addListener(
                    callbackFn,
                    {urls: ["<all_urls>"]},
                    ['blocking']
        );
        """ % (proxy[2], proxy[-1], proxy[0], proxy[1])

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)

    else:
        options.add_argument(f'--proxy-server={proxy_type}://{proxy}')

    driver = webdriver.Chrome(options=options)

    return driver


def bypass_consent(driver):
    try:
        consent = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(
            (By.XPATH, "//input[@type='submit' and @value='I agree']")))
        driver.execute_script("arguments[0].scrollIntoView();", consent)
        consent.submit()
    except:
        consent = driver.find_element_by_css_selector(
            'button.VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ.VfPpkd-LgbsSe-OWXEXe-dgl2Hf.nCP5yc.AjY5Oe.DuMIQc.IIdkle')
        driver.execute_script("arguments[0].scrollIntoView();", consent)
        consent.click()



def search_video(driver, video_title):
    i = 1
    for i in range(1, 11):
        try:
            section = WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
                (By.XPATH, f'//ytd-item-section-renderer[{i}]')))
            find_video = section.find_element_by_xpath(
                f'//*[@title="{video_title}"]')
            find_video.click()
            break
        except NoSuchElementException:
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                (By.TAG_NAME, 'body'))).send_keys(Keys.CONTROL, Keys.END)
            sleep(5)

    return i


def check_state(driver):
    try:
        driver.find_element_by_css_selector('[title^="Pause (k)"]')
    except:
        try:
            driver.find_element_by_css_selector(
                'button.ytp-large-play-button.ytp-button').send_keys(Keys.ENTER)
        except:
            try:
                driver.find_element_by_css_selector('[title^="Play (k)"]').click()
            except:
                driver.execute_script(
                    "document.querySelector('button.ytp-play-button.ytp-button').click()")



def skip_initial_ad(driver, position):
    try:
        skip_ad = WebDriverWait(driver, 45).until(EC.element_to_be_clickable(
            (By.CLASS_NAME, "ytp-ad-skip-button-container")))
        if skip_ad:
            print(timestamp() + bcolors.OKBLUE +
                  f"Tried {position+1} | Skipping Ads..." + bcolors.ENDC)
            ad_duration = driver.find_element_by_class_name(
                'ytp-time-duration').get_attribute('innerText')
            ad_duration = sum(x * int(t)
                              for x, t in zip([60, 1], ad_duration.split(":")))
            ad_duration = ad_duration * uniform(.01, .1)
            sleep(ad_duration)
            skip_ad.click()
    except:
        pass


def quit_driver(driver, pluginfile):
    try:
        os.remove(pluginfile)
    except:
        pass

    driver.quit()
    status = 400
    return status


def sleeping():
    sleep(30)


def main_viewer(proxy_type, proxy, position):
    try:

        checked[position] = None

        header = Headers(
            browser="chrome",
            os=OSNAME,
            headers=False
        ).generate()
        agent = header['User-Agent']

        status = check_proxy(agent, proxy, proxy_type)

        if status == 200:
            try:
                print(timestamp() + bcolors.OKBLUE + f"Tried {position+1} | " + bcolors.OKGREEN +
                      f"{proxy} | {proxy_type} --> Good Proxy | Searching for videos..." + bcolors.ENDC)

                pluginfile = os.path.join(
                    'extension', f'proxy_auth_plugin{position}.zip')

                driver = get_driver(agent, proxy, proxy_type, pluginfile)
                url = ''

                if position % 2:
                    try:
                        method = 1
                        url = choice(urls)
                    except:
                        raise UrlsError

                else:
                    try:
                        method = 2
                        query = choice(queries)
                        keyword = query[0]
                        video_title = query[1]
                        url = f"https://www.youtube.com/results?search_query={keyword.replace(' ', '+')}"
                    except:
                        raise SearchError

                # driver.get('https://ipof.me')
                # sleep(30)

                driver.get(url)

                if 'consent' in driver.current_url:
                    print(timestamp() + bcolors.OKBLUE +
                          f"Tried {position+1} | Bypassing consent..." + bcolors.ENDC)
                    bypass_consent(driver)

                try:
                    driver.execute_script("""
                    (function myLoop(i) {
                    setTimeout(function() {
                        try{
                            var nothanks, iagree;
                            nothanks = document.getElementsByClassName('style-scope yt-button-renderer style-text size-small')[0];
                            nothanks.click()
                            iagree = document.getElementsByTagName('iframe')[1].contentDocument.getElementById('introAgreeButton');
                            iagree.click()
                        }
                        catch(err){
                            try{
                                iagree = document.getElementsByTagName('iframe')[1].contentDocument.getElementById('introAgreeButton');
                                iagree.click()
                            }
                            catch(err){
                            }

                        }
                        if (--i) myLoop(i);
                    }, 3000)
                    })(10);
                    """)

                except:
                    pass

                if method == 1:
                    skip_initial_ad(driver, position)

                else:
                    scroll = search_video(driver, video_title)
                    if scroll == 10:
                        raise QueryError

                    skip_initial_ad(driver, position)

                check_state(driver)

                try:
                    video_len = duration_dict[url]
                except KeyError:
                    video_len = 0
                    while video_len == 0:
                        video_len = driver.execute_script(
                            "return document.getElementById('movie_player').getDuration()")

                    duration_dict[url] = video_len

                video_len = video_len*uniform(.85, .95)

                duration = strftime("%Hh:%Mm:%Ss", gmtime(video_len))
                print(timestamp() + bcolors.OKBLUE + f"Tried {position+1} | " + bcolors.OKGREEN +
                      f"{proxy} --> Video Found : {url} | Watch Duration : {duration} " + bcolors.ENDC)

                check_state(driver)

                sleep(video_len)
                driver.quit()

                view.append(position)
                print(timestamp() + bcolors.OKCYAN +
                      f'View added : {len(view)}' + bcolors.ENDC)

                status = quit_driver(driver, pluginfile)

            except UrlsError:
                print(timestamp() + bcolors.FAIL +
                      f"Tried {position+1} | Your urls.txt is empty!" + bcolors.ENDC)
                status = quit_driver(driver, pluginfile)
                pass

            except SearchError:
                print(timestamp() + bcolors.FAIL +
                      f"Tried {position+1} | Your search.txt is empty!" + bcolors.ENDC)
                status = quit_driver(driver, pluginfile)
                pass

            except QueryError:
                print(timestamp() + bcolors.FAIL +
                      f"Tried {position+1} | Can't find this [{video_title}] video with this keyword [{keyword}]" + bcolors.ENDC)
                status = quit_driver(driver, pluginfile)
                pass

            except Exception as e:
                *_, exc_tb = sys.exc_info()
                print(timestamp() + bcolors.FAIL +
                      f"Tried {position+1} | Line : {exc_tb.tb_lineno} | " + str(e) + bcolors.ENDC)
                status = quit_driver(driver, pluginfile)
                pass

    except:
        print(timestamp() + bcolors.OKBLUE + f"Tried {position+1} | " +
              bcolors.FAIL + f"{proxy} | {proxy_type} --> Bad proxy " + bcolors.ENDC)
        checked[position] = proxy_type
        pass


def view_video(position):
    proxy = proxy_list[position]

    if category == 'f':
        main_viewer('http', proxy, position)
        if checked[position] == 'http':
            main_viewer('socks4', proxy, position)
        if checked[position] == 'socks4':
            main_viewer('socks5', proxy, position)

    else:
        main_viewer(proxy_type, proxy, position)


def main():
    pool_number = [i for i in range(total_proxies)]

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(view_video, position)
                   for position in pool_number]

        try:
            for future in as_completed(futures):
                if len(view) == views:
                    print(
                        bcolors.WARNING + f'Amount of views added : {views} | Stopping program...' + bcolors.ENDC)
                    executor._threads.clear()
                    concurrent.futures.thread._threads_queues.clear()
                    break
                future.result()

        except KeyboardInterrupt:
            executor._threads.clear()
            concurrent.futures.thread._threads_queues.clear()


if __name__ == '__main__':

    urls = load_url()
    queries = load_search()

    views = int(input(bcolors.OKBLUE + 'Amount of views : ' + bcolors.ENDC))

    category = input(bcolors.WARNING + "What's your proxy category? " +
                     "[F = Free (without user:pass), P = Premium (with user:pass), R = Rotating Proxy] : " + bcolors.ENDC).lower()

    if category == 'f':
        handle_proxy = str(input(
            bcolors.OKBLUE + 'Let YouTube Viewer handle proxies ? [Y/n] : ' + bcolors.ENDC)).lower()

        if handle_proxy == 'y' or handle_proxy == 'yes' or handle_proxy == '':
            reload_proxy = True
            proxy_list = gather_proxy()
        else:
            proxy_list = load_proxy()

    elif category == 'p' or category == 'r':
        if category == 'r':
            proxy = input(bcolors.OKBLUE +
                          'Enter your Rotating Proxy service Main Gateway : ' + bcolors.ENDC)
            proxy_list = [proxy]
            proxy_list = proxy_list * 100000

            if '@' in proxy:
                auth_required = True
                proxy_type = 'http'
            else:
                handle_proxy = str(input(
                    bcolors.OKBLUE + "Select proxy type [1 = HTTP , 2 = SOCKS4, 3 = SOCKS5] : " + bcolors.ENDC)).lower()

                if handle_proxy == '1':
                    proxy_type = 'http'
                elif handle_proxy == '2':
                    proxy_type = 'socks4'
                elif handle_proxy == '3':
                    proxy_type = 'socks5'
                else:
                    print(
                        'Please input 1 for HTTP, 2 for SOCKS4 and 3 for SOCKS5 proxy type')
                    sys.exit()
        else:
            proxy_list = load_proxy()
            auth_required = True
            proxy_type = 'http'

    else:
        print('Please input F for Free, P for Premium and R for Rotating proxy')
        sys.exit()

    proxy_list = list(filter(None, proxy_list))  # removing empty lines

    total_proxies = len(proxy_list)

    if category != 'r':
        print(bcolors.OKCYAN +
              f'Total proxies : {total_proxies}' + bcolors.ENDC)

    gui = str(input(
        bcolors.WARNING + 'Do you want to run in headless(background) mode? (recommended=No) [No/yes] : ' + bcolors.ENDC)).lower()

    if gui == 'n' or gui == 'no' or gui == '':
        background = False
    else:
        background = True

    threads = int(
        input(bcolors.OKBLUE+'Threads (recommended = 5): ' + bcolors.ENDC))

    check = -1
    while len(view) < views:
        try:
            check += 1
            if check == 0:
                main()
            else:
                sleeping()
                print(bcolors.WARNING +
                      f'Total Checked : {check} times' + bcolors.ENDC)
                if reload_proxy:
                    proxy_list = gather_proxy()
                    proxy_list = list(filter(None, proxy_list))
                    total_proxies = len(proxy_list)
                main()
        except KeyboardInterrupt:
            sys.exit()
