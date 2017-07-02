#!/usr/bin/python3
# Python GUI for sine-gen 2

#import tkinter as tk
from tkinter import *
from tkinter import font
from tkinter.ttk import *
import threading
import queue
import subprocess
import time

root = Tk()
root.title("Control Panel")


PUMP = 15  # GPIO15, pin 10
gen_q = queue.Queue(1)
pump_q = queue.Queue(1)
progress_q = queue.Queue(1)

class Application (Frame):
    def __init__(self,master=None):
        super().__init__(master)
#        self.pack()
        self.runstate = 1
        self.freq = StringVar()
        self.freq.set (2.6)
        self.freq2 = StringVar()
        self.freq2.set (2.85)
        self.shadow = StringVar()
        self.shadow.set (1.0594)
        self.duration = StringVar()
        self.duration.set (0.5)
        self.guard = StringVar()
        self.guard.set (0.5)
        self.gtime = StringVar()
        self.gtime.set (0.5)
        self.pumprun = StringVar()
        self.pumprun.set (1)
        self.pumpstop = StringVar()
        self.pumpstop.set (20)
        self.genstate = StringVar()
        self.genstate.set ("OFF")
        self.pumpstate = StringVar()
        self.pumpstate.set ("OFF")
        self.progress_var = StringVar()
        self.progress_var.set(50.0)
        self.event = threading.Event()

        self.create_widgets()
    def create_widgets(self):

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Liberation Sans', size=20, weight='bold')

        Label(self,text="RESONANCE CONTROL PANEL").grid(row=0,column=0,columnspan=5,pady=20)

        Label(self,text="Frequency (kHz)",relief = 'raised', width=20,anchor='center').grid(row=3,column=0)
        f1 = Spinbox(self,textvariable = self.freq ,from_= 0.2, to = 10.01,increment=0.01,command=self.freq_change,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=3,column=1)
        Label(self,text="2nd Frequency (kHz)",relief = 'raised', width=20,anchor='center').grid(row=4,column=0)
    #    f2 = Spinbox(self,textvariable = self.freq2 ,from_= 2.0, to = 3.9,increment=0.01,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=4,column=1)
        f2 = Label(self,textvariable = self.freq2 ,relief = 'sunken', background='#fff',width=7,anchor='w').grid(row=4,column=1,sticky='W')

        Button(self,text="12\N{SQUARE ROOT}2",command=self.shadow_default).grid(row=3,column=4)
        Label(self,text="Frequency ratio",relief = 'raised', width=20,anchor='center').grid(row=4,column=3)
        self.shad = Spinbox(self,textvariable = self.shadow ,from_= 0.001, to = 2.5,increment=0.001,command=self.freq_change,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=4,column=4)

        Label(self,text="", width=5).grid(row=5,column=2)

        Label(self,text="Generator is",relief = 'raised', width=20,anchor='center').grid(row=6,column=0)
        self.gen =Spinbox(self,textvariable = self.genstate ,values=("OFF","ON","CONT"),relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=6,column=1)
        Label(self,text="Generator on (s)",relief = 'raised', width=20,anchor='center').grid(row=7,column=0)
        dur = Spinbox(self,textvariable = self.duration ,from_= 0.1, to = 1.9,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=7,column=1)
        Label(self,text="Generator off (s)",relief = 'raised', width=20,anchor='center').grid(row=8,column=0)
        guard = Spinbox(self,textvariable = self.gtime ,from_= 0.1, to = 1.9,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=8,column=1)

        Label(self,text="Valve is",relief = 'raised', width=20,anchor='center').grid(row=6,column=3)
        self.pump = Spinbox(self,textvariable = self.pumpstate ,values=("OFF","ON"),relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=6,column=4)
        Label(self,text="Flush time (s)",relief = 'raised', width=20,anchor='center').grid(row=7,column=3)
        run = Spinbox(self,textvariable = self.pumprun ,from_= 0.1, to = 10.0,increment=0.1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=7,column=4)
        Label(self,text="Pause time (s)",relief = 'raised', width=20,anchor='center').grid(row=8,column=3)
        stop = Spinbox(self,textvariable = self.pumpstop ,from_= 1.0, to = 60,increment=1,relief = 'sunken', bg='#fff',width=7, font = default_font).grid(row=8,column=4)

        self.w = Canvas(self,width=110, height=18, relief="sunken")
        self.w.grid(row=9,column=1)
        self.r = self.w.create_rectangle(0, 0, 99, 16, fill="silver", outline='white')

        Label(self,text="", width=5).grid(row=9,column=2)
        self.bar = Progressbar(self,orient="horizontal",length=400,mode="determinate",variable=self.progress_var,maximum=100).grid(row=9,column=3,columnspan=2)

        Button(self,text="Quit",command=self.quitnot,width=7).grid(row=10,column=0,pady=20)
        Button(self,text="Stop",command=self.stopnot,width=7).grid(row=10,column=1,pady=20)

    def confess(self):
        q1_data = [ self.runstate, self.genstate.get(), float(self.freq.get()), float(self.freq2.get()), float(self.duration.get()), float(self.gtime.get()) ]
        q2_data = [ self.runstate, self.pumpstate.get(),float(self.pumprun.get()), float(self.pumpstop.get()) ]
        if not gen_q.full():
            gen_q.put(q1_data)
        if not pump_q.full():
            pump_q.put(q2_data)
        if not progress_q.empty():
            self.progress_data = progress_q.get()
            self.progress_var.set(self.progress_data)
        if self.genstate.get() != 'OFF':
            self.w.itemconfig(self.r,fill="red")
        else:
            self.w.itemconfig(self.r,fill="silver")
        if self.pumpstate.get() == "OFF":
            self.event.set()
        else:
            self.event.clear()

        if not self.runstate:
            thread1.stop()
            thread2.stop()
            thread1.join()
            thread2.join()
            root.destroy()

    def freq_change(self):
        num = float(self.shadow.get()) * float(self.freq.get())
        string = "%2.3f" % num
        num = float(string)
        self.freq2.set(num)
    def shadow_default(self):
        self.shadow.set("1.0594")
        self.freq_change()
    def stopnot(self):
        cont = self.genstate.get()
        self.genstate.set("OFF")
        self.pumpstate.set("OFF")
        if cont == "CONT":
            time.sleep(1)
            command = "./sox_kill.sh"
            subprocess.call(command)
            time.sleep(1)
            command = "./sox_kill.sh"
            subprocess.call(command)
    def quitnot(self):
        self.runstate = 0
        command = "./sox_kill.sh"
        subprocess.call(command)
