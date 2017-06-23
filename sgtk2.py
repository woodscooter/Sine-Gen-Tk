#!/usr/bin/python3
# Python GUI for sine-gen 2

import tkinter as tk
from tkinter import font
from tkinter.ttk import *
import threading
import queue
import subprocess


PUMP = 15  # GPIO15, pin 10
gen_q = queue.Queue(3)
pump_q = queue.Queue(3)

class Application (tk.Frame):
    def __init__(self,master=None):
        super().__init__(master)
        self.pack()
        self.runstate = 1
        self.freq = tk.StringVar()
        self.freq.set (2.6)
        self.freq2 = tk.StringVar()
        self.freq2.set (2.85)
        self.shadow = tk.StringVar()
        self.shadow.set (1.0594)
        self.duration = tk.StringVar()
        self.duration.set (0.5)
        self.guard = tk.StringVar()
        self.guard.set (0.5)
        self.gtime = tk.StringVar()
        self.gtime.set (0.5)
        self.pumprun = tk.StringVar()
        self.pumprun.set (1)
        self.pumpstop = tk.StringVar()
        self.pumpstop.set (20)
        self.genstate = tk.StringVar()
        self.genstate.set ("OFF")
        self.pumpstate = tk.StringVar()
        self.pumpstate.set ("OFF")

        self.create_widgets()
    def create_widgets(self):

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Liberation Sans', size=24, weight='bold')
#        self.title("Sine wave Generator")

        tk.Label(self,text="SINE WAVE GENERATOR",pady=20).grid(row=1,column=1,columnspan=3)

        tk.Label(self,text="Frequency (kHz)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=3,column=0)
        f1 = tk.Spinbox(self,textvariable = self.freq ,from_= 0.2, to = 10.01,increment=0.01,command=self.freq_change,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=3,column=1)
        tk.Label(self,text="2nd Frequency (kHz)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=4,column=0)
    #    f2 = tk.Spinbox(self,textvariable = self.freq2 ,from_= 2.0, to = 3.9,increment=0.01,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=4,column=1)
        f2 = tk.Label(self,textvariable = self.freq2 ,relief = 'sunken', bg='#fff',width=7,anchor='w').grid(row=4,column=1,sticky='W')

        tk.Button(self,text="12\N{SQUARE ROOT}2",command=self.shadow_default).grid(row=3,column=4)
        tk.Label(self,text="Frequency ratio",relief = 'raised', width=20,anchor='center', pady=5).grid(row=4,column=3)
        self.shad = tk.Spinbox(self,textvariable = self.shadow ,from_= 0.001, to = 2.5,increment=0.001,command=self.freq_change,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=4,column=4)

        tk.Label(self,text="", width=5, pady=5).grid(row=5,column=2)

        tk.Label(self,text="Generator is",relief = 'raised', width=20,anchor='center', pady=5).grid(row=6,column=0)
        self.gen =tk.Spinbox(self,textvariable = self.genstate ,values=("OFF","ON"),relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=6,column=1)
        tk.Label(self,text="Generator on (s)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=7,column=0)
        dur = tk.Spinbox(self,textvariable = self.duration ,from_= 0.1, to = 1.9,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=7,column=1)
        tk.Label(self,text="Generator off (s)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=8,column=0)
        guard = tk.Spinbox(self,textvariable = self.gtime ,from_= 0.1, to = 1.9,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=8,column=1)

        tk.Label(self,text="Valve is",relief = 'raised', width=20,anchor='center', pady=5).grid(row=6,column=3)
        self.pump = tk.Spinbox(self,textvariable = self.pumpstate ,values=("OFF","ON"),relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=6,column=4)
        tk.Label(self,text="Flush time (s)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=7,column=3)
        run = tk.Spinbox(self,textvariable = self.pumprun ,from_= 0.1, to = 10.0,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=7,column=4)
        tk.Label(self,text="Pause time (s)",relief = 'raised', width=20,anchor='center', pady=5).grid(row=8,column=3)
        stop = tk.Spinbox(self,textvariable = self.pumpstop ,from_= 1.0, to = 60,increment=1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=8,column=4)

#        tk.Label(self,text="Signal").grid(row=9,column=0)
#        tk.Label(self,text="Valve").grid(row=9,column=3)
        tk.Label(self,text="", width=5, pady=5).grid(row=9,column=2)
        self.bar = tk.ttk.Progressbar(self,orient="horizontal",length=500,mode="indeterminate",maximum=100).grid(row=9,column=3,columnspan=2)

        tk.Button(self,text="Quit",command=self.quitnot).grid(row=10,column=4)

    def confess(self):
        q1_data = [ self.runstate, self.genstate.get(), float(self.freq.get()), float(self.freq2.get()), float(self.duration.get()), float(self.gtime.get()) ]
        q2_data = [ self.runstate, self.pumpstate.get(),float(self.pumprun.get()), float(self.pumpstop.get()) ]
        if not gen_q.full():
            gen_q.put(q1_data)
        if not pump_q.full():
            pump_q.put(q2_data)
#        pumpval = float(self.pumprun.get()) + float(self.pumpstop.get())
        if not self.runstate:
            thread2.stop()
            thread1.join()
            thread2.join()
            command = "./sox_kill.sh"
            subprocess.run(command)
            root.destroy()

    def freq_change(self):
        num = float(self.shadow.get()) * float(self.freq.get())
        string = "%2.3f" % num
        num = float(string)
        self.freq2.set(num)
    def shadow_default(self):
        self.shadow.set("1.0594")
        self.freq_change()
    def quitnot(self):
        self.runstate = 0
def update():
    app.confess()
    app.after(100,update)
class genThread(threading.Thread):
    def __init__(self,threadID,name,q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        generator(self.name,self.q)
class pumpThread(threading.Thread):
    def __init__(self,threadID,name,q):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.threadID = threadID
        self.name = name
        self.q = q
    def stop(self):
        self._stop_event.set()
    def stopped(self):
        return self._stop_event.is_set()
    def run(self):
        setpump(self.name, self.q)
def generator(threadName,q):
    data = [1,"OFF",0.0,0.0,0.0,0.0]
    while data[0]:
        if not q.empty():
            data = q.get()
        if data[1] == "ON":
            gen_freq = data[2]
            gen_freq2 = data[3]
            gen_duration = data[4]
            gen_gtime = data[5]
            command = "./play -n -c1 synth %2.1f sin %2.3f k sin %2.3f k lowpass 9k : trim 0 %2.1f lowpass 1k 2>/dev/null" % (gen_duration, gen_freq, gen_freq2, gen_gtime)
            subprocess.run(command,shell=True)

def calc (parameter):
    number = float (parameter)
    number *= 1000
    number /= 333
    return int(number)
def setpump(threadName,q):
    data = [1,"OFF",0.0,0.0]
    sleepcmd = "pigs mils 333"
    command = "pigs modes %d W" % PUMP
    subprocess.run(command,shell=True)
    while data[0]:
        if not q.empty():
            data = q.get()
        if data[1] == "OFF":
            command = "pigs w %d 0" % PUMP
            subprocess.run(command,shell=True)
            subprocess.run(sleepcmd,shell=True)
            if thread2.stopped():
                return
        else:
            command = "pigs w %d 1" % PUMP
            subprocess.run(command,shell=True)
            pumpcount = calc(data[2])
            while pumpcount:
                subprocess.run(sleepcmd,shell=True)
                pumpcount -= 1
            command = "pigs w %d 0" % PUMP
            subprocess.run(command,shell=True)
            pumpcount = calc (data[3])
            while pumpcount:
                subprocess.run(sleepcmd,shell=True)
                if thread2.stopped():
                    return
                pumpcount -= 1
        subprocess.run(sleepcmd,shell=True)
    # thread finished, switch off
    command = "pigs w %d 0" % PUMP
    subprocess.run(command,shell=True)

root = tk.Tk()
root.title("Sine Generator")
app = Application(master = root)
thread1 = genThread(1, "Generator",gen_q)
thread2 = pumpThread(2, "Pump",pump_q)
thread1.start()
thread2.start()
app.after(100,update)
app.mainloop()
