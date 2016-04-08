"""A simple command line interface.
It attempts to connect to a server, by default on the current machine
and then allows the user to enter commands"""
import cmd
import requests


class CommandLineInterface(cmd.Cmd):
    """A simple implementation of a CLI"""

    connection = {"url": "localhost", "port": 9000}
    connection_attempts = 0
    prompt = ">>> "

    def preloop(self):
        """Runs before the loop. Greets the user"""
        print("\n"
              "   ____    _    __  __    _    _   _ _____ _   _    _     ""\n"
              r"  / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    ""\n"
              r"  \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ""\n"
              r"   ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  ""\n"
              r"  |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ""\n"
              "                                                      hi~ ""\n"
              "  Starting up!\n")
        self.connect()

    def postloop(self):
        """Runs after the loop."""
        print("\n"
              "   ____    _    __  __    _    _   _ _____ _   _    _     ""\n"
              r"  / ___|  / \  |  \/  |  / \  | \ | |_   _| | | |  / \    ""\n"
              r"  \___ \ / _ \ | |\/| | / _ \ |  \| | | | | |_| | / _ \   ""\n"
              r"   ___) / ___ \| |  | |/ ___ \| |\  | | | |  _  |/ ___ \  ""\n"
              r"  |____/_/   \_\_|  |_/_/   \_\_| \_| |_| |_| |_/_/   \_\ ""\n"
              "                                                     bye~ ")

    def parseline(self, line):
        """Parses a line
        TODO: actually send the command to the server."""
        ret = cmd.Cmd.parseline(self, line)
        try:
            requests.post("http://{url}:{port}/command"
                          .format(**self.connection),
                          {"key": ret[0], "params": ret[1], "comm": ret[2]})
        except requests.ConnectionError:
            print "Connection lost."
            self.connection_error()
            return ("exit", "", "exit")
        print "processing " + str(ret)
        return ret

    def emptyline(self):
        pass

    def default(self, line):
        pass

    def precmd(self, line):
        return cmd.Cmd.precmd(self, line)

    def postcmd(self, stop, line):
        return cmd.Cmd.postcmd(self, stop, line)

    def do_exit(self, line):
        "Exit the interface"
        return True

    def do_EOF(self, line):
        "Exit the interface"
        return True

    def connect(self):
        """attept connecting to an instance of Samantha"""
        print("Attempting to connect to 'http://{url}:{port}'"
              .format(**self.connection))
        try:
            requests.get("http://{url}:{port}/status"
                         .format(**self.connection))
            self.connection_attempts = 0
            print "Connection available."
        except requests.ConnectionError:
            self.connection_error()

    def connection_error(self):
        """Handle a failed connection. The program will abort after 3
        failed attempts to the same server."""
        self.connection_attempts += 1
        if self.connection_attempts >= 3:
            print "The connection failed 3 times in a row. Exiting."
            self.postloop()
            exit()
        print("The Connection to 'http://{url}:{port}/status' failed."
              .format(**self.connection))
        var = raw_input("Try to start the server remotely? (y/n) \n>>> ")
        while var not in ["y", "n"]:
            var = raw_input("Please use 'y' for yes or 'n' for no. \n>>> ")
        if var == "y":
            # Start remotely
            pass
        elif var == "n":
            var = raw_input("Enter a new host? (y/n) \n>>> ")
            while var not in ["y", "n"]:
                var = raw_input(
                    "Please use 'y' for yes or 'n' for no. \n>>> ")
            if var == "y":
                self.connection_attempts = 0
                self.connection["url"] = raw_input(
                    "Please enter the new host: ")
        self.connect()


def start():
    """Starts the interface"""
    CommandLineInterface().cmdloop("Please enter your command:")
