# -------------
# switch.py
# -------------
#	Last update: 2021/11/19 T. Fujisawa
#	This script calcuates the switching time of each JJs.

# -------------
# Example
# ------------
#	python switch.py

# -------------
# Notice
# ------------
#   The name of the inp file must be "si.inp".
#	The phase of each JJs needs to be monitored and you must not add other components which have nothing to do with them.
#   You have to put the input pattern you want to calcuate at the beginning of the simulation.
#	You have to change the input pattern by yourself to calcuate different patterns.


# ------------
# Module	From the top: libraries for regular expressions, console usage, arithmetic operations (pi, etc), and matrix calcuation.
# ------------
import re
import sys
from subprocess import *
from math import *
import numpy as np


# --------------------
# Commands on shell
# --------------------
def shell(s):
    p = Popen(s, shell=True)
    p.wait()


# --------------
# Pattern check of a.txt and si.inp
# --------------
def checka(s):		# search "~e+~" or "~e-~"
    p = re.compile(r'.e[-,+].')
    return p.search(s)


# --------------------
# Execute jsim
# --------------------
def exe(str):
    s = "jsim_n " + str + " > a.txt"
    shell(s)


# --------------------
# Switching time
# --------------------
def switch():
    f1 = open("a.txt", "r")
    initial = 0
    number_of_monitored = 0
    for line in f1.readlines():
        a = line.split()
        if a == []:
            continue
        elif checka(a[0]) != None:
            if initial == 0:
                initial = a
                number_of_monitored = len(a) - 1
                switchlist = np.zeros(number_of_monitored)
            else:
                for i, (phase, initial_phase) in enumerate(zip(a, initial)):
                    if i == 0:
                        continue
                    elif (float(phase) - float(initial_phase)) / pi > 1 and switchlist[i - 1] == 0:
                        switchlist[i - 1] = a[0]
                    else:
                        continue
    f1.close()
    return switchlist


# --------------------
# Main
# --------------------
def main():
    if len(sys.argv) <= 1:
        exe("si.inp")
    else:
        exe(sys.argv[1])
    switchlist = np.sort(switch())
    interval = np.diff(switchlist)
    with open("switch_time.txt", "w") as f:
        f.write(
            f"switch: {str(switchlist * 1e12) + 'ps'}\ninterval: {str(interval * 1e12) + 'ps'}\n")
        f.write(
            f"latency: {(switchlist[len(switchlist) - 1] - switchlist[0]) * 1e12} ps")
    print(
        f"switch: {str(switchlist * 1e12) + 'ps'}\ninterval: {str(interval * 1e12) + 'ps'}\n")
    print(
        f"latency: {(switchlist[len(switchlist) - 1] - switchlist[0]) * 1e12} ps")
    shell("rm a.txt")
    shell("del a.txt")


if __name__ == "__main__":
    main()
