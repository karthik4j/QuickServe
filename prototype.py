#UI layout test
import tkinter as tk
from tkinter import ttk

from tkinter import messagebox
from tkinter import PhotoImage
import os
import sqlite3
import threading 

global table_name
global file
global conn
global table_name

file ="python_proj.db"
table_name = "my_plates" 

#testing if the connector exists, otherwise we create one
def get_sql_conn():
    try: 
      conn = sqlite3.connect(file) 
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
root = tk.Tk()

window_width = 650
window_height = 500
root.title("QuickServe")
lent = int((root.winfo_screenheight()/2)-window_height/2)
widt = int((root.winfo_screenwidth()/2)-window_width/2)
root.geometry("{}x{}+{}+{}".format(window_width,window_height,widt,lent))
root.minsize(window_width,window_height)
root.maxsize(window_width,window_height)

nb = ttk.Notebook(root)
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
def display_plates():
    list_of_plates = cursor.execute(f'SELECT * from {table_name}')
    list_of_plates = list_of_plates.fetchall()
    for i in list_of_plates:
        print(i)
      
#------------------------------------------------------------ MENU PAGE CODE ------------------------------------------

frame1 = ttk.Frame(menu_tab,relief='ridge')
frame2 = ttk.Frame(menu_tab)

scan_g_img = PhotoImage(file="button.png")
scan_b_img =  PhotoImage(file='red-b.png')

lab0 = ttk.Label(frame1,text="Scan options: ",font=("Roboto",22,"bold")).pack(pady=10)
                                    
scan_g = ttk.Button(frame1,text='Available',image = scan_g_img,command=create_plate).pack(pady=10)
scan_b = ttk.Button(frame1,text='USE',image=scan_b_img,command=display_plates)
#scan_g.pack(expand=True,fill='both')
scan_b.pack(padx=10)


#frame1.pack(expand=True,fill='both',side='left')
frame1.pack(side='left',ipadx=10,ipady=10)

lab1 = ttk.Label(frame2,text='Available plate count is: 200',font=('Roboto', 18))
lab1.pack(pady=10)
frame2.pack(side='top',ipadx=50,ipady=50)
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
sql_status_lb = ttk.Label(master=db_status_f,text=f"SQL connection status: ",font=('Roboto',22)).pack(side='left')

sql_status = ttk.Label(master=db_status_f,textvariable=ok_sql,foreground='green',font=('Roboto',22))
sql_status.pack(side='left')

def update_lab_sql():
    if(check_table_conn()):
        ok_sql.set('Connected')
        sql_status.configure(foreground='green')
    else:
        ok_sql.set('Not connected')
        sql_status.configure(foreground='tomato')
update_lab_sql()

refresh_btn = ttk.Button(db_status_f,text='Refresh',command=refresh)
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

btn_ok = tk.Button(db_tab,text="Drop database",font=("Roboto",14,"bold"),command=kill_db)
btn_ok.pack()
    
#--------------------------------------- Modify DB  -----------------------------------------------------------------
modify_db = ttk.Frame(nb)
to_update_plate_id = tk.StringVar(value=None)
to_update_state = tk.StringVar(value=None)

entry_fram = ttk.Frame(modify_db)
lb = ttk.Label(modify_db,text="Update plate ",font=('Roboto','14')).pack()

pid_fram =ttk.Frame(entry_fram)
lb1 = ttk.Label(pid_fram,text="PID").pack(side='left')
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
btn1.pack()
#-------------------------------------- On closing
"""def on_closing():
    cursor.close()
    root.destroy() 
"""
#----------------------------------- Loop and notebook-menu section ----------------------------------------------
nb.add(menu_tab,text="Menu")
nb.add(db_tab,text="Database")
nb.add(modify_db,text="(testing)")
#root.protocol("WM_DELETE_WINDOW", on_closing)
nb.pack()
root.mainloop()
