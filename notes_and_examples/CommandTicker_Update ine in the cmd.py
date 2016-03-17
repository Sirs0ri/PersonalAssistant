class CommandTicker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        ticks = ['[.  ]', '[.. ]', '[...]', '[ ..]', '[  .]', '[   ]']
        i = 0
        first = True
        while True:
            self.stop_event.wait(0.25)
            if self.stop_event.isSet(): break
            if i == len(ticks):
                first = False
                i = 0
                if not first:
                    sys.stderr.write("\r%s\r" % ticks[i])
                    sys.stderr.flush()
                i += 1
            sys.stderr.flush()
            
ticker_thread = CommandTicker()
ticker_thread.start()
ticker_thread.stop()
ticker_thread.join()