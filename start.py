import sys
import samantha

if __name__ == "__main__":
    if "--debug" in sys.argv or "-D" in sys.argv:
        DEBUG = True
    else:
        DEBUG = False
    samantha.run(DEBUG)