def update():
    app.confess()
    app.after(100,update)
class genThread(threading.Thread):
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
        if data[1] != "OFF":
            gen_freq = data[2]
            gen_freq2 = data[3]
            gen_duration = data[4]
            gen_gtime = data[5]
            command = "play -c1 -b16 --null synth %2.1f sin %2.3fk sin %2.3fk lowpass 9k : trim 0 %2.1f 2>/dev/null" % (gen_duration, gen_freq, gen_freq2, gen_gtime)
            if data[1] == "CONT":
                command = "play -c1 -b16 --null synth 0 sin %2.3fk sin %2.3fk lowpass 9k 2>/dev/null" % ( gen_freq, gen_freq2 )
            subprocess.call(command,shell=True)
            if thread1.stopped():
                return
#            subprocess.call(command)

def calc (parameter):
    number = float (parameter)
    number *= 1000
    number /= 333
    return int(number)
def setpump(threadName,q):
    data = [1,"OFF",0.0,0.0]
    sleepcmd = "pigs mils 333"
    command = "pigs modes %d W" % PUMP
    pumptotal = 0
    pumpprogress = 0
    subprocess.call(command,shell=True)
    while data[0]:
        if pumpprogress >= pumptotal:
            pumpprogress = 0
        if not q.empty():
            data = q.get()
            pumptotal=calc(data[2]+data[3])
        if data[1] == "OFF":
            command = "pigs w %d 1" % PUMP
            subprocess.call(command,shell=True)
            subprocess.call(sleepcmd,shell=True)
            pumpprogress = 0
            if not progress_q.full():
                if pumptotal == 0:
                    pumptotal = 1
                queue3_data = 100*pumpprogress/pumptotal
                progress_q.put(queue3_data)
            if thread2.stopped():
                return
        else:
            command = "pigs w %d 0" % PUMP
            subprocess.call(command,shell=True)
            pumpcount = calc(data[2])
            while pumpcount:
                subprocess.call(sleepcmd,shell=True)
                pumpcount -= 1
                pumpprogress += 1
                if app.event.isSet():
                    break
                if not progress_q.full():
                    if pumptotal == 0:
                        pumptotal = 1
                    queue3_data = 100*pumpprogress/pumptotal
                    progress_q.put(queue3_data)
            command = "pigs w %d 1" % PUMP
            subprocess.call(command,shell=True)
            pumpcount = calc (data[3])
            while pumpcount:
                subprocess.call(sleepcmd,shell=True)
                if thread2.stopped():
                    return
                pumpcount -= 1
                pumpprogress += 1
                if app.event.isSet():
                    break
                if not progress_q.full():
                    if pumptotal == 0:
                        pumptotal = 1
                    queue3_data = 100*pumpprogress/pumptotal
                    progress_q.put(queue3_data)
#        subprocess.call(sleepcmd,shell=True)
        if not progress_q.full():
        	if pumptotal == 0:
                    pumptotal = 1
        	queue3_data = 100*pumpprogress/pumptotal
        	progress_q.put(queue3_data)
    # thread finished, switch off
    command = "pigs w %d 1" % PUMP
    subprocess.call(command,shell=True)

app = Application(master = root)
app.pack()
thread1 = genThread(1, "Generator",gen_q)
thread2 = pumpThread(2, "Pump",pump_q)
thread1.start()
thread2.start()
app.after(100,update)
app.mainloop()
