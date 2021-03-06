#!/usr/bin/env python

from __future__ import print_function

import os
import re
import sys
import atexit
from collections import deque

# Pre-checks for dependencies

missing = []
try:
    import matplotlib
except ImportError:
    if sys.version_info[0] == 2:
        missing.append('python-matplotlib')
    else:
        missing.append('python3-matplotlib')

if sys.version_info[0] == 2:
    try:
        # TkAgg
        import Tkinter
    except ImportError:
        missing.append('python-tk')
else:
    xrange = range
    try:
        # TkAgg
        import tkinter
    except ImportError:
        missing.append('python3-tk')

if os.system('which sensors') != 0:
    missing.append('lm-sensors')

if missing:
    packages = ' '.join(missing)
    print('Missing some packages:', packages)
    print('Install them and run again.')
    os.system('sudo apt-get install ' + packages)
    exit()

number_with_plus_after_colon = ':\s*\+([\d\.]+)'


def sensor_names():
    last_sensor = None
    sensors = []

    for line in os.popen('sensors').read().split('\n'):
        if ':' not in line and line.strip() and line[0] != ' ':
            last_sensor = line.strip()
            continue
        if last_sensor and re.findall(number_with_plus_after_colon, line):
            sensors.append(last_sensor)

    return sensors


def cpu_temps():
    """Run sensors program and parse temperatures."""
    dta = os.popen('sensors').read()
    return list(map(float, re.findall(number_with_plus_after_colon, dta)))


def cpu_freq():
    dta = open('/proc/cpuinfo').read()
    return map(float, re.findall('cpu MHz\s*:\s*([\d\.]+)', dta))


def temp_graph():
    """Animate a graph with temperatures from sensors output."""
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.pyplot import plot, show, figure, draw, axis
    from time import time, sleep
    from threading import Thread
    sensors = sensor_names()
    print(' '.join(sensors))
    init_temps = cpu_temps()
    window = [deque([i] * 300) for i in init_temps]
    fig = figure()
    ax = fig.add_subplot(111)
    lines = [ax.plot(win, label=sensor)[0] for win, sensor in zip(window, sensors)]
    ax.axis([0, 300,
             min(30, min(init_temps) - 10),
             max(60, max(init_temps) + 10)])
    ax.legend(handles=lines, loc='lower left')

    def update():
        if update.live and fig.canvas.manager.window:
            temps = cpu_temps()
            print('Current temperatures: '
                  + ', '.join('{:4.1f}'.format(t) for t in temps), end='\r')
            sys.stdout.flush()
            for win, temp, line in zip(window, temps, lines):
                win.append(temp)
                win.popleft()
                line.set_ydata(win)
            fig.canvas.draw()
            fig.canvas.manager.window.after(1000, update)

    update.live = True
    fig.canvas.manager.window.after(1000, update)

    def toggle(event):

        if update.live:
            update.live = False
        else:
            update.live = True
            fig.canvas.manager.window.after(100, update)

    fig.canvas.mpl_connect('key_press_event', toggle)
    atexit.register(print)  # prevent last temperature wipeout
    show()


if __name__ == '__main__':
    temp_graph()
