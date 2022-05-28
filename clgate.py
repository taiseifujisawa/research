# -------------
# clgate.py
# -------------
#	Last update: 2021/11/19 T. Fujisawa
#	This script calcuates the maximum input skew or the latency on several conditions.

# -------------
# Example
# ------------
#	python clgate.py a
#		calcuates the maximum input skew of clockless AND gate.
#	python clgate.py o
#		calcuates the maximum input skew of clockless OR gate.
#	python clgate.py x
#		calcuates the maximum input skew of clockless XOR gate.
#	python clgate.py l
#		calcuates the latency from the input JJ switching to the output JJ switching for every gate.
#	python clgate.py ls
#		calcuates the dependence of the latency from the input JJ switching to the output JJ switching on the input skew for the "11" input pattern.
#	python clgate.py lb
#		calcuates the dependence of the latency from the input JJ switching to the output JJ switching on the bias voltage for every gate.

# -------------
# Notice
# ------------
# general:	The name of the inp file must be "si.inp".
# a, o, x:	You have to set the ONLY 2 input sfq pulses arriving simultaniously.
#			You have to name one of two input voltage sources "Vc". The input time of the voltage source named "Vc" is changed.
#			The phase of the input JJ of the one changing the input time and the output JJ needs to be monitored from the top and in this order.
#			If it does not work, you may want to make the value of variable "initial_skew" smaller. When it is large, this program will last shorter, but it may cause the problem.
#			Or, you may want to make the duration of the simulation longer. The duration of 200 ps is probably long enough.
# l:		You have to put the input pattern you want to calcuate at the beginning of the simulation.
#			You have to change the input pattern by yourself to calcuate different patterns.
#			If no output JJ switching is monitored, N/A is displayed.
#			You can change the bias voltage on the console.
# ls:		This is for the "11" input pattern. Thus, this is not available for XOR gate etc.
#			You have to set the ONLY 2 input sfq pulses arriving simultaniously.
#			You can change the bias voltage on the console.
# lb:		You have to put the input pattern you want to calcuate at the beginning of the simulation.
#			You have to change the input pattern by yourself to calcuate different patterns.


# ------------
# Module	From the top: libraries for regular expressions, argument handling, console usage, fixed-point arithmetic, and arithmetic operations (pi, etc.)
# ------------
import re
import sys
from subprocess import *
from decimal import *
from math import *


# -----------------
# Initialize valuables
# -----------------
#	vbmin: the minimum bias voltage
#	vbmax: the maximum bias voltage
#	vbstep: the step to change the bias voltage
#	skewstep: the step to change the input skew
#	initial_skew: the initial value of the input skew
vbmin = Decimal("2.0")
vbmax = Decimal("3.0")
vbstep = Decimal("0.05")
skewstep = Decimal("0.025e-12")
initial_skew = Decimal("4e-12")


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


def checkb(s):		# search "Vc"
    p = re.compile(r'Vc')
    return p.search(s)


def checkc(s):		# search "Vb"
    p = re.compile(r'Vb')
    return p.match(s)


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
    exe("sitmp.inp")
    f1 = open("a.txt", "r")
    initial = 0
    list1 = []
    list2 = []
    for line in f1.readlines():
        a = line.split()
        if a == []:
            continue
        elif checka(a[0]) != None:
            if initial == 0:
                initial = a
            else:
                if (float(a[1]) - float(initial[1])) / pi > 1 + len(list1) * 2:
                    list1.append(a[0])
                if (float(a[2]) - float(initial[2])) / pi > 1 + len(list2) * 2:
                    list2.append(a[0])
    f1.close()
    return list1, list2


# --------------------
# Rewrite si.inp and change bias voltage
# --------------------
def rewrite_vb(vb):
    f1 = open("si.inp", "r")
    f2 = open("sivb.inp", "w")
    for line in f1.readlines():
        a = line.split()
        if a == []:
            f2.write(line)
        elif checkc(a[0]) != None:
            b = []
            b.append(a[0])
            b.append(a[1])
            b.append(a[2])
            b.append(a[3])
            b.append(a[4])
            b.append(a[5])
            b.append(a[6])
            b.append(a[7])
            b.append(str(vb) + "mV" + ")\n")
            f2.write(" ".join(b))
        else:
            f2.write(line)
    f1.close()
    f2.close()


# --------------------
# Rewrite si.inp and change input arrival
# --------------------
def rewrite_skew(skew):
    f1 = open("sivb.inp", "r")
    f2 = open("sitmp.inp", "w")
    for line in f1.readlines():
        a = line.split()
        if a == []:
            f2.write(line)
        elif checkb(a[0]) != None:
            b = []
            b.append(a[0])
            b.append(a[1])
            b.append(a[2])
            b.append(a[3])
            b.append(a[4])
            b.append(str(float(a[5].replace("ps", "")) +
                     float(skew) * 1e12) + "ps")
            b.append(a[6])
            b.append(str(float(a[7].replace("ps", "")) +
                     float(skew) * 1e12) + "ps")
            b.append(a[8])
            b.append(str(float(a[9].replace("ps", "")) +
                     float(skew) * 1e12) + "ps")
            b.append(a[10])
            b.append("\n")
            f2.write(" ".join(b))
        else:
            f2.write(line)
    f1.close()
    f2.close()


# --------
# XOR Judge
# --------
def XOR(list1, list2):
    if len(list1) == 1 and len(list2) == 0:
        return 1
    if len(list1) == 1 and len(list2) == 2:
        return 2
    else:
        return 3


# --------
# AND Judge
# --------
def AND(list1, list2):
    if len(list1) == 1 and len(list2) == 1:
        return 1
    if len(list1) == 1 and len(list2) == 0:
        return 2
    else:
        return 3


