
import signal
import atexit
import time

class TestObj:

    def __init__(self):
        self.emergency_stop = False

    def handle_exit(self, *args):
        try:
            print("2)I am catching the exit. I will do my termination job.")
            time.sleep(5)
            print("3) done!")
        except BaseException as exception:
            print(f"exception : {exception}")

    def register(self):
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def doing(self):
        print("1) I am doing my normal job.")
        time.sleep(10)
        print("I have done my normal job.")

def main2():
    to = TestObj()
    to.register()
    to.doing()

if __name__ == '__main__':
    # atexit.register(handle_exit)  ## It makes Keyboard Interrupt Error!
    main2()
    # signal.signal(signal.SIGTERM, to.handle_exit)
    # signal.signal(signal.SIGINT, to.handle_exit)


