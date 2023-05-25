"""Multi thread"""
# threader.py

from threading import Thread

def threader(func_name, func_args):
    """Thread for list"""

    thread_list = []

    for argument in func_args:
        worker = Thread(target=func_name, args=(argument,))
        thread_list.append(worker)

    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

def main():
    """Main"""

if __name__ == "__main__":
    main()
