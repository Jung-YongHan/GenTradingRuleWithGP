
import signal
import atexit
import time


def handle_exit(*args):
    try:
        print("2)I am catching the exit. I will do my termination job.")
        time.sleep(5)
        print("3) done!")
    except BaseException as exception:
        print(f"exception : {exception}")


if __name__ == '__main__':
    # atexit.register(handle_exit)  ## It makes Keyboard Interrupt Error!
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    print("1) I am doing my normal job.")
    time.sleep(10)
    print("I have done my normal job.")
