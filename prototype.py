#UI layout test
#import tkinter as tk
#from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

import ttkbootstrap as ttk
from ttkbootstrap.constants import *

from tkinter import messagebox
from tkinter import PhotoImage
import os
import sqlite3
import threading
import qrcode
import http.server
import socketserver
import math

global table_name
global file
global conn

import cv2
import tkinter as tk
from tkinter import Label
from PIL import Image, ImageTk,ImageFont,ImageDraw
from pyzbar.pyzbar import decode
import queue
import time
import platform
import winsound
import http.server
import socketserver


PORT = 7000
MESSAGE = "21"
#os.environ["OPENCV_VIDEOIO_MSMF_ENABLE_HW_TRANSFORMS"] = "0"
file ="python_proj.db"
table_name = "my_plates"
set_theme = "cosmo"
_bg ='white'
_bg2 = "sky blue"
_fg = "bisque"
b_style ='info-outline'
window_width = 700
window_height = 530
#--------------------------------  HTTP server  ------------
def server_run():
    class CustomHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == "/data":
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                MESSAGE = plate_count()
                self.wfile.write(MESSAGE.encode())
            elif self.path == "/":  # Serve the webpage
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                with open("website\index.html", "rb") as file:
                    self.wfile.write(file.read())
            else:
                self.send_error(404, "Not Found")

    with socketserver.TCPServer(('0.0.0.0', PORT), CustomHandler) as httpd:
        print(f"Serving at {PORT}")

        httpd.serve_forever()
#
def check_multi():
    MESSAGE = plate_count()
    print(MESSAGE)
#------------------------------------------------------------ 
#testing if the connector exists, otherwise we create one
def get_sql_conn():
    try: 
      conn = sqlite3.connect(file,check_same_thread=False) 
     # print(f"Database {file} is formed.")
      
      return conn
    except: 
      print(f"Database {file} not formed.")

def create_table():
    #try to check if the table exists or not
    # used to check if table exist or not, if not it is created.
    #returns a value based on whether it exists or not.
    conn = get_sql_conn()
    res = conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (table_name,))
    table_exists = res.fetchone()
    if table_exists:
     #   print('table exists')
        return True
       
    else:
        print('table does not exist')
        conn.execute(f'CREATE TABLE {table_name} (plate_id INT, plate_state INT)')
        print('table has been created')
        return False
    
def check_table_conn():
    try: 
      conn = sqlite3.connect(file) 
      res = conn.execute("""SELECT name FROM sqlite_master WHERE type='table' AND name=?;""", (table_name,))
      table_exists = res.fetchone()
      if table_exists:
         # print('connected')
          return True
      else:
        #  print('not connected')
          return False 
      
    except: 
      print(f"Database {file} not formed.")
      return False
#conn.execute(f'INSERT INTO {table_name} values(1,1)')
#conn.commit()
#print((conn.execute(f'select * from {table_name}')).fetchone())

#--------------------------------------------------  ROOT WINDOW CONFIGURE   -------------------------------------------------------------
root = tb.Window(themename=set_theme)
style=ttk.Style()
root.title("QuickServe")
lent = int((root.winfo_screenheight()/2)-window_height/2)
widt = int((root.winfo_screenwidth()/2)-window_width/2)
root.geometry("{}x{}+{}+{}".format(window_width,window_height,widt,lent))
root.minsize(window_width,window_height)
root.maxsize(window_width,window_height)
nb = ttk.Notebook(root)
root.iconbitmap('res/logo.ico')
menu_tab = ttk.Frame(nb)
global cursor
#check SQL connectivity and set up cursor to be used
cursor =  get_sql_conn()
#------------------------------------------------ PLATE_ID GENERATOR -------------------------------------------
def create_plate():
    cursor =get_sql_conn()
    if(check_table_conn):
        if(create_table()):
            list_of_plates = cursor.execute(f'SELECT max(plate_id) from {table_name}')
            list_of_plates = list_of_plates.fetchone()
            if(list_of_plates[0] == None):
                new_plate_id = 1
            else:
                new_plate_id= list_of_plates[0]+1
            cursor.execute(f'insert into {table_name} values({new_plate_id},1)')
            cursor.commit()
        else: #table does not exist but connection does
            x = create_table()
    else:
        cursor =get_sql_conn()
    
       
#------------------------------------------------ PLATE_ID DISPLAY -------------------------------------------
def plate_count():
    if(check_table_conn()):
        val = cursor.execute(f"SELECT COUNT(plate_state) FROM {table_name} WHERE plate_state = 1")
        VAL = str(val.fetchone())
        VAL = VAL.strip("(),")
        return VAL
