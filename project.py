import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3


conn = sqlite3.connect("sklad_bolnica.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS postavki (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    supplier TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
user = cursor.fetchone()

if user is None:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))

conn.commit()


def login():
    username = entry_login.get()
    password = entry_password.get()

    if username == "" or password == "":
        messagebox.showwarning("Ошибка", "Введите имя пользователя и пароль")
        return

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    user = cursor.fetchone()

    if user:
        login_window.destroy()
        open_main_window(username)
    else:
        messagebox.showerror("Ошибка", "Неверное имя пользователя или пароль")


def add_worker():
    username = entry_new_login.get()
    password = entry_new_password.get()

    if username == "" or password == "":
        messagebox.showwarning("Ошибка", "Заполните поля нового работника")
        return

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        messagebox.showinfo("Готово", "Работник добавлен")
        entry_new_login.delete(0, tk.END)
        entry_new_password.delete(0, tk.END)
    except:
        messagebox.showerror("Ошибка", "Такой работник уже существует")


def add_item():
    name = entry_name.get()
    category = entry_category.get()
    quantity = entry_quantity.get()
    supplier = entry_supplier.get()
    date = entry_date.get()

    if name == "" or category == "" or quantity == "" or supplier == "" or date == "":
        messagebox.showwarning("Ошибка", "Заполните все поля")
        return

    try:
        quantity = int(quantity)
    except:
        messagebox.showwarning("Ошибка", "Количество должно быть числом")
        return

    cursor.execute("""
    INSERT INTO postavki (name, category, quantity, supplier, date)
    VALUES (?, ?, ?, ?, ?)
    """, (name, category, quantity, supplier, date))

    conn.commit()
    clear_fields()
    show_items()


def show_items():
    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("SELECT * FROM postavki")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def delete_item():
    selected = tree.selection()

    if not selected:
        messagebox.showwarning("Ошибка", "Выберите запись для удаления")
        return

    item = tree.item(selected)
    item_id = item["values"][0]

    cursor.execute("DELETE FROM postavki WHERE id = ?", (item_id,))
    conn.commit()
    show_items()
    clear_fields()


def select_item(event):
    selected = tree.selection()

    if not selected:
        return

    item = tree.item(selected)
    values = item["values"]

    clear_fields()

    entry_id.insert(0, values[0])
    entry_name.insert(0, values[1])
    entry_category.insert(0, values[2])
    entry_quantity.insert(0, values[3])
    entry_supplier.insert(0, values[4])
    entry_date.insert(0, values[5])


def update_item():
    item_id = entry_id.get()
    name = entry_name.get()
    category = entry_category.get()
    quantity = entry_quantity.get()
    supplier = entry_supplier.get()
    date = entry_date.get()

    if item_id == "":
        messagebox.showwarning("Ошибка", "Выберите запись для изменения")
        return

    if name == "" or category == "" or quantity == "" or supplier == "" or date == "":
        messagebox.showwarning("Ошибка", "Заполните все поля")
        return

    try:
        quantity = int(quantity)
    except:
        messagebox.showwarning("Ошибка", "Количество должно быть числом")
        return

    cursor.execute("""
    UPDATE postavki
    SET name = ?, category = ?, quantity = ?, supplier = ?, date = ?
    WHERE id = ?
    """, (name, category, quantity, supplier, date, item_id))

    conn.commit()
    show_items()
    clear_fields()


def search_item():
    text = entry_search.get()

    for row in tree.get_children():
        tree.delete(row)

    cursor.execute("""
    SELECT * FROM postavki
    WHERE name LIKE ? OR category LIKE ? OR supplier LIKE ?
    """, ("%" + text + "%", "%" + text + "%", "%" + text + "%"))

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def clear_fields():
    entry_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)
    entry_supplier.delete(0, tk.END)
    entry_date.delete(0, tk.END)


def logout(window):
    window.destroy()
    create_login_window()


