"""
TRIAL 2
"""
import datetime
from tkinter import *
from tkinter.ttk import Combobox
from tkcalendar import DateEntry
import tkinter.ttk as ttk
import mysql.connector as m
import tkinter.messagebox as mb
from matplotlib import pyplot as plt

mydatabase = m.connect(host="localhost", user="root", password="Root", database="expense_tracker")
initial_balance = 50000.0
cursor=mydatabase.cursor()
cursor.execute("create table if not exists expenses(Sr.No. int primary key auto_increment,Date date,Category varchar(100),Description varchar(100),Amount float,Paymentmode varchar(100))")
mydatabase.commit()

"""
The SalaryDialog class is defined, which represents a pop-up window for adding salary. It inherits from the Toplevel class.
In the SalaryDialog class, the __init__ method is defined to set up the window and its components.
The add_salary method in the SalaryDialog class is used to add the salary entered by the user. It updates the initial_balance variable and displays a message box with the success message.
The insertion function is defined, which is used to insert an expense record into the database. It retrieves the values from the input fields, executes an SQL query, and commits the changes to the database.
The add_salary function creates an instance of the SalaryDialog class, which opens the salary entry window.
"""
class SalaryDialog(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Salary")
        self.geometry("300x100")
        self.resizable(False, False)

        self.salary_entry = Entry(self)
        self.salary_entry.pack(pady=10)

        button_frame = Frame(self)
        button_frame.pack()

        add_button = Button(button_frame, text="Add", command=self.add_salary)
        add_button.pack(side=LEFT, padx=5)

        cancel_button = Button(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side=LEFT)

    def add_salary(self):
        global initial_balance
        salary = self.salary_entry.get()
        try:
            salary = float(salary)
            initial_balance += salary
            mb.showinfo("Salary Added", "The salary has been added successfully.")
            self.destroy()
        except ValueError:
            mb.showerror("Invalid Salary", "Please enter a valid salary amount.")


    """
    Add Expense:
    Allows users to enter details of their expenses, including date, category, description, amount, and payment mode.
    Validates the input fields to ensure all required information is provided.
    Inserts the expense record into the MySQL database.
    Displays a success message upon successful insertion.
    """
def insertion():
    global date, catvalue, descvalue, amountvalue, payvalue

    if not date.get() or not catvalue.get() or not descvalue.get() or not amountvalue.get() or not payvalue.get():
        mb.showerror("Fields Empty", "Please fill all missing fields before pressing the add button")
    else:
        cursor = mydatabase.cursor()
        query = "insert into expenses(Date,Category,Description,Amount,Paymentmode) values(%s,%s,%s,%s,%s)"
        cursor.execute(query, [date.get_date(), catvalue.get(), descvalue.get(), amountvalue.get(), payvalue.get()])
        mydatabase.commit()
        clear_fields()
        mb.showinfo("Expense Added","The expense has been entered successfully")
"""
Add Salary:
Opens a dialog box for users to add their salary amount.
Updates the initial balance variable by adding the salary amount.
Displays a success message upon successful addition.
"""
def add_salary():
    SalaryDialog(root1)

"""
View Balance:
Calculates the remaining balance by subtracting the total expenses from the initial balance.
Retrieves the total expenses from the database using SQL queries.
Displays the remaining balance to the user.
"""
def view_balance():
    global initial_balance

    cursor = mydatabase.cursor()
    cursor.execute("SELECT SUM(Amount) FROM expenses")
    total_expenses = cursor.fetchone()[0]

    if total_expenses is not None:
        remaining_balance = initial_balance - total_expenses
        mb.showinfo("Remaining Balance", f"The remaining balance is: {remaining_balance}")
    else:
        mb.showinfo("Remaining Balance", f"The remaining balance is: {initial_balance}")

"""
View All Expenses:
Retrieves all expense records from the database and displays them in a tabular format.
Utilizes the ttk.Treeview widget for a user-friendly display.
Supports horizontal and vertical scrolling for easy navigation.
Implements a delete function to remove selected expense records from the database.
"""
def list_all_expenses():
    global table

    table.delete(*table.get_children())
    cursor=mydatabase.cursor()
    cursor.execute("select * from expenses")
    tabledata=cursor.fetchall()
    for values in tabledata:
        table.insert("",END,values=values)

def delete_expenses():
    global table
    if not table.selection():
        mb.showerror('No record selected!', 'Please select a record to delete!')
        return

    current_selected_expense = table.item(table.focus())
    values_selected = current_selected_expense['values']

    surety = mb.askyesno('Are you sure?', f'Are you sure that you want to delete the record of {values_selected[2]}')

    if surety:
        cursor=mydatabase.cursor()
        cursor.execute('delete from expenses where SrNo=%s '% values_selected[0])
        mydatabase.commit()

        list_all_expenses()
        mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')


def clear_fields():
    global date, catvalue, descvalue, amountvalue, payvalue

    today_date=datetime.datetime.now().date()
    date.set_date(today_date)
    descvalue.set(""),catvalue.set("Select a Category"), amountvalue.set(""), payvalue.set("Select a payment mode")


"""
View Graph:
Opens a new window for users to plot graphs based on expense data.
Allows users to select a date range and plot type (histogram or pie chart).
Retrieves expense data from the database and generates the desired graph using matplotlib.
Provides visual representation of expense distribution by category.
"""
def graph_plot():
    top = Toplevel(root1)
    top.title("Graph Plot")
    top.geometry("300x200")
    top.resizable(False, False)

    start_label = Label(top, text="From Date:")
    start_label.pack(pady=5)
    start_date = DateEntry(top, date=datetime.datetime.now().date())
    start_date.pack(pady=5)
    start_date.bind("<Return>", lambda event: plot_graph())

    end_label = Label(top, text="To Date:")
    end_label.pack(pady=5)
    end_date = DateEntry(top, date=datetime.datetime.now().date())
    end_date.pack(pady=5)
    end_date.bind("<Return>", lambda event: plot_graph())

    plot_label = Label(top, text="Select Plot Type:")
    plot_label.pack(pady=5)
    plot_type = Combobox(top, values=["Histogram", "Pie Chart"])
    plot_type.set("Histogram")
    plot_type.pack(pady=5)
    plot_type.bind("<Return>", lambda event: plot_graph())

    def plot_graph():
        start = start_date.get_date()
        end = end_date.get_date()
        plot_type_selected = plot_type.get()

        cursor = mydatabase.cursor()
        query = "SELECT Category, SUM(Amount) AS TotalAmount FROM expenses WHERE Date BETWEEN %s AND %s GROUP BY Category"
        cursor.execute(query, (start, end))
        result = cursor.fetchall()

        categories = []
        amounts = []

        for row in result:
            categories.append(row[0])
            amounts.append(row[1])

        if plot_type_selected == "Histogram":
            plt.bar(categories, amounts)
            plt.xlabel('Categories')
            plt.ylabel('Total Amount')
            plt.title('Expense Distribution by Category')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
        elif plot_type_selected == "Pie Chart":
            plt.pie(amounts, labels=categories, autopct='%1.1f%%')
            plt.title('Expense Distribution by Category')
            plt.axis('equal')
            plt.show()

    plot_button = Button(top, text="Plot", command=plot_graph)
    plot_button.pack(pady=10)

"""
The main code block starts by creating the root window.
Various GUI components, such as labels, buttons, and entry fields, are defined and placed using the place geometry manager.
The addexpense function is called when the "Add Expense" button is clicked. It creates a frame and adds input fields for date, category, description, amount, and payment mode. It also includes a button to submit the expense record.
The view_all_expenses function is called when the "View Expenses" button is clicked. It creates a frame and a table widget to display all the expense records from the database.
The root window's mainloop is started, which keeps the application running and handles user interactions.
"""

root1 = Tk()
root1.geometry("500x300")
root1.title("Expense_Tracker")
root1.maxsize(800, 450)
root1.minsize(800, 450)
root1.configure(bg="Lavender")


def addexpense():
    global date, catvalue, descvalue, amountvalue, payvalue
    frame2 = Frame(root1, bg="SkyBlue")
    Date = Label(frame2, text="Date").grid(row=15, pady=5, padx=3)
    date = DateEntry(frame2, date=datetime.datetime.now().date())
    date.grid(row=15, column=2)

    Category = Label(frame2, text="Category").grid(row=16, pady=5, padx=3)
    catvalue = StringVar()
    catvalue = Combobox(frame2, values=["Travel", "Food", "Clothing", "Rent", "Fuel", "Medicines", "Others"])
    catvalue.set("Select a Category")
    catvalue.config(width=15)
    catvalue.grid(row=16, column=2)

    Description = Label(frame2, text="Description").grid(row=17, pady=5, padx=3)
    descvalue = StringVar()
    descentry = Entry(frame2, textvariable=descvalue)
    descentry.grid(row=17, column=2)

    Amount = Label(frame2, text="Amount").grid(row=18, pady=5, padx=3)
    amountvalue = DoubleVar()
    amountentry = Entry(frame2, textvariable=amountvalue)
    amountentry.grid(row=18, column=2)

    Paymentmode = Label(frame2, text="Mode of Payment").grid(row=19, pady=5, padx=5)
    payvalue = StringVar()
    payvalue = Combobox(frame2, values=["GPay", "Cash", "Credit Card", "NetBanking", "Debit Card", "NEFT"])
    payvalue.set("Select a payment mode")
    payvalue.grid(row=19, column=2)

    Button2 = Button(frame2, text="ENTER", command=insertion).grid(row=21, column=1, pady=5)

    frame2.place(x=200, y=40, height=400, relheight=0.95, relwidth=0.75)


def view_all_expenses():
    global table
    frame3 = Frame(root1, bg="SkyBlue")
    table = ttk.Treeview(frame3, selectmode=BROWSE,
                         columns=('Id', 'Date', 'Category', 'Description', 'Amount', 'Mode of Payment'))
    x_Scroller = Scrollbar(table, orient=HORIZONTAL, command=table.xview)
    y_Scroller = Scrollbar(table, orient=VERTICAL, command=table.yview)
    x_Scroller.pack(side=BOTTOM, fill=X)
    y_Scroller.pack(side=RIGHT, fill=Y)
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
                    background="white",
                    foreground="black",
                    fieldbackground="white")
    table.config(yscrollcommand=y_Scroller.set, xscrollcommand=x_Scroller.set)

    table.heading('Id', text='S No.', anchor=CENTER)
    table.heading('Date', text='Date', anchor=CENTER)
    table.heading('Category', text='Category', anchor=CENTER)
    table.heading('Description', text='Description', anchor=CENTER)
    table.heading('Amount', text='Amount', anchor=CENTER)
    table.heading('Mode of Payment', text='Mode of Payment', anchor=CENTER)

    table.column('#0', width=0, stretch=NO)
    table.column('#1', width=50, stretch=NO)
    table.column('#2', width=95, stretch=NO)
    table.column('#3', width=150, stretch=NO)
    table.column('#4', width=150, stretch=NO)
    table.column('#5', width=135, stretch=NO)
    table.column('#6', width=125, stretch=NO)

    table.place(relx=0, y=0, relheight=0.95, relwidth=1)


    list_all_expenses()

    frame3.place(x=200, y=40, relheight=0.96, relwidth=0.76)

Label(root1, text="EXPENSE TRACKER", font="comicsansms 18 bold", border=4, relief=RIDGE, width=24,
      background="beige").pack(side=TOP, fill=X)

frame1 = Frame(root1, bg="Pink")
Button(frame1, text="Add expense", width=15, command=addexpense).place(x=10, y=30, relwidth=0.85, rely=0.05)
Button(frame1, text="View Expenses", width=15, command=view_all_expenses).place(x=10, y=60, relwidth=0.85, rely=0.1)
Button(frame1, text="Delete Expenses", width=15, command=delete_expenses).place(x=10, y=90, relwidth=0.85, rely=0.15)
Button(frame1, text="View Graph", width=15, command=graph_plot).place(x=10, y=120, relwidth=0.85, rely=0.2)
Button(frame1, text="Add Salary", width=15, command=add_salary).place(x=10, y=150, relwidth=0.85, rely=0.25)
Button(frame1, text="View Balance", width=15, command=view_balance).place(x=10, y=195, relwidth=0.85, rely=0.25)
Button(frame1, text="EXIT", command=root1.destroy).place(x=10, y=240, relwidth=0.85, rely=0.25)


frame1.place(y=40, relheight=0.95, relwidth=0.25)

root1.mainloop()
