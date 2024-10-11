import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class SavingGoalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Saving Goal")

        self.goals = []

        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        # Input for saving goal
        tk.Label(self.frame, text="Amount:").grid(row=0, column=0)
        self.amount_entry = tk.Entry(self.frame)
        self.amount_entry.grid(row=0, column=1)

        # Separate inputs for Start Date
        tk.Label(self.frame, text="Start Year:").grid(row=1, column=0)
        self.start_year_entry = tk.Entry(self.frame, width=5)
        self.start_year_entry.grid(row=1, column=1, sticky='w')

        tk.Label(self.frame, text="Month:").grid(row=1, column=2)
        self.start_month_var = tk.StringVar(value="")  # Default to empty
        self.start_month_menu = tk.OptionMenu(self.frame, self.start_month_var, *[str(i) for i in range(1, 13)])
        self.start_month_menu.grid(row=1, column=3)

        tk.Label(self.frame, text="Day:").grid(row=1, column=4)
        self.start_day_entry = tk.Entry(self.frame, width=5)
        self.start_day_entry.grid(row=1, column=5)

        # Separate inputs for End Date
        tk.Label(self.frame, text="End Year:").grid(row=2, column=0)
        self.end_year_entry = tk.Entry(self.frame, width=5)
        self.end_year_entry.grid(row=2, column=1, sticky='w')

        tk.Label(self.frame, text="Month:").grid(row=2, column=2)
        self.end_month_var = tk.StringVar(value="")  # Default to empty
        self.end_month_menu = tk.OptionMenu(self.frame, self.end_month_var, *[str(i) for i in range(1, 13)])
        self.end_month_menu.grid(row=2, column=3)

        tk.Label(self.frame, text="Day:").grid(row=2, column=4)
        self.end_day_entry = tk.Entry(self.frame, width=5)
        self.end_day_entry.grid(row=2, column=5)

        # Progress selection
        tk.Label(self.frame, text="Progress:").grid(row=3, column=0)
        self.progress_var = tk.StringVar(value="")  # Default to empty
        self.progress_menu = tk.OptionMenu(self.frame, self.progress_var, "ongoing", "finished",
                                           command=self.toggle_progress_input)
        self.progress_menu.grid(row=3, column=1)

        # Input for progress when ongoing
        self.progress_amount_label = tk.Label(self.frame, text="Progress Amount:")
        self.progress_amount_label.grid(row=4, column=0)
        self.progress_amount_entry = tk.Entry(self.frame)
        self.progress_amount_entry.grid(row=4, column=1)

        self.add_button = tk.Button(self.frame, text="Add Goal", command=self.add_goal)
        self.add_button.grid(row=5, columnspan=6, pady=10)

        self.goal_listbox = tk.Listbox(self.root, width=50)
        self.goal_listbox.pack(pady=10)
        self.goal_listbox.bind("<Double-1>", self.show_goal_details)  # Bind double-click event

        self.delete_button = tk.Button(self.root, text="Delete Selected Goal", command=self.delete_goal)
        self.delete_button.pack(pady=5)

        # Initially hide the progress amount entry
        self.progress_amount_label.grid_remove()
        self.progress_amount_entry.grid_remove()

    def toggle_progress_input(self, selection):
        if selection == "ongoing":
            self.progress_amount_label.grid()
            self.progress_amount_entry.grid()
        else:
            self.progress_amount_label.grid_remove()
            self.progress_amount_entry.grid_remove()

    def add_goal(self):
        try:
            amount = float(self.amount_entry.get())
            start_year = int(self.start_year_entry.get())
            start_month = self.start_month_var.get() if self.start_month_var.get() != "" else 1  # Default to 1 if empty
            start_month = int(start_month)
            start_day = int(self.start_day_entry.get())

            end_year = int(self.end_year_entry.get())
            end_month = self.end_month_var.get() if self.end_month_var.get() != "" else 1  # Default to 1 if empty
            end_month = int(end_month)
            end_day = int(self.end_day_entry.get())

            # Validate month and day
            if not (1 <= start_month <= 12 and 1 <= end_month <= 12):
                raise ValueError("Month must be between 1 and 12.")
            if not (1 <= start_day <= 31 and 1 <= end_day <= 31):
                raise ValueError("Day must be between 1 and 31.")

            # Create date strings
            start_date = f"{start_year}-{str(start_month).zfill(2)}-{str(start_day).zfill(2)}"
            end_date = f"{end_year}-{str(end_month).zfill(2)}-{str(end_day).zfill(2)}"

            # Validate dates
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')

            progress = self.progress_var.get()
            if progress == "ongoing":
                progress_amount = float(self.progress_amount_entry.get())
                if progress_amount >= amount:
                    raise ValueError("Progress amount must be less than the goal amount.")
            else:
                progress_amount = amount  # For finished goals

            goal = {
                "amount": amount,
                "start_date": start_date,
                "end_date": end_date,
                "progress": progress,
                "progress_amount": progress_amount
            }
            self.goals.append(goal)
            self.update_goal_list()
            self.clear_entries()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def update_goal_list(self):
        self.goal_listbox.delete(0, tk.END)
        for goal in self.goals:
            display_text = f"Goal: ${goal['amount']} | Progress: {goal['progress']} | Progress Amount: {goal['progress_amount']}"
            self.goal_listbox.insert(tk.END, display_text)

    def delete_goal(self):
        selected_indices = self.goal_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection Error", "Please select a goal to delete.")
            return

        for index in selected_indices[::-1]:  # Delete from the end to avoid index shift
            del self.goals[index]

        self.update_goal_list()

    def clear_entries(self):
        self.amount_entry.delete(0, tk.END)
        self.start_year_entry.delete(0, tk.END)
        self.start_month_var.set("")  # Reset to empty
        self.start_day_entry.delete(0, tk.END)
        self.end_year_entry.delete(0, tk.END)
        self.end_month_var.set("")  # Reset to empty
        self.end_day_entry.delete(0, tk.END)
        self.progress_var.set("")  # Reset to empty
        self.progress_amount_entry.delete(0, tk.END)  # Clear progress amount

    def show_goal_details(self, event):
        selected_index = self.goal_listbox.curselection()
        if not selected_index:
            return

        index = selected_index[0]
        goal = self.goals[index]

        # Calculate progress percentage
        if goal['progress'] == "ongoing":
            percentage = (goal['progress_amount'] / goal['amount']) * 100
        else:
            percentage = 100  # Finished goals are 100% complete

        # Create a new window to display goal details
        details_window = tk.Toplevel(self.root)
        details_window.title("Goal Details")

        details_text = (
            f"Amount: ${goal['amount']}\n"
            f"Start Date: {goal['start_date']}\n"
            f"End Date: {goal['end_date']}\n"
            f"Progress: {goal['progress']}\n"
            f"Progress Amount: {goal['progress_amount']}\n"
            f"Completion Percentage: {percentage:.2f}%"
        )
        tk.Label(details_window, text=details_text).pack(padx=10, pady=10)

        close_button = tk.Button(details_window, text="Close", command=details_window.destroy)
        close_button.pack(pady=5)


if __name__ == "__main__":
    root = tk.Tk()
    app = SavingGoalApp(root)
    root.mainloop()
