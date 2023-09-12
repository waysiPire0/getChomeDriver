import os, zipfile, string, random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def get_background_js_str(PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS):
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
                    """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)
    return manifest_json,background_js

def get_driver_path():
    driver_path = ChromeDriverManager().install()
    return driver_path

def generate_random_string(length=8):
    characters = string.ascii_letters + string.digits  # You can also add more characters if needed
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def get_driver(user_profile_path,proxy=None):
    print("** Launching driver..")

    options = Options()
    options.add_argument("–lang= en")

    if proxy:
        print("** Using proxies -> ", proxy)

        if len(proxy.split(":"))>2: # proxy = "HOST:PORT:USERNAME:PASSWORD"
            arr = proxy.split(":")
            proxiesZipFolder = os.path.join(os.getcwd(),'proxies_zip')
            if not os.path.exists(proxiesZipFolder):
                os.mkdir(proxiesZipFolder)
            random_name = generate_random_string() + '.zip'
            pluginfile = os.path.join(proxiesZipFolder,random_name)
            manifest_json,background_js = get_background_js_str(arr[0],arr[1],arr[2],arr[3])
            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(pluginfile)
        else:  # proxy = "HOST:PORT"
            options.add_argument('--proxy-server=%s' % proxy)
    else:
        print("** Continue without proxies...")


    if not os.path.exists(user_profile_path): os.mkdir(user_profile_path)

    options.add_argument("user-data-dir={}".format(user_profile_path))
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driverPath = get_driver_path()
    
    dr =  webdriver.Chrome(options=options)
    
    return dr



if __name__ == "__main__":
    profilePath = os.path.join(os.getcwd(),'my-profile')
    
    driver = get_driver(profilePath)

    driver.get("https://www.google.com")

    print("** DONE ")

    while 1: pass