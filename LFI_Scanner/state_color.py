BLACK = "\033[30m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"

# (Background)
BG_BLACK = "\033[40m"
BG_RED = "\033[41m"
BG_GREEN = "\033[42m"
BG_YELLOW = "\033[43m"
BG_BLUE = "\033[44m"
BG_MAGENTA = "\033[45m"
BG_CYAN = "\033[46m"
BG_WHITE = "\033[47m"

# (Bright)
BRED = "\033[91m"
BGREEN = "\033[92m"
BYELLOW = "\033[93m"
BBLUE = "\033[94m"
BMAGENTA = "\033[95m"
BCYAN = "\033[96m"
BWHITE = "\033[97m"

# (Reset)
RESET = "\033[0m"

# Extra
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
REVERSED = "\033[7m"


INFO     = f"{BCYAN}[-]{RESET}"
SUCCESS  = f"{BGREEN}[+]{RESET}"
WARN     = f"{BYELLOW}[?]{RESET}"
PAYLOADC = f"{BMAGENTA}[*]{RESET} Payload -> "
LINE = f"{BWHITE}_{RESET}" * 50
ERROR = f"{BRED}[-]{RESET}"
