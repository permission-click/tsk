#!/usr/bin/python3

import os
import platform
import json
import argparse
from getch import getch
from process import Process
from time import sleep
from math import ceil, log


processes = []
log_dir = os.path.join('~', '.tsk.logs')


def main(config):
    with open(config, 'r') as f:
        config = json.load(f)

    # Prepare log directory
    global log_dir
    log_dir = config.get('logs', log_dir)
    log_dir = os.path.expanduser(log_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    try:
        # Create process objects
        processes.extend(
            Process(**p, log_dir=log_dir) for p in config.get('processes', {})
        )

        if not processes:
            print('No processes to manage.')
            return

        # Main menu loop
        done = False
        prompt = '\nSelect a process to stop or start: '
        while not done:
            menu()

            if len(processes) > 9:
                selection = input(prompt).lower()
            else:
                print(prompt)
                selection = getch().decode('utf-8').lower()

            done = select(selection)

    finally:
        for process in processes:
            process.cleanup()


def clear():
    os.system('cls' if platform.system() == 'Windows' else 'clear')


def open_path(path):
    if platform.system() == 'Windows':
        os.startfile(path)
    elif platform.system() == 'Darwin':
        subprocess.Popen(['open', path])
    else:
        subprocess.Popen(['xdg-open', path])


def width(items, min_length=0):
    return max(min_length, *(len(i) for i in items)) if items else min_length


def menu():
    clear()
    print('TSK PROCESS MANAGER\n')

    iw = ceil(log(len(processes) + 1, 10))
    nw = width((p.name for p in processes), 15)
    sw = width(p.status for p in processes)
    lw = width(p.log_file for p in processes)

    print(
        f'{" " * iw}  {"PROCESS":{nw}}   {"STATUS":{sw}}   {"LOG FILE":{lw}}'
    )
    for i, process in enumerate(processes):
        print(
            f'{i + 1:>{iw}}: {process.name:{nw}}   '
            f'{process.status:{sw}}   {process.log_file:{lw}}'
        )

    print(f'\n{"L":>{iw}}: View Logs')
    print(f'{"Q":>{iw}}: Quit')


def select(selection):
    if selection == 'q':
        return True

    if selection == 'l':
        open_path(log_dir)
        return False

    try:
        process = processes[int(selection) - 1]
    except:
        return False

    process.toggle()
    sleep(1)
    return False


if __name__ == '__main__':
    default_config = os.path.expanduser(os.path.join('~', '.tsk.json'))

    parser = argparse.ArgumentParser()
    parser.add_argument('config', nargs='?', default=default_config)
    args = parser.parse_args()

    main(args.config)