#-------------------------------------------------------OPENCV qr code ---------------------------
class WebcamScanner:
    def __init__(self, video_label, sound_path="beep.mp3", width=640, height=480, camera_index=0):
        """
        Initializes the webcam scanner with customizable options.
        
        Parameters:
            video_label (tk.Label): The label to display the webcam feed.
            sound_path (str): Path to the sound file to play on QR code detection.
            width (int): Width of the webcam feed.
            height (int): Height of the webcam feed.
            camera_index (int): Index of the webcam to use (default is 0).
        """
        self.video_label = video_label
        self.width = width
        self.height = height
        self.sound_path = sound_path
        self.camera_index = camera_index
        self.scanning = False
        self.running = True
        self.scanned_code = None
        self.lock = threading.Lock()  # Lock for thread-safe access to scanned_code

        # Queue for thread-safe frame passing
        self.frame_queue = queue.Queue(maxsize=1)

        # Open the specified webcam
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            print(f"Error: Could not open webcam with index {self.camera_index}")
            return
        
        # Start video capture in a separate thread
        self.capture_thread = threading.Thread(target=self.capture_frames, daemon=True)
        self.capture_thread.start()

        # Start updating the GUI frame
        self.update_frame()

    def play_sound(self):
        """Plays a sound when a QR code is detected."""
        try:
            if platform.system() == "Windows":
                winsound.Beep(1000, 300)  # Frequency 1000 Hz, Duration 200 ms
            else:
                print("\a")  # Fallback beep for non-Windows systems
        except Exception as e:
            print(f"Error playing sound: {e}")

    def scan_qr(self):
        """Triggers QR code scanning on button press."""
        self.scanning = True

    def capture_frames(self):
        """Captures frames continuously in a separate thread."""
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                # Resize the frame for consistency
                frame = cv2.resize(frame, (self.width, self.height))

                # Check for QR code when scanning is triggered
                if self.scanning:
                    decoded_objects = decode(frame)
                    for obj in decoded_objects:
                        data = obj.data.decode("utf-8")
                        if data.isdigit():
                            number = int(data)
                            print(f"Scanned Number: {number}")
                            self.play_sound()
                            with self.lock:
                                self.scanned_code = number  # Store scanned code
                            self.scanning = False  # Stop scanning after detecting
                            break

                # Put the frame into the queue if space is available
                if not self.frame_queue.full():
                    self.frame_queue.put(frame)

            # Delay to reduce CPU usage
            time.sleep(0.01)

    def get_scanned_code(self):
        """Returns the last scanned QR code and resets it to None."""
        with self.lock:
            code = self.scanned_code
            self.scanned_code = None  # Reset after returning
            return code

    def update_frame(self):
        """Updates the tkinter label with the latest frame from the queue."""
        if not self.frame_queue.empty():
            frame = self.frame_queue.get()

            # Convert the frame to RGB and display it
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the tkinter label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

        # Schedule the next frame update
        self.video_label.after(10, self.update_frame)

    def stop(self):
        """Releases the webcam and stops the feed."""
        self.running = False
        self.capture_thread.join()
        self.cap.release()
        cv2.destroyAllWindows()


        
   
#------------------------------------------------------------ MENU PAGE CODE ------------------------------------------

def cam_ref_sh():
    scanner.scan_qr()
    plat_count_menu.set(plate_count())


style = ttk.Style()
style.configure("My.TFrame",background=_bg)
style.configure("frame2.TFrame",background=_bg2)
style.configure('frame3.TLabel',background=_bg2)

frame1 = ttk.Frame(menu_tab,relief='ridge',style='My.TFrame')
frame2 = ttk.Frame(menu_tab,style="frame2.TFrame")


scan_g_img = PhotoImage(file="res/AvailableV.png")
scan_b_img =  PhotoImage(file='res/InuseV.png')

lab0 = ttk.Label(frame1,text="SCAN OPTIONS",font=("Bebas Neue",22,"bold")).pack(pady=10,expand=True)
                                    
plat_count_menu = tk.StringVar(value=plate_count())

mu_lab_fram = ttk.Frame(frame2)
lab1 = ttk.Label(mu_lab_fram,text=f'    AVAILABLE PLATE COUNT IS:',font=('Bebas Neue', 18),style='frame3.TLabel')
lab1.pack(side='left')
lab11 = ttk.Label(mu_lab_fram,textvariable=plat_count_menu,font=('Bebas Neue', 18),style="frame3.TLabel").pack(side='left')
#QR CODE READING/HANDLING/DISPLAY IN MAIN PAGE
qr_window =ttk.Label(master=frame2)
mu_lab_fram.pack()
qr_window.pack()

