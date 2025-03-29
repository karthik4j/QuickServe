import tkinter as tk
from tkinter import ttk
from tkinter import messagebox ,PhotoImage
from PIL import Image,ImageTk
import threading
import time
window_width = 700
window_height = 530

window = tk.Tk()
window.title("Progress Window")
window.geometry('300x400')

def  start_thread():
    w1 = tk.Toplevel()
    w1.geometry('500x300')
    lent = int((w1.winfo_screenheight()/2)-window_height/2)
    widt = int((w1.winfo_screenwidth()/2)-window_width/2)
    w1.geometry("{}x{}+{}+{}".format(window_width,window_height,widt,lent))
    w1.minsize(window_width,window_height)
    w1.maxsize(window_width,window_height)
    lb1 = ttk.Label(w1,text="Loading ",font=('Comic sans',24)).pack()
    img = Image.open('logo.png')
    img = img.resize((300,300))
    img = ImageTk.PhotoImage(img)
    lb2 = ttk.Label(w1,image=img).pack()
    progress_bar = ttk.Progressbar(w1, length=300, maximum=100, mode='determinate')
    progress_bar.pack()
    i=0
    while(i<100.00):
        progress_bar['value'] = i
        w1.update_idletasks()  
        i=i+10.0
        time.sleep(1.2)
    w1.update_idletasks()
    w1.destroy()
def say(i):
    print('Info',f'button pressed is: {i}')
    
frm = ttk.Frame(window)
lab = ttk.Label(frm,text='DEMO TEST',font=('Comic sans',24)).pack()
btn1 = ttk.Button(frm,text="BTN 1",command=lambda :say(1)).pack()
btn2 = ttk.Button(frm,text="BTN 2",command=lambda :say(2)).pack()
btn3 = ttk.Button(frm,text="BTN 3",command=lambda :say(3)).pack()
btn4 = ttk.Button(frm,text="BTN 4",command=lambda :say(4)).pack()
t1  = threading.Thread(target=start_thread,daemon=True).start()
frm.pack()
window.mainloop()



