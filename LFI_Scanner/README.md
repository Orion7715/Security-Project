# LFI-AutoScanner

**LFI-AutoScanner** is an automated reconnaissance and exploitation tool designed to identify **Local File Inclusion (LFI)** vulnerabilities in web applications. It leverages advanced techniques, including PHP Filter Chain generation, to test for potential Remote Code Execution (RCE).



---

## ⚠️ Legal Disclaimer
This tool is intended for **educational purposes and authorized security testing only**. The developer assumes no liability and is not responsible for any misuse or damage caused by this program. Use it only on systems you have explicit, written permission to test.

---

## 🚀 Features
* **Automated Fuzzing:** Tests a wide array of path traversal payloads and bypass techniques.
* **PHP Filter Chain Generator:** Automatically constructs complex filter chains to attempt to bypass restrictions and achieve RCE.
* **System Enumeration:**
    * Automatically extracts usernames from `/etc/passwd`.
    * Searches for user SSH keys (`id_rsa`, `authorized_keys`, etc.).
    * Checks for common user shell history files (`.bash_history`, `.zsh_history`).
* **Log Poisoning Detection:** Tests common paths for Apache/HTTPD logs to identify potential RCE vectors.
* **RFI Detection:** Checks if the server allows Remote File Inclusion via external links.
* **Interactive Shell:** Provides an easy-to-use interactive shell if an RCE vulnerability is confirmed.

---

## 📋 Prerequisites
Ensure you have Python 3 installed. Install the required dependencies using:

```bash
pip install requests colorama
```

### ⚙️ Usage

```
python lfi_scanner.py -u "[http://target.com/index.php?file=](http://target.com/index.php?file=)" -f "index.php" -c "PHPSESSID=your_session_id"
```
| Argument | Description |
| :--- | :--- |
| `-u` / `--url` | The target URL (must include the vulnerable parameter). |
| `-f` / `--file` | A path to a known existing file on the server. |
| `-c` / `--cookie` | (Optional) Cookie header for authenticated sessions. |


Contributing

Contributions are highly encouraged! If you have suggestions for new bypass patterns, better detection logic, or bug fixes, please submit a Pull Request or open an Issue.
