import tkinter as tk
from tkinter import messagebox  # pop up the prompt box
from tkcalendar import DateEntry  # date selection control
from database import User, Spending

# 创建窗口 Creating a window
root = tk.Tk()
root.title("Creating New Spending")
root.geometry("300x300")  # set the size of the window, width x height


# 标签和输入框 label and input box
def create_ui():
    # pack() is layout management function, padx - horizontal spacing, pady - vertical spacing
    tk.Label(root, text="Create new spending").pack(pady=10)

    # Spending input 金额输入
    # anchor='w': Specifies that the control is left aligned (w = west, for left).
    # tk.Entry(): control for text input.
    tk.Label(root, text="Amount:").pack(anchor='w', padx=30)
    amount_entry = tk.Entry(root)
    amount_entry.pack(padx=30, pady=5)

    # Category input 类别输入
    tk.Label(root, text="Category:").pack(anchor='w', padx=30)
    category_entry = tk.Entry(root)
    category_entry.pack(padx=30, pady=5)

    # Spending date input 消费日期输入
    # DateEntry(): Date selection control from tkcalendar, allows the user to select a date from the calendar. Pink!!!
    tk.Label(root, text="Spending Date:").pack(anchor='w', padx=30)
    date_entry = DateEntry(root, width=16, background='pink',
                           foreground='white', borderwidth=2)
    date_entry.pack(padx=30, pady=5)

    # Submit bottom 提交按钮
    def submit_data():
        amount = amount_entry.get()
        category = category_entry.get()
        date = date_entry.get()

        # Check if not empty 检查输入是否为空
        if not category or not amount or not date:
            messagebox.showwarning("Input Error", "Please fill all fields.")
        else:
            messagebox.showinfo("Data Submitted", f"Amount: {amount}\nCategory: {category}\nDate: {date}")

            # We can write code here to pop up input data to the database 在此处可以添加代码来将数据保存到数据库中

    # Bottom 按钮
    # Frame is created in the main window root to hold the buttons  在主窗口 root 中创建了一个 Frame，来存放按钮
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)

    # root.quit: When the user clicks the "Back" button, the application is quit.
    """ This quit function should change to "back to Main Dashboard function" 这个应该改为返回主界面 """
    back_button = tk.Button(button_frame, text="Back", command=root.quit)
    back_button.pack(side="left", padx=10)

    finish_button = tk.Button(button_frame, text="Submit", command=submit_data)
    finish_button.pack(side="right", padx=10)


create_ui()

# Enter the main event loop, keep the window displayed, and wait for the user to act.
root.mainloop()