def open_main_window(username):
    global entry_id, entry_name, entry_category, entry_quantity
    global entry_supplier, entry_date, entry_search, tree
    global entry_new_login, entry_new_password

    root = tk.Tk()
    root.title("Учет складских поставок больницы")
    root.geometry("950x650")
    root.resizable(False, False)

    title = tk.Label(
        root,
        text="Учет складских поставок больницы",
        font=("Arial", 16, "bold")
    )
    title.pack(pady=10)

    user_label = tk.Label(
        root,
        text="В системе работает: " + username,
        font=("Arial", 10)
    )
    user_label.pack()

    frame_input = tk.Frame(root)
    frame_input.pack(pady=10)

    tk.Label(frame_input, text="ID").grid(row=0, column=0, padx=5, pady=5)
    entry_id = tk.Entry(frame_input, width=10)
    entry_id.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_input, text="Название").grid(row=1, column=0, padx=5, pady=5)
    entry_name = tk.Entry(frame_input, width=25)
    entry_name.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_input, text="Категория").grid(row=1, column=2, padx=5, pady=5)
    entry_category = tk.Entry(frame_input, width=25)
    entry_category.grid(row=1, column=3, padx=5, pady=5)

    tk.Label(frame_input, text="Количество").grid(row=2, column=0, padx=5, pady=5)
    entry_quantity = tk.Entry(frame_input, width=25)
    entry_quantity.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_input, text="Поставщик").grid(row=2, column=2, padx=5, pady=5)
    entry_supplier = tk.Entry(frame_input, width=25)
    entry_supplier.grid(row=2, column=3, padx=5, pady=5)

    tk.Label(frame_input, text="Дата").grid(row=3, column=0, padx=5, pady=5)
    entry_date = tk.Entry(frame_input, width=25)
    entry_date.grid(row=3, column=1, padx=5, pady=5)
    entry_date.insert(0, "24.06.2026")

    frame_buttons = tk.Frame(root)
    frame_buttons.pack(pady=5)

    tk.Button(frame_buttons, text="Добавить", width=15, command=add_item).grid(row=0, column=0, padx=5)
    tk.Button(frame_buttons, text="Изменить", width=15, command=update_item).grid(row=0, column=1, padx=5)
    tk.Button(frame_buttons, text="Удалить", width=15, command=delete_item).grid(row=0, column=2, padx=5)
    tk.Button(frame_buttons, text="Очистить", width=15, command=clear_fields).grid(row=0, column=3, padx=5)

    frame_search = tk.Frame(root)
    frame_search.pack(pady=5)

    tk.Label(frame_search, text="Поиск").grid(row=0, column=0, padx=5)
    entry_search = tk.Entry(frame_search, width=40)
    entry_search.grid(row=0, column=1, padx=5)

    tk.Button(frame_search, text="Найти", width=12, command=search_item).grid(row=0, column=2, padx=5)
    tk.Button(frame_search, text="Показать все", width=12, command=show_items).grid(row=0, column=3, padx=5)

    columns = ("id", "name", "category", "quantity", "supplier", "date")

    tree = ttk.Treeview(root, columns=columns, show="headings", height=12)

    tree.heading("id", text="ID")
    tree.heading("name", text="Название")
    tree.heading("category", text="Категория")
    tree.heading("quantity", text="Количество")
    tree.heading("supplier", text="Поставщик")
    tree.heading("date", text="Дата")

    tree.column("id", width=50)
    tree.column("name", width=180)
    tree.column("category", width=150)
    tree.column("quantity", width=100)
    tree.column("supplier", width=180)
    tree.column("date", width=120)

    tree.pack(pady=10)

    tree.bind("<<TreeviewSelect>>", select_item)

    frame_workers = tk.LabelFrame(root, text="Добавление работника")
    frame_workers.pack(pady=5)

    tk.Label(frame_workers, text="Имя").grid(row=0, column=0, padx=5, pady=5)
    entry_new_login = tk.Entry(frame_workers, width=20)
    entry_new_login.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_workers, text="Пароль").grid(row=0, column=2, padx=5, pady=5)
    entry_new_password = tk.Entry(frame_workers, width=20)
    entry_new_password.grid(row=0, column=3, padx=5, pady=5)

    tk.Button(frame_workers, text="Добавить работника", command=add_worker).grid(row=0, column=4, padx=5)

    tk.Button(root, text="Выйти из аккаунта", width=20, command=lambda: logout(root)).pack(pady=5)

    show_items()

    root.mainloop()


def create_login_window():
    global login_window, entry_login, entry_password

    login_window = tk.Tk()
    login_window.title("Вход в систему")
    login_window.geometry("350x250")
    login_window.resizable(False, False)

    title = tk.Label(
        login_window,
        text="Вход на склад больницы",
        font=("Arial", 14, "bold")
    )
    title.pack(pady=15)

    frame = tk.Frame(login_window)
    frame.pack(pady=10)

    tk.Label(frame, text="Имя работника").grid(row=0, column=0, padx=5, pady=5)
    entry_login = tk.Entry(frame, width=25)
    entry_login.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame, text="Пароль").grid(row=1, column=0, padx=5, pady=5)
    entry_password = tk.Entry(frame, width=25, show="*")
    entry_password.grid(row=1, column=1, padx=5, pady=5)

    tk.Button(login_window, text="Войти", width=15, command=login).pack(pady=10)

    info = tk.Label(
        login_window,
        text="Первый вход: admin / 1234",
        font=("Arial", 9)
    )
    info.pack()

    login_window.mainloop()


create_login_window()
conn.close()