from subprocess import run
from display import Display

class ConsoleDisplay(Display):
    def write(self, message, color=None):
        self.clear()
        print(message)

    def clear(self):
        run('clear')