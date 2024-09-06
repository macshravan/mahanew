
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, Toplevel, Label, Button, Entry
from PIL import Image, ImageTk
import csv
import os
from datetime import datetime
from functools import partial
# Paths for menu CSV files
menu_files = {
    "rooms": "room.csv",
    "facilities": "facilities.csv",
    "beverages": "beverages.csv",
    "others": "others.csv"
}

# Dummy data for menus
dummy_image_path = "dummy.jpeg"
dummy_data = {
    "rooms": [["1", dummy_image_path, "Spring Roll", "5", "10"], ["2", dummy_image_path, "Nachos", "4", "8"]],
    "facilities": [["1", dummy_image_path, "Fried Rice", "8", "15"], ["2", dummy_image_path, "Noodles", "7", "20"]],
    "beverages": [["1", dummy_image_path, "Orange Juice", "3", "25"], ["2", dummy_image_path, "Apple Juice", "3", "30"]],
    "others": [["1", dummy_image_path, "Vanilla", "2", "50"], ["2", dummy_image_path, "Chocolate", "2", "45"]]
}

# Ensure CSV files exist with dummy data
for category, file in menu_files.items():
    if not os.path.exists(file):
        with open(file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["RoomID", "ImagePath", "Name", "Cost", "Stock"])
            writer.writerows(dummy_data[category])