scanner = WebcamScanner(qr_window, width=350, height=400, camera_index=0)
cv_done =False
scan_g = ttk.Button(frame1,text='Available',image = scan_g_img,command=lambda:plate_avail(scanner),bootstyle=b_style,padding=0).pack(padx=10,expand=False)#pady=10)
scan_b = ttk.Button(frame1,text='USE',image=scan_b_img,command=lambda:plate_in_use(scanner),bootstyle=b_style,padding=0)
scan_b.pack(pady=10,expand=False)#padx=10)


frame1.pack(ipady=30,side='left',expand=True,fill='both')
frame2.pack(side='left',expand=True,fill='both')
#frame1.pack(side='left',ipadx=10,ipady=10,expand=True,fill='y')
#frame2.pack(side='top',ipadx=50,ipady=50)
style.configure('btn1.TButton',background=_bg2,bootstyle='info-outline',font=("Bebas Neue",22))
ref_sh = ttk.Button(master=frame1,text='Refresh ',command=cam_ref_sh,style='btn1.TButton').pack(pady=20)
#menu_tab.pack(expand=True)
#--------------------------------------------------------------  update/delete  --------------------------------------------------------------
#accepts the plate id of the plate to be udpated and the state to be updated
def update_plate(plate_id = None,plate_status=None):
    if(plate_id == None or plate_status == None):
        messagebox.showerror('Error','one or more entires are empty')
        return None
    if(check_table_conn()):
        chk = cursor.execute(f'SELECT plate_id FROM {table_name} WHERE plate_id = {plate_id}')
        if(chk.fetchone()):
            
            cursor.execute(f'UPDATE {table_name} SET plate_state = {plate_status} WHERE plate_id = {plate_id}')
            cursor.commit()
            messagebox.showinfo('Info','plate has been updated')
        else:
            messagebox.showerror('Error','Plate was not found in DB')
def plate_avail(obj):
    obj.scan_qr()
    ret_val = obj.get_scanned_code()
    update_plate(ret_val,1)
    plat_count_menu.set(value=plate_count())
    #obj.scanned_code = None
def plate_in_use(obj):
    obj.scan_qr()
    ret_val = obj.get_scanned_code()
    print(ret_val)
    update_plate(ret_val,0)
    plat_count_menu.set(value=plate_count())
    #obj.scanned_code = None
#--------------------------------------------------------------  DATABASE   -------------------------------------------------------------------
def fetch_data():
    if(check_table_conn()):
        list_of_plates_in_db = cursor.execute(f'select * from {table_name}')
        list_of_plates_in_db = list_of_plates_in_db.fetchall()
        return list_of_plates_in_db

def clear_tree():
    list_of_plates_in_db = fetch_data()
    for item in db_table.get_children():
        db_table.delete(item)    
def refresh():
    #global list_of_plates_in_db
    update_lab_sql()
    plat_count_menu.set(plate_count())
    if(check_table_conn()):
        list_of_plates_in_db = fetch_data()
        if(list_of_plates_in_db !=None):
            clear_tree()
            for i in list_of_plates_in_db:
                current_plate_id = i[0]
                current_plate_status = i[1]
                data = (current_plate_id,current_plate_status)
                if(current_plate_status == 1):
                    db_table.insert(parent='',index=0,values=data,tag='avail')
                else:
                    db_table.insert(parent='',index=0,values=data,tag='use')
    if(check_table_conn()==False):
        create_table()
        clear_tree()

db_tab = ttk.Frame(nb)
db_status_f = ttk.Frame(db_tab)
db_notebook_f =ttk.Frame(db_tab)

db_table = ttk.Treeview(db_notebook_f,columns= ('first','second'),show='headings')
db_table.heading('first',text='Plate number')
db_table.heading('second',text='Plate status')
db_table.column("first", anchor='center')
db_table.column("second", anchor='center')

db_table.tag_configure("avail",background='light green')
db_table.tag_configure("use",background='tomato')

db_table.pack(expand=True,fill='both')

info1 = ttk.Label(db_notebook_f,text='1 means plate is availabe \n0 means its not.',foreground='red',font=('Roboto',20)).pack(side='left')

ok_sql = tk.StringVar()
sql_status_lb = ttk.Label(master=db_status_f,text=f"SQL connection status: ",font=('Roboto',20)).pack(side='left')

sql_status = ttk.Label(master=db_status_f,textvariable=ok_sql,foreground='green',font=('Roboto',20))
sql_status.pack(side='left')