# --------
# OR Judge
# --------
def OR(list1, list2):
    if len(list1) == 1 and len(list2) == 1:
        return 1
    if len(list1) == 1 and len(list2) == 2:
        return 2
    else:
        return 3


# --------
# mais(logic) calcuates the Maximum Allowed Input Skew. logic is an argument; either "and", "or" or "xor".
# --------
def mais(logic):
    vb = vbmax
    skew = initial_skew
    shell("rm result_skew.txt")
    shell("del result_skew.txt")
    f = open("resulttmp.txt", "w")
    while vb >= vbmin:
        rewrite_vb(vb)
        rewrite_skew(skew)
        while True:
            list1, list2 = switch()
            print(list1, list2)
            if logic == "and":
                if AND(list1, list2) == 1:
                    maxskew = prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
                if AND(list1, list2) == 2:
                    break
                if AND(list1, list2) == 3:
                    prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
            if logic == "or":
                if OR(list1, list2) == 1:
                    maxskew = prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
                if OR(list1, list2) == 2:
                    break
                if OR(list1, list2) == 3:
                    prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
            if logic == "xor":
                if XOR(list1, list2) == 1:
                    maxskew = prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
                if XOR(list1, list2) == 2:
                    break
                if XOR(list1, list2) == 3:
                    prohibit = skew
                    skew = skew + skewstep
                    rewrite_skew(skew)
        f.write(str(vb) + " " + str(float(maxskew) * 1e12) +
                " " + str(float(prohibit) * 1e12) + "\n")
        print(str(vb) + " " + str(float(maxskew) * 1e12) +
              " " + str(float(prohibit) * 1e12) + "\n")
        vb = vb - vbstep
        skew = maxskew - Decimal(0.1e-12)
    f.close()
    print("end")
    shell("sort -n resulttmp.txt > result_skew.txt")
    shell("rm sitmp.inp resulttmp.txt a.txt sivb.inp")
    shell("del sitmp.inp resulttmp.txt a.txt sivb.inp")


# --------
# ltcy(mode) calcuates the latency. mode is an argument; either 1, 2 or 3.
# mode 1 simply calcuates the latency of the first input combination.
# mode 2 changes the input skew.
# mode 3 changes the bias voltage.
# --------
def ltcy(mode):
    if mode == 1:
        try:
            vb = Decimal(
                input("Please input the bias voltage [mV] (Default = 2.5 mV) : "))
        except:
            vb = Decimal(2.5)
        skew = Decimal(0)
        rewrite_vb(vb)
        rewrite_skew(skew)
        list1, list2 = switch()
        if list1 == [] or list2 == []:
            print("latency = N/A ps")
        elif Decimal(list2[0]) - Decimal(list1[0]) < 0:
            print("latency = N/A ps")
        else:
            print("latency = {} ps".format(
                round((Decimal(list2[0]) - Decimal(list1[0])) * Decimal(1e12), 2)))
        shell("rm sitmp.inp a.txt sivb.inp")
        shell("del sitmp.inp a.txt sivb.inp")
    if mode == 2:
        try:
            vb = Decimal(
                input("Please input the bias voltage [mV] (Default = 2.5 mV) : "))
        except:
            vb = Decimal(2.5)
        skew = Decimal(0)
        rewrite_vb(vb)
        rewrite_skew(skew)
        list1, list2 = switch()
        f = open("result_latencyskew.txt", "w")
        while True:
            if len(list1) == 1 and len(list2) == 1:
                f.write(str(round(skew * Decimal(1e12), 3)) + " " + str(
                    round((Decimal(list2[0]) - Decimal(list1[0])) * Decimal(1e12), 2)) + "\n")
                print(str(round(skew * Decimal(1e12), 3)) + " " +
                      str(round((Decimal(list2[0]) - Decimal(list1[0])) * Decimal(1e12), 2)) + "\n")
                skew = skew + skewstep
                rewrite_skew(skew)
                list1, list2 = switch()
            else:
                print("end")
                break
        f.close()
        shell("rm sitmp.inp a.txt sivb.inp")
        shell("del sitmp.inp a.txt sivb.inp")
    if mode == 3:
        vb = vbmax
        skew = Decimal(0)
        shell("rm result_latency.txt")
        f = open("resulttmp.txt", "w")
        while vb >= vbmin:
            rewrite_vb(vb)
            rewrite_skew(skew)
            list1, list2 = switch()
            if list1 != [] and list2 != []:
                f.write(str(
                    vb) + " " + str(round((Decimal(list2[0]) - Decimal(list1[0])) * Decimal(1e12), 2)) + "\n")
                print(str(
                    vb) + " " + str(round((Decimal(list2[0]) - Decimal(list1[0])) * Decimal(1e12), 2)) + "\n")
            else:
                print("lower than {} mV, no output".format(vb + vbstep))
                break
            vb = vb - vbstep
        f.close()
        print("end")
        shell("sort -n resulttmp.txt > result_latency.txt")
        shell("rm sitmp.inp resulttmp.txt a.txt sivb.inp")
        shell("del sitmp.inp resulttmp.txt a.txt sivb.inp")


# --------
# Main
# --------
def main():
    args = sys.argv
    if len(args) >= 2:
        if args[1] == "a":
            mais("and")
        elif args[1] == "o":
            mais("or")
        elif args[1] == "x":
            mais("xor")
        elif args[1] == "l":
            ltcy(1)
        elif args[1] == "ls":
            ltcy(2)
        elif args[1] == "lb":
            ltcy(3)
        else:
            print(
                'Argument error.\nAND -> a, OR -> o, XOR -> x, LATENCY -> l or ls or lb')
    else:
        print('Argument error.\nAND -> a, OR -> o, XOR -> x, LATENCY -> l or ls or lb')


if __name__ == "__main__":
    main()
