from colorama import Fore, Style
import os
import datetime

colors = {
    "gray": Fore.LIGHTBLACK_EX,
    "orange": Fore.LIGHTYELLOW_EX,
    "lightblue": Fore.LIGHTCYAN_EX,
    "purple": Fore.LIGHTMAGENTA_EX,
    "green": Fore.LIGHTGREEN_EX,
    "yellow": Fore.LIGHTYELLOW_EX,
    "red": Fore.LIGHTRED_EX,
    "reset": Style.RESET_ALL
}

symbols = {
    "success": "✅",
    "fail": "❌",
    "info": "ℹ️",
    "warn": "⚠️",
    "working": "⏳",
    "input": "⌨️"
}

class Console_UI:
    @staticmethod
    def _get_timestamp():
        """Get the current timestamp in a nice format."""
        return datetime.datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def _center(text):
        try:
            t_width = os.get_terminal_size().columns
        except OSError:
            t_width = 80  

        textlen = len(text)
        if textlen >= t_width:
            return text
        l_pad = (t_width - textlen) // 2
        return ' ' * l_pad + text

    @staticmethod
    def _formatted_log(symbol, color, message, time=None):
        timestamp = Console_UI._get_timestamp()
        msg = f"{colors['gray']}[{colors['purple']}{timestamp}{colors['gray']}]"
        msg += f" {color}{symbol} {message}"
        if time:
            msg += f" {colors['gray']}[{colors['lightblue']}{time:.2f}s{colors['gray']}]"
        print(Console_UI._center(msg + colors['reset']))

    @staticmethod
    def success(message, time=0):
        Console_UI._formatted_log(symbols['success'], colors['green'], message, time)

    @staticmethod
    def fail(message):
        Console_UI._formatted_log(symbols['fail'], colors['red'], message)

    @staticmethod
    def warn(message):
        Console_UI._formatted_log(symbols['warn'], colors['yellow'], message)

    @staticmethod
    def info(message):
        Console_UI._formatted_log(symbols['info'], colors['lightblue'], message)

    @staticmethod
    def working(message):
        Console_UI._formatted_log(symbols['working'], colors['orange'], message)

    @staticmethod
    def input(message):
        timestamp = Console_UI._get_timestamp()
        msg = f"{colors['gray']}[{colors['purple']}{timestamp}{colors['gray']}] {colors['lightblue']}{symbols['input']} {message}"
        centered_msg = Console_UI._center(msg)
        return input(centered_msg + " " + colors['reset'])