def update_lab_sql():
    if(check_table_conn()):
        ok_sql.set('Connected')
        sql_status.configure(foreground='green')
    else:
        ok_sql.set('Not connected')
        sql_status.configure(foreground='tomato')
update_lab_sql()
#style.configure('Ref.TButton',background='info-outline')
style.configure('REF.TButton',foreground='black',background='white',bootstyle='info-link',font=("Bebas Neue",18))

refresh_btn = ttk.Button(db_status_f,text='Refresh',command=refresh,style='REF.TButton')
refresh_btn.pack(padx=20,side='left')

db_status_f.pack(side='top',fill='x')
db_notebook_f.pack(side='top',expand=True,fill='both')

def kill_db():
    response = messagebox.askyesno("Drop tables?",'Do you really want to drop all tables?')
    if(response):
        if(check_table_conn()):
            cursor.execute(f"drop table {table_name}")
            messagebox.showinfo("Info","ALL data has been removed")
            clear_tree()
            update_lab_sql()
        else:
            messagebox.showerror("Error","No database to delete")
        update_lab_sql()
        #print(cursor.fetchone()
        
    else:
        messagebox.showinfo("Info",'No changes to DB')
#style.configure('btn2.TButton',bootstyle='danger-outline')
style.configure('DB.TButton',background='red',bootstyle='danger-link',font=("Bebas Neue",22))

btn_ok = ttk.Button(db_tab,text="Drop database",command=kill_db,style='DB.TButton')
btn_ok.pack()
    
#--------------------------------------- Modify DB  -----------------------------------------------------------------
modify_db = ttk.Frame(nb)
to_update_plate_id = tk.StringVar(value=None)
to_update_state = tk.StringVar(value=None)

entry_fram = ttk.Frame(modify_db)
lb = ttk.Label(modify_db,text="Update plate ",font=('Roboto','14')).pack(padx=20)

pid_fram =ttk.Frame(entry_fram)
lb1 = ttk.Label(pid_fram,text="PID").pack(padx=4.5,side='left')
ent1 = ttk.Entry(pid_fram,textvariable=to_update_plate_id).pack(side='left')

pst_fram =ttk.Frame(entry_fram)
lb2 = ttk.Label(pst_fram,text="State").pack(side='left')
ent2 = ttk.Entry(pst_fram,textvariable=to_update_state).pack(side='left')

pid_fram.pack()
pst_fram.pack()
entry_fram.pack()

btn1 = ttk.Button(modify_db,text='Ok',command = lambda :update_plate(to_update_plate_id.get(),to_update_state.get()))
                  #print(f"Entry: {to_update_plate_id.get()} state: {to_update_state.get()}"))
                  ##