if not os.path.exists('request.csv'):
    with open('request.csv', mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Time', 'Category', 'Item', 'Quantity', 'Cost', 'Email', 'Username'])

# Variables to store the logged-in user's email and username
current_user_email = None
current_user_username = None

def user_exists(email):
    if not os.path.exists('user.csv'):
        return False
    with open('user.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == email:  # Email is in the second column
                return True
    return False

# Function to add a new user to the CSV file
def add_user(username, email, password):
    with open('user.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([username, email, password])

# Function to validate user login
def validate_login(email, password):
    if not os.path.exists('user.csv'):
        return False
    with open('user.csv', mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[1] == email and row[2] == password:  # Email is in the second column, password in the third
                global current_user_username
                current_user_username = row[0]  # Username is in the first column
                return True
    return False

def set_background(window, image_path):
    # Load the image using PIL
    bg_image = Image.open(image_path)
    window_width = window.winfo_screenwidth()
    window_height = window.winfo_screenheight()
    bg_image=bg_image.resize((window_width,window_height))
    bg_photo = ImageTk.PhotoImage(bg_image)
    
    print(window_width,window_height)


    # Create a label with the image
    bg_label = tk.Label(window, image=bg_photo)
    bg_label.image = bg_photo  # Keep a reference to avoid garbage collection
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
def admin():
    def load_data():
        if os.path.exists("request.csv"):
            with open("request.csv", mode="r") as file:
                reader = csv.reader(file)
                return list(reader)
        else:
            return []

    def update_csv(data):
        with open("request.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def refresh_display():
        for row in tree.get_children():
            tree.delete(row)

        data = load_data()
        if data:
            columns = data[0]
            tree.config(columns=columns)
            for col in columns:
                tree.heading(col, text=col)
            
            for index, row in enumerate(data[1:]):
                tags = ()
                if len(row) > 0 and row[-1] == "Checkedin":
                    tags = ("checkedin",)
                tree.insert("", "end", iid=index, values=row, tags=tags)
            
            tree.tag_configure("checkedin", background="yellow")

    def mark_checkin():
        selected_items = tree.selection()
        if selected_items:
            # Assuming the first selected item is the one we want
            selected_item = selected_items[0]
            index = tree.index(selected_item)
            data = load_data()
            data[index+1][-3] = "Checkedin"
            data[index+1][-2]=datetime.now()
            # +1 because the first row is header
            update_csv(data)
            refresh_display()

    def mark_done():
        selected_items = tree.selection()
        if selected_items:
            # Assuming the first selected item is the one we want
            selected_item = selected_items[0]
            index = tree.index(selected_item)
            data = load_data()
            with open('checkoutdata.csv','a',newline='') as f:
                csvwriter=csv.writer(f,delimiter=',')
                data[index+1][-1]=datetime.now()
                csvwriter.writerow(data[index+1])
            data.pop(index+1)  # +1 because the first row is header
            update_csv(data)
            refresh_display()

    root = tk.Tk()
    root.title("CSV Request Viewer")
    root.geometry("800x400")

    frame = tk.Frame(root)
    frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(frame)
    scroll_y = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scroll_x = tk.Scrollbar(frame, orient="horizontal", command=canvas.xview)
    tree = ttk.Treeview(canvas, show="headings")

    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=tree, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

    frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    refresh_display()

    frame_buttons = tk.Frame(root)
    frame_buttons.pack(side="bottom", fill="x")

    checkin_button = tk.Button(frame_buttons, text="Checkin", command=mark_checkin)
    checkin_button.pack(side="left", fill="x")

    checkout_button = tk.Button(frame_buttons, text="Checkout", command=mark_done)
    checkout_button.pack(side="left", fill="x")

    root.mainloop()




def login():
    global current_user_email
    email = email_entry.get()
    password = password_entry.get()
    ##Loading the image using PIL
    if email!='admin' and password!='admin':
        if validate_login(email, password):
            current_user_email = email
            messagebox.showinfo("Login Success", "Logged in successfully!")
            login_window.destroy()
            home_page()
        else:
            messagebox.showerror("Login Error", "Invalid email or password.")
    else:
        admin()
            

def mainlogin():
    global email_entry, password_entry, login_window
    login_window = Toplevel(root)
    login_window.title('Login')
    login_window.geometry('400x400')  # Normal window size
    set_background(login_window, 'login.jpeg')
    email_label = tk.Label(login_window, text="Email:")
    email_label.pack(pady=10)
    email_entry = tk.Entry(login_window)
    email_entry.pack(pady=10)

    password_label = tk.Label(login_window, text="Password:")
    password_label.pack(pady=10)
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack(pady=10)

    login_button = tk.Button(login_window, text="Login", command=login)
    login_button.pack(pady=20)
    

def signUp():
    signUpWindow = Toplevel(root)
    signUpWindow.title('Sign Up')
    signUpWindow.geometry('400x400')  # Normal window size
    set_background(signUpWindow, 'signup.jpeg')
    username_label = tk.Label(signUpWindow, text="Username:")
    username_label.pack(pady=10)
    username_entry = tk.Entry(signUpWindow)
    username_entry.pack(pady=10)

    email_label = tk.Label(signUpWindow, text="Email:")
    email_label.pack(pady=10)
    email_entry = tk.Entry(signUpWindow)
    email_entry.pack(pady=10)

    password_label = tk.Label(signUpWindow, text="Password:")
    password_label.pack(pady=10)
    password_entry = tk.Entry(signUpWindow, show="*")
    password_entry.pack(pady=10)


    def processSignUp():
        username = username_entry.get()
        email = email_entry.get()
        password = password_entry.get()
        if user_exists(email):
            messagebox.showerror("Sign Up Error", "User already exists.")
        else:
            add_user(username, email, password)
            messagebox.showinfo("Sign Up Success", "Signed up successfully!")
            signUpWindow.destroy()
    
    signUpButton = tk.Button(signUpWindow, text="Sign Up", command=processSignUp)
    signUpButton.pack(pady=20)
##image_path = "signup.jpeg"  
##image = Image.open(image_path)
##photo = ImageTk.PhotoImage(image)
##label = tk.Label(signUpWindow, image=photo)
##label.pack()
def home_page():
    global home_window
    home_window = Toplevel(root)
    home_window.title("Home Page")
    home_window.wm_state("zoomed")
    set_background(home_window, 'welcome.jpeg')# Maximized state
    root.withdraw()

    welcome_label = tk.Label(home_window, text="Welcome to the Hotel Management System", font=("Arial", 18, "bold"))
    welcome_label.pack(pady=20)

    menu_label = tk.Label(home_window, text="Menu", font=("Arial", 16, "bold"))
    menu_label.pack(pady=10)

    menu_frame = tk.Frame(home_window)
    menu_frame.pack(pady=20)

    rooms_button = tk.Button(menu_frame, text="rooms", font=("Arial", 14), width=20, command=lambda: show_menu("rooms"))
    rooms_button.grid(row=0, column=0, padx=20, pady=10)

    view_cart_button = tk.Button(home_window, text="View Cart", font=("Arial", 14), command=lambda:view_cart())
    view_cart_button.pack(pady=20)

    def on_closing():
        root.deiconify()
        home_window.destroy()

    home_window.protocol("WM_DELETE_WINDOW", on_closing)

def show_menu(category):
    menu_window = Toplevel(home_window)
    menu_window.title(category)
    menu_window.wm_state("zoomed")  # Maximized state
    
    canvas = tk.Canvas(menu_window)
    set_background(canvas, 'menu.jpeg')
    scrollbar = tk.Scrollbar(menu_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    with open(menu_files[category], mode="r") as file:
        reader = csv.DictReader(file)
        items = list(reader)

    def go_back():
        if category!='rooms':
            menu_window.destroy()
            show_additional_categories()
        else:
            menu_window.destroy()
    row=0
    col=0
    for idx, item in enumerate(items):
        food_id, img_path, name, cost, stock = item["RoomID"], item["ImagePath"], item["Name"], item["Cost"], item["Stock"]
        frame = tk.Frame(scrollable_frame, relief=tk.RAISED, borderwidth=2)
        if idx%4==0:
            row+=1
            col=1
        print(row,col)
        frame.grid(row=row, column=col, padx=10, pady=10)
        
        col+=1

        try:
            img = Image.open(img_path)
            img = img.resize((150, 150), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
        except Exception:
            img = Image.open(dummy_image_path)
            img = img.resize((150, 150), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

        img_label = tk.Label(frame, image=img)
        img_label.image = img
        img_label.pack(pady=5)

        name_label = tk.Label(frame, text=name, font=("Arial", 14))
        name_label.pack(pady=5)

        cost_label = tk.Label(frame, text=f"Cost: Rs.{cost}", font=("Arial", 12))
        cost_label.pack(pady=5)

##        stock_label = tk.Label(frame, text=f"Stock: {stock}", font=("Arial", 12))
##        stock_label.pack(pady=5)
        if category=='rooms':
            quantity_label = tk.Label(frame, text="Number of members:")
            quantity_label.pack(pady=5)
        else:
            quantity_label = tk.Label(frame, text="quantity:")
            quantity_label.pack(pady=5)
        quantity_entry = tk.Entry(frame)
        quantity_entry.pack(pady=5)
        if category=='rooms':
            add_to_cart_button = tk.Button(frame, text="Add to Cart", command=partial(add_to_cart,category, food_id, name, cost, [stock,item['members']], quantity_entry))
            add_to_cart_button.pack(pady=10)
        else:
            add_to_cart_button = tk.Button(frame, text="Add to Cart", command=partial(add_to_cart,category, food_id, name, cost, stock, quantity_entry))
            add_to_cart_button.pack(pady=10)

    

    go_back_button = tk.Button(scrollable_frame, text="Go Back", command=go_back)
    go_back_button.grid(row=0,column=0,padx=10,pady=10)

def add_to_cart(category,food_id, name, cost, stock, quantity_entry):

    try:
        quantity = int(quantity_entry.get())
    except ValueError:
        messagebox.showerror("Error", "Invalid quantity. Please enter a valid number.")
        return

    if quantity <= 0:
        messagebox.showerror("Error", "Quantity must be greater than zero.")
        return
    if category=='rooms':
        if quantity > int(stock[1]):
            
            messagebox.showerror("Error", f"Not available max members {stock[1]}")
            return
            
        if int(stock[0])==0:
            
            messagebox.showerror("Error", f"Not available")
            return
            
    else:
        if quantity > int(stock):
            
            messagebox.showerror("Error", "Not available")
            return
    with open("view.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([category, name, cost, quantity, food_id])
    messagebox.showinfo("Success", f"Added {quantity} x {name} to cart.")
    
    # Prompt user for further action
    prompt_window = Toplevel()
    prompt_window.title("Continue Shopping")
    prompt_window.geometry("300x200")

    def continue_shopping():
        prompt_window.destroy()
        show_additional_categories()

    def view_cart_directly():
        prompt_window.destroy()
        view_cart()

    prompt_label = tk.Label(prompt_window, text="Do you want to continue shopping?", font=("Arial", 12))
    prompt_label.pack(pady=20)

    continue_button = tk.Button(prompt_window, text="Yes", command=continue_shopping)
    continue_button.pack(pady=10)

    view_cart_button = tk.Button(prompt_window, text="View Cart", command=view_cart_directly)
    view_cart_button.pack(pady=10)



def view_cart():
    cart_window = Toplevel(home_window)
    cart_window.title("Cart")
    cart_window.wm_state("zoomed")
    set_background(cart_window, 'cart.jpeg')# Maximized state
    continue_button = tk.Button(cart_window, text="add extra", command=lambda:show_additional_categories())
    continue_button.pack(pady=10)
    with open("view.csv", mode="r") as file:
        reader = csv.reader(file)
        cart_items = list(reader)

    if not cart_items:
        messagebox.showinfo("Cart", "Your cart is empty.")
        cart_window.destroy()
        return

    total_cost = 0
    def delete_item(idx):
        cart_items.pop(idx)
        with open("view.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(cart_items)
        cart_window.destroy()
        view_cart()
    
    with open('room.csv', mode="r") as file:
            reader = csv.DictReader(file)
            items = list(reader)
    names=[]
    for a in items:
        names+=[a['Name']]
    print(names)
    for idx, item in enumerate(cart_items):
        category, name, cost, quantity, food_id = item
        quantity = int(quantity)
        cost = int(cost)
        total_cost += cost * quantity
        item_frame = tk.Frame(cart_window)
        item_frame.pack(pady=5, fill="x")
        if name in names:
        
            item_label = tk.Label(item_frame, text=f"Item: {name}, members: {quantity}, Cost: Rs.{cost * quantity:.2f}", font=("Arial", 12))
            item_label.pack(side="left", padx=10)
        else:
            item_label = tk.Label(item_frame, text=f"Item: {name}, Quantity: {quantity}, Cost: Rs.{cost * quantity:.2f}", font=("Arial", 12))
            item_label.pack(side="left", padx=10)

        delete_button = tk.Button(item_frame, text="Delete", command=partial(delete_item, idx))
        delete_button.pack(side="right", padx=10)

    total_cost_label = tk.Label(cart_window, text=f"Total Cost: Rs.{total_cost:.2f}", font=("Arial", 14, "bold"))
    total_cost_label.pack(pady=10)

    def checkout():
        with open("view.csv", mode="r") as file:
            reader = csv.reader(file)
            cart_items = list(reader)

        total_cost = sum(int(item[2]) * int(item[3]) for item in cart_items)
        messagebox.showinfo("Checkout", f"Total cost: Rs.{total_cost:.2f}\nThank you for your purchase!")

        # Log the request
        with open("request.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            for item in cart_items:
                category, name, cost, quantity, food_id = item
                writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category, name, quantity, cost, current_user_email, current_user_username,"booked",None,None])

        # Update stock
        for item in cart_items:
            category, name, cost, quantity, food_id = item
            quantity = int(quantity)
            menu_file = menu_files[category]
            updated_items = []

            with open(menu_file, mode="r") as file:
                reader = csv.DictReader(file)
                items = list(reader)
                print(items)
                for menu_item in items:
                    if menu_item["RoomID"] == food_id:
                        if menu_file=='room.csv':
                            menu_item["Stock"] = str(int(menu_item["Stock"]) - 1)
                        else:
                            menu_item["Stock"] = str(int(menu_item["Stock"]) - quantity)
                    updated_items.append(menu_item)

            with open(menu_file, mode="w", newline="") as file:
                if menu_file=='room.csv':
                    writer = csv.DictWriter(file, fieldnames=["RoomID", "ImagePath", "Name", "Cost", "Stock","members"])
                else:
                    writer = csv.DictWriter(file, fieldnames=["RoomID", "ImagePath", "Name", "Cost", "Stock"])

                writer.writeheader()
                writer.writerows(updated_items)

        # Clear the cart after checkout
        with open("view.csv", mode="w", newline="") as file:
            file.truncate()

        cart_window.destroy()
        home_page()

    checkout_button = tk.Button(cart_window, text="Checkout", font=("Arial", 14), command=checkout)
    checkout_button.pack(pady=20)

def show_additional_categories():
    additional_window = Toplevel(root)
    additional_window.title("Additional Categories")
    additional_window.geometry("400x400")
    set_background(additional_window, 'login.jpeg')
    def show_category(category):
        additional_window.destroy()
        show_menu(category)

    facilities_button = tk.Button(additional_window, text="facilities", font=("Arial", 14), command=lambda: show_category("facilities"))
    facilities_button.pack(pady=10)
    beverages_button = tk.Button(additional_window, text="beverages", font=("Arial", 14), command=lambda: show_category("beverages"))
    beverages_button.pack(pady=10)
    others_button = tk.Button(additional_window, text="others", font=("Arial", 14), command=lambda: show_category("others"))
    others_button.pack(pady=10)
    view_cart_button = tk.Button(additional_window, text="View Cart", command=lambda:view_Cart())
    view_cart_button.pack(pady=10)

root = tk.Tk()
root.title('FIKA')
root.wm_state('zoomed')  # Maximized stateh
set_background(root,'welcome.jpeg')
welcome_label = tk.Label(root, text="Welcome to FIKA", font=("Arial", 18, "bold"))
welcome_label.pack(pady=20)


signup_button = tk.Button(root, text="Sign Up", command=signUp)
signup_button.pack(pady=10)



login_button = tk.Button(root, text="Login", command=mainlogin)
login_button.pack(pady=10)


root.mainloop()