btn1.pack(padx=50,pady=20)
#------------------------------------------- COMBINING QR CODE -------------------------
def combine_qr_codes(input_folder, output_folder="output", qr_size=350, max_per_page=20):
        #Combines multiple PNG QR codes into A4-sized sheets (210x297 mm).

        #Parameters:
        #input_folder (str): Folder containing QR code PNG files.
        #output_folder (str): Folder to save the combined A4 images.
        #qr_size (int): Size of each QR code in pixels.
        #max_per_page (int): Maximum number of QR codes per A4 sheet.
    try:
        os.makedirs(output_folder, exist_ok=True)

        # Load all PNG files from the input folder
        files = [f for f in os.listdir(input_folder) if f.lower().endswith(".png")]
        if not files:
            print("No PNG files found in the specified folder.")
            messagebox.showerror('No QR found','QR code folder empty. Try adding new QR using "Generate QR"')
            return

        # Calculate grid size (4x5 for 20 QR codes per page)
        cols = 4
        rows = 5
        margin = 30
        text_height = 50  # Height reserved for the filename text
        page_width, page_height = 2480, 3508  # A4 size at 300 DPI

        # Adjust QR code size to fit 20 per page
        qr_size = min((page_width - margin * (cols + 1)) // cols, (page_height - margin * (rows + 1) - rows * text_height) // rows)

        # Font setup
        try:
            font = ImageFont.truetype("arial.ttf", 28)
        except IOError:
            print("Arial font not found. Using default font.")
            font = ImageFont.load_default()

        page_number = 1
        total_pages = math.ceil(len(files) / max_per_page)
        img_count = 0

        # Iterate through the files and group them into pages
        while img_count < len(files):
            # Create a new A4-sized blank image
            page = Image.new("RGB", (page_width, page_height), "white")
            draw = ImageDraw.Draw(page)

            for row in range(rows):
                for col in range(cols):
                    if img_count >= len(files):
                        break

                    file_name = files[img_count]
                    img_path = os.path.join(input_folder, file_name)

                    try:
                        qr_img = Image.open(img_path).resize((qr_size, qr_size))
                    except Exception as e:
                        print(f"Error loading {file_name}: {e}")
                        img_count += 1
                        continue

                    # Calculate position
                    x = margin + col * (qr_size + margin)
                    y = margin + row * (qr_size + margin + text_height)

                    # Add the filename text above the QR code
                    text_width, _ = draw.textbbox((0, 0), file_name, font=font)[2:4]
                    text_x = x + (qr_size - text_width) // 2
                    draw.text((text_x, y), file_name, fill="black", font=font)

                    # Paste the QR code image below the text
                    page.paste(qr_img, (x, y + text_height))

                    img_count += 1

            # Save the page
            output_path = os.path.join(output_folder, f"combined_page_{page_number}.png")
            page.save(output_path)
            print(f"Page {page_number}/{total_pages} saved: {output_path}")
            page_number += 1

        #print("All QR codes combined successfully!")
        messagebox.showinfo(f'QR combine',f'QR codes have been merged into a single file in: {output_path}')

    except Exception as e:
        print(f"An error occurred: {e}")
#-------------------------------------- qr_management ---------------------------------------

def number_to_qr(number):
    folder_name = "qr_codes"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    data = str(number)
    qr = qrcode.make(data)
    
    file_path = os.path.join(folder_name, f"{data}.png")
    qr.save(file_path)
    messagebox.showinfo("A new QR code has been created: ",f"QR code saved at: {file_path}")


def gen_qr():
    if(check_table_conn()):
        ls = cursor.execute(f"SELECT MAX(plate_id) FROM {table_name}")
        ls = str(ls.fetchone()).strip('(),')
        if(ls == "None"):
            new_id = 1
            
           
        else:
            ls = int(ls)
            new_id = ls + 1
        number_to_qr(new_id)
        cursor.execute(f'insert into {table_name} values({new_id},1)')

        cursor.commit()
        #messagebox.showinfo("QR DB","A new QR code has been created")
    else:
        messagebox.showerror('DB error',"Database or Table does not exist. Creating one.")
        create_table()
        
def rem_qr():
    if(check_table_conn()):
       cursor_n = cursor.cursor()
       to_rem  = del_pid.get()
       if len(to_rem)>0:
           cursor_n.execute(f"DELETE FROM {table_name} WHERE plate_id = {int(to_rem)}")
           
           if( cursor_n.rowcount==0):
               messagebox.showerror('Error','No such plate exist in DB')
           else:
               messagebox.showinfo('Info',"Deleted plate from DB")
               path_f = f"C:\\Users\\karth\\Documents\\python\\canteen-proj\\QuickServe\\qr_codes\\{to_rem}.png"
               os.remove(path_f) 
               cursor.commit()
       else:
           messagebox.showerror('Error',"You're entering null value")
      
           
        

qr_manage = ttk.Frame(master=nb)
qr_lab = ttk.Label(qr_manage,text="QR Code Management",font=('Roboto',22,'bold',)).pack()
bf = ttk.Frame(qr_manage)

qr_add = ttk.Button(bf,text="Generate QR",command=gen_qr).pack(side='left',padx=10,ipadx=50,ipady=50)
combine_btn = ttk.Button(bf,text="Combine QR codes",command = lambda: combine_qr_codes("qr_codes")).pack(side='left',ipadx=30,ipady=50,padx=10,pady=50)
qr_remove = ttk.Button(bf,text="Remove QR",command=rem_qr).pack(side='left',padx=10,ipadx=50,ipady=50)

bf2 = ttk.Frame(qr_manage)
qr_say = ttk.Label(bf2,text='Enter Plate_ID: ',font=('Roboto'),foreground='tomato').pack(side='left')
del_pid = tk.StringVar(value=None)
rm_entry = ttk.Entry(master=bf2,textvariable=del_pid)
rm_entry.pack(side='left')

bf.pack()
bf2.pack(padx=200,fill='x')

#----------------------------------- Loop and notebook-menu section ----------------------------------------------
nb.add(menu_tab,text="Menu")
nb.add(db_tab,text="Database")
nb.add(qr_manage,text="QR code")
nb.add(modify_db,text="(testing)")
#root.protocol("WM_DELETE_WINDOW", on_closing)
web_thread = threading.Thread(target = server_run)
web_thread.start()
nb.pack()
root.mainloop()
scanner.stop()
