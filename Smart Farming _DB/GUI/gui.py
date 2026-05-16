
import os, tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
import bcrypt

# env
_env = os.path.join(os.path.dirname(__file__), "..", ".env")
with open(_env) as _f:
    for _line in _f:
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip().strip('"\''))

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# WINDOW SETUP
root = tk.Tk()
root.title("Smart Farm Management System")
root.geometry("960x640")
root.configure(bg="#1f2937")
root.resizable(True, True)

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",    font=("Segoe UI", 10), padding=6)
style.configure("TLabel",     font=("Segoe UI", 10), background="#1f2937", foreground="#f3f4f6")
style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background="#1f2937", foreground="#f3f4f6")
style.configure("Sub.TLabel", font=("Segoe UI", 10), background="#111827", foreground="#9ca3af")
style.configure("Treeview",   background="#111827", foreground="#d1d5db",
                fieldbackground="#111827", rowheight=26, font=("Segoe UI", 10))
style.configure("Treeview.Heading", background="#0f172a", foreground="#9ca3af",
                font=("Segoe UI", 10, "bold"))
style.map("Treeview", background=[("selected", "#1d4ed8")])
style.configure("TEntry",    fieldbackground="#374151", foreground="#f3f4f6", insertcolor="#f3f4f6")
style.configure("TCombobox", fieldbackground="#374151", foreground="#f3f4f6")


container = tk.Frame(root, bg="#1f2937")
container.pack(fill="both", expand=True)

frames = {}

def show_frame(name):
    frames[name].tkraise()

def make_frame(name, bg="#1f2937"):
    f = tk.Frame(container, bg=bg)
    f.place(relwidth=1, relheight=1)
    frames[name] = f
    return f


def lbl(parent, text, row, col, bg="#111827", fg="#9ca3af", sticky="e", padx=6, pady=4):
    tk.Label(parent, text=text, bg=bg, fg=fg, font=("Segoe UI", 10)).grid(
        row=row, column=col, sticky=sticky, padx=padx, pady=pady)

def make_tree(parent, cols, heights=12):
    frame = tk.Frame(parent, bg="#111827")
    frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))
    tree = ttk.Treeview(frame, columns=cols, show="headings", height=heights)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=max(80, 120 if len(c) > 8 else 80), anchor="w")
    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="left", fill="y")
    return tree


login_frame = make_frame("login")

ttk.Label(login_frame, text="Smart Farm System", style="Header.TLabel").pack(pady=(60, 4))
ttk.Label(login_frame, text="Sign in to continue", style="TLabel").pack(pady=(0, 24))

lf_box = tk.Frame(login_frame, bg="#111827", padx=30, pady=30)
lf_box.pack()

tk.Label(lf_box, text="Email",    bg="#111827", fg="#9ca3af", font=("Segoe UI", 10)).grid(row=0, column=0, sticky="w", pady=4)
login_email = ttk.Entry(lf_box, width=32)
login_email.grid(row=1, column=0, pady=(0, 12))

tk.Label(lf_box, text="Password", bg="#111827", fg="#9ca3af", font=("Segoe UI", 10)).grid(row=2, column=0, sticky="w", pady=4)
login_pass = ttk.Entry(lf_box, width=32, show="*")
login_pass.grid(row=3, column=0, pady=(0, 8))

login_status = tk.Label(lf_box, text="", bg="#111827", fg="#f87171", font=("Segoe UI", 10))
login_status.grid(row=4, column=0, pady=4)

def do_login():
    email = login_email.get().strip()
    pwd   = login_pass.get()
    if not email or not pwd:
        login_status.config(text="Please fill in all fields.")
        return
    try:
        res = supabase.table("users").select("*").eq("email", email).execute()
    except Exception as e:
        login_status.config(text=f"Connection error: {e}")
        return
    if not res.data:
        login_status.config(text="No account found with that email.")
        return
    user = res.data[0]
    stored = user["password_hash"]
    if stored.startswith("$2b$") or stored.startswith("$2a$"):
        ok = bcrypt.checkpw(pwd.encode(), stored.encode())
    elif ":" in stored:
        import hashlib
        salt, h = stored.split(":", 1)
        ok = hashlib.pbkdf2_hmac("sha256", pwd.encode(), salt.encode(), 100_000).hex() == h
    else:
        ok = (pwd == stored)
    if ok:
        login_status.config(text="")
        login_email.delete(0, "end")
        login_pass.delete(0, "end")
        show_frame("home")
    else:
        login_status.config(text="Incorrect password.")

tk.Button(lf_box, text="Login", command=do_login, bg="#3b82f6", fg="white",
          font=("Segoe UI", 11, "bold"), relief="flat", padx=12, pady=7, cursor="hand2",
          width=28).grid(row=5, column=0, pady=8)

tk.Button(lf_box, text="Create Account", command=lambda: show_frame("register"),
          bg="#374151", fg="#d1d5db", font=("Segoe UI", 10), relief="flat",
          padx=12, pady=5, cursor="hand2", width=28).grid(row=6, column=0)


register_frame = make_frame("register")

ttk.Label(register_frame, text="Create Account", style="Header.TLabel").pack(pady=(60, 4))
ttk.Label(register_frame, text="Fill in your details below", style="TLabel").pack(pady=(0, 24))

rf_box = tk.Frame(register_frame, bg="#111827", padx=30, pady=30)
rf_box.pack()

for i, (lbl_text, _) in enumerate([("Full Name",""),("Email",""),("Password","*")]):
    tk.Label(rf_box, text=lbl_text, bg="#111827", fg="#9ca3af", font=("Segoe UI", 10)
             ).grid(row=i*2, column=0, sticky="w", pady=4)

reg_name  = ttk.Entry(rf_box, width=32); reg_name.grid(row=1, column=0, pady=(0,10))
reg_email = ttk.Entry(rf_box, width=32); reg_email.grid(row=3, column=0, pady=(0,10))
reg_pass  = ttk.Entry(rf_box, width=32, show="*"); reg_pass.grid(row=5, column=0, pady=(0,8))

reg_status = tk.Label(rf_box, text="", bg="#111827", fg="#f87171", font=("Segoe UI", 10))
reg_status.grid(row=6, column=0, pady=4)

def do_register():
    name  = reg_name.get().strip()
    email = reg_email.get().strip()
    pwd   = reg_pass.get()
    if not name or not email or not pwd:
        reg_status.config(text="Please fill in all fields.")
        return
    exists = supabase.table("users").select("user_id").eq("email", email).execute()
    if exists.data:
        reg_status.config(text="An account with this email already exists.")
        return
    hashed = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()
    try:
        supabase.table("users").insert({
            "full_name": name, "email": email, "password_hash": hashed
        }).execute()
    except Exception as e:
        reg_status.config(text=f"Error: {e}")
        return
    messagebox.showinfo("Success", "Account created! Please log in.")
    reg_name.delete(0, "end"); reg_email.delete(0, "end"); reg_pass.delete(0, "end")
    reg_status.config(text="")
    show_frame("login")

tk.Button(rf_box, text="Create Account", command=do_register, bg="#10b981", fg="white",
          font=("Segoe UI", 11, "bold"), relief="flat", padx=12, pady=7, cursor="hand2",
          width=28).grid(row=7, column=0, pady=8)

tk.Button(rf_box, text="Back to Login", command=lambda: show_frame("login"),
          bg="#374151", fg="#d1d5db", font=("Segoe UI", 10), relief="flat",
          padx=12, pady=5, cursor="hand2", width=28).grid(row=8, column=0)


home_frame = make_frame("home")

ttk.Label(home_frame, text="Dashboard", style="Header.TLabel").pack(pady=(40, 6))
ttk.Label(home_frame, text="Select a section to manage", style="TLabel").pack(pady=(0, 24))

nav_grid = tk.Frame(home_frame, bg="#1f2937")
nav_grid.pack()

for col, (label, frame_name) in enumerate([
    ("Farmers",     "farmers"),
    ("Fields",      "fields"),
    ("Crops",       "crops"),
    ("Sensors",     "sensors"),
    ("Sensor Data", "sensor_data"),
    ("Irrigation",  "irrigation"),
    ("Queries",     "queries"),       
]):
    tk.Button(nav_grid, text=label, command=lambda fn=frame_name: show_frame(fn),
              bg="#111827", fg="#f3f4f6", font=("Segoe UI", 12, "bold"),
              relief="flat", width=14, height=4, cursor="hand2",
              activebackground="#1d4ed8", activeforeground="white"
              ).grid(row=0, column=col, padx=8, pady=8)

tk.Button(home_frame, text="Logout", command=lambda: show_frame("login"),
          bg="#f97316", fg="white", font=("Segoe UI", 10, "bold"),
          relief="flat", padx=14, pady=6, cursor="hand2").pack(pady=20)


def build_crud_frame(frame_name, title, table, pk, columns, field_builders):
    frm = make_frame(frame_name, bg="#1f2937")

    top = tk.Frame(frm, bg="#111827", pady=6)
    top.pack(fill="x")
    tk.Label(top, text=title, bg="#111827", fg="#f3f4f6",
             font=("Segoe UI", 15, "bold")).pack(side="left", padx=14)
    tk.Button(top, text="<< Dashboard", command=lambda: show_frame("home"),
              bg="#374151", fg="#d1d5db", relief="flat", font=("Segoe UI", 10),
              padx=10, pady=4, cursor="hand2").pack(side="right", padx=14)

    col_names = [c[0] for c in columns]
    tree = make_tree(frm, col_names, heights=10)

    inp = tk.Frame(frm, bg="#111827", padx=14, pady=10)
    inp.pack(fill="x")

    widgets = {}
    for i, build in enumerate(field_builders):
        field_key, widget = build(inp, i)
        widgets[field_key] = widget

    selected_id = tk.StringVar()

    btn_row = tk.Frame(inp, bg="#111827")
    btn_row.grid(row=len(field_builders) + 1, column=0, columnspan=6, sticky="w", pady=6)

    def clear_inputs():
        for w in widgets.values():
            if isinstance(w, ttk.Entry):
                w.delete(0, "end")
            elif isinstance(w, ttk.Combobox):
                w.set("")
        selected_id.set("")
        tree.selection_remove(tree.selection())

    def load():
        tree.delete(*tree.get_children())
        data = supabase.table(table).select("*").execute().data or []
        for row in data:
            tree.insert("", "end", iid=str(row[pk]),
                        values=[row.get(c[1], "") for c in columns])

    def on_select(event):
        sel = tree.focus()
        if not sel:
            return
        vals = tree.item(sel)["values"]
        selected_id.set(str(vals[0]))
        for i, (_, field) in enumerate(columns[1:], start=1):
            w = widgets.get(field)
            if w is None:
                continue
            if isinstance(w, ttk.Combobox):
                w.set(str(vals[i]))
            elif isinstance(w, ttk.Entry):
                w.delete(0, "end")
                w.insert(0, str(vals[i]))

    tree.bind("<<TreeviewSelect>>", on_select)

    def do_add():
        payload = {field: w.get() for field, w in widgets.items() if w.get()}
        if not payload:
            return
        supabase.table(table).insert(payload).execute()
        load(); clear_inputs()
        messagebox.showinfo("Success", f"{title[:-1] if title.endswith('s') else title} added.")

    def do_update():
        rid = selected_id.get()
        if not rid:
            messagebox.showwarning("Select a row", "Click a row to select it first.")
            return
        payload = {field: w.get() for field, w in widgets.items() if w.get()}
        supabase.table(table).update(payload).eq(pk, rid).execute()
        load(); clear_inputs()
        messagebox.showinfo("Success", "Record updated.")

    def do_delete():
        rid = selected_id.get()
        if not rid:
            messagebox.showwarning("Select a row", "Click a row to select it first.")
            return
        if messagebox.askyesno("Confirm", "Delete this record?"):
            supabase.table(table).delete().eq(pk, rid).execute()
            load(); clear_inputs()

    for col_i, (btn_text, cmd, color) in enumerate([
        ("Add",     do_add,    "#3b82f6"),
        ("Update",  do_update, "#f59e0b"),
        ("Delete",  do_delete, "#ef4444"),
        ("Refresh", lambda: (load(), clear_inputs()), "#6b7280"),
    ]):
        tk.Button(btn_row, text=btn_text, command=cmd, bg=color, fg="white",
                  font=("Segoe UI", 10, "bold"), relief="flat", padx=12, pady=5,
                  cursor="hand2").grid(row=0, column=col_i, padx=4)

    load()
    return frm


def text_field(label, db_field, row_i, col_a=0, col_b=1):
    def build(parent, _i):
        lbl(parent, label, row_i, col_a)
        e = ttk.Entry(parent, width=22)
        e.grid(row=row_i, column=col_b, padx=6, pady=4, sticky="ew")
        return db_field, e
    return build

def num_field(label, db_field, row_i, col_a=0, col_b=1):
    return text_field(label, db_field, row_i, col_a, col_b)

def fk_combo_field(label, db_field, fk_table, fk_id, fk_label, row_i, col_a=2, col_b=3):
    def build(parent, _i):
        lbl(parent, label, row_i, col_a)
        options = supabase.table(fk_table).select(f"{fk_id},{fk_label}").execute().data or []
        display = [f"{o[fk_id]} - {o[fk_label]}" for o in options]
        c = ttk.Combobox(parent, values=display, width=22, state="readonly")
        c.grid(row=row_i, column=col_b, padx=6, pady=4, sticky="ew")
        orig_get = c.get
        def patched_get():
            val = orig_get()
            return val.split(" - ")[0] if val else ""
        c.get = patched_get
        return db_field, c
    return build


build_crud_frame(
    "farmers", "Farmers", "users", "user_id",
    columns=[
        ("ID",         "user_id"),
        ("Full Name",  "full_name"),
        ("Email",      "email"),
        ("Role",       "role"),
        ("Created At", "created_at"),
    ],
    field_builders=[
        text_field("Full Name", "full_name", 0, 0, 1),
        text_field("Email",     "email",     1, 0, 1),
        text_field("Role",      "role",      0, 2, 3),
    ]
)


build_crud_frame(
    "fields", "Fields", "fields", "field_id",
    columns=[
        ("ID",         "field_id"),
        ("Field Name", "field_name"),
        ("Location",   "location"),
        ("Area (ha)",  "size_hectares"),
        ("Soil Type",  "soil_type"),
        ("Crop ID",    "crop_id"),
        ("Farmer ID",  "farmer_id"),
    ],
    field_builders=[
        text_field("Field Name", "field_name",    0, 0, 1),
        text_field("Location",   "location",      1, 0, 1),
        num_field("Area (ha)",   "size_hectares", 0, 2, 3),
        text_field("Soil Type",  "soil_type",     1, 2, 3),
        fk_combo_field("Crop",   "crop_id",   "crops", "crop_id", "crop_name", 2, 0, 1),
        fk_combo_field("Farmer", "farmer_id", "users", "user_id", "full_name", 2, 2, 3),
    ]
)


build_crud_frame(
    "crops", "Crops", "crops", "crop_id",
    columns=[
        ("ID",          "crop_id"),
        ("Crop Name",   "crop_name"),
        ("Season",      "growing_season"),
        ("Yield kg/ha", "expected_yield_kg_per_hectare"),
        ("Min Moist.",  "min_moisture"),
        ("Max Moist.",  "max_moisture"),
        ("Field ID",    "field_id"),
        ("Farmer ID",   "farmer_id"),
    ],
    field_builders=[
        text_field("Crop Name",    "crop_name",                     0, 0, 1),
        text_field("Season",       "growing_season",                1, 0, 1),
        num_field("Yield (kg/ha)", "expected_yield_kg_per_hectare", 0, 2, 3),
        num_field("Min Moisture",  "min_moisture",                  1, 2, 3),
        num_field("Max Moisture",  "max_moisture",                  2, 2, 3),
        fk_combo_field("Field",    "field_id",  "fields", "field_id", "field_name", 3, 0, 1),
        fk_combo_field("Farmer",   "farmer_id", "users",  "user_id",  "full_name",  3, 2, 3),
    ]
)


build_crud_frame(
    "sensors", "Sensors", "sensors", "sensor_id",
    columns=[
        ("ID",           "sensor_id"),
        ("Type",         "sensor_type"),
        ("Status",       "status"),
        ("Install Date", "install_date"),
        ("Field ID",     "field_id"),
    ],
    field_builders=[
        text_field("Sensor Type",  "sensor_type",  0, 0, 1),
        text_field("Status",       "status",       1, 0, 1),
        num_field("Install Date",  "install_date", 0, 2, 3),
        fk_combo_field("Field",    "field_id", "fields", "field_id", "field_name", 1, 2, 3),
    ]
)


build_crud_frame(
    "sensor_data", "Sensor Data", "sensor_data", "data_id",
    columns=[
        ("Data_id",   "data_id"),
        
        ("Moisture",    "moisture"),
        ("Temperature", "temperature"),
        ("Humidity",    "humidity"),
        ("Recorded At", "recorded_at"),
    ],
    field_builders=[
        fk_combo_field("Sensor",     "sensor_id",   "sensors", "sensor_id", "sensor_type", 0, 0, 1),
        num_field("Moisture",        "moisture",    1, 0, 1),
        num_field("Temperature",     "temperature", 0, 2, 3),
        num_field("Humidity",        "humidity",    1, 2, 3),
        text_field("Recorded At",    "recorded_at", 2, 0, 1),
    ]
)


build_crud_frame(
    "irrigation", "Irrigation Logs", "irrigation_logs", "log_id",
    columns=[
        ("ID",           "log_id"),
        ("Water (L)",    "water_amount_litres"),
        ("Irrigated At", "irrigated_at"),
        ("Triggered By", "triggered_by"),
        ("Field ID",     "field_id"),
    ],
    field_builders=[
        num_field("Water (L)",     "water_amount_litres", 0, 0, 1),
        text_field("Irrigated At", "irrigated_at",        1, 0, 1),
        text_field("Triggered By", "triggered_by",        0, 2, 3),
        fk_combo_field("Field",    "field_id", "fields", "field_id", "field_name", 1, 2, 3),
    ]
)


queries_frame = make_frame("queries")

q_top = tk.Frame(queries_frame, bg="#111827", pady=6)
q_top.pack(fill="x")
tk.Label(q_top, text="Queries", bg="#111827", fg="#f3f4f6",
         font=("Segoe UI", 15, "bold")).pack(side="left", padx=14)
tk.Button(q_top, text="<< Dashboard", command=lambda: show_frame("home"),
          bg="#374151", fg="#d1d5db", relief="flat", font=("Segoe UI", 10),
          padx=10, pady=4, cursor="hand2").pack(side="right", padx=14)

preset_bar = tk.Frame(queries_frame, bg="#1f2937")
preset_bar.pack(fill="x", padx=10, pady=(8, 4))
tk.Label(preset_bar, text="Presets:", bg="#1f2937", fg="#9ca3af",
         font=("Segoe UI", 10)).pack(side="left", padx=(0, 6))

q_status = tk.Label(queries_frame, text="", bg="#1f2937", fg="#f87171", font=("Segoe UI", 9))
q_status.pack(anchor="w", padx=14)

result_container = tk.Frame(queries_frame, bg="#111827")
result_container.pack(fill="both", expand=True, padx=10, pady=4)

PRESET_QUERIES = {
    "All Farmers": lambda: (
        ["ID", "Full Name", "Email", "Role", "Created At"],
        [[r["user_id"], r["full_name"], r["email"], r["role"], r.get("created_at", "")]
         for r in (supabase.table("users").select("user_id,full_name,email,role,created_at").execute().data or [])]
    ),
    "Fields + Farmer": lambda: (
        ["Field ID", "Field Name", "Location", "Area (ha)", "Soil Type", "Farmer"],
        [[r["field_id"], r["field_name"], r["location"], r["size_hectares"], r["soil_type"],
          r["users"]["full_name"] if r.get("users") else ""]
         for r in (supabase.table("fields").select("field_id,field_name,location,size_hectares,soil_type,users(full_name)").execute().data or [])]
    ),
    "Fields + Crop": lambda: (
        ["Field ID", "Field Name", "Crop", "Season"],
        [[r["field_id"], r["field_name"],
          r["crops"]["crop_name"] if r.get("crops") else "",
          r["crops"]["growing_season"] if r.get("crops") else ""]
         for r in (supabase.table("fields").select("field_id,field_name,crops(crop_name,growing_season)").execute().data or [])]
    ),
    "Sensor Readings": lambda: (
        ["ID", "Sensor Type", "Moisture", "Temperature", "Humidity", "Recorded At"],
        [[r["data_id"],
          r["sensors"]["sensor_type"] if r.get("sensors") else "",
          r["moisture"], r["temperature"], r["humidity"], r["recorded_at"]]
         for r in (supabase.table("sensor_data").select("data_id,moisture,temperature,humidity,recorded_at,sensors(sensor_type)").order("data_id", desc=True).limit(50).execute().data or [])]
    ),
    "Irrigation + Field": lambda: (
        ["Log ID", "Field", "Water (L)", "Irrigated At", "Triggered By"],
        [[r["log_id"],
          r["fields"]["field_name"] if r.get("fields") else "",
          r["water_amount_litres"], r["irrigated_at"], r["triggered_by"]]
         for r in (supabase.table("irrigation_logs").select("log_id,water_amount_litres,irrigated_at,triggered_by,fields(field_name)").execute().data or [])]
    ),
    "Active Sensors": lambda: (
        ["ID", "Type", "Status", "Install Date", "Field"],
        [[r["sensor_id"], r["sensor_type"], r["status"], r["install_date"],
          r["fields"]["field_name"] if r.get("fields") else ""]
         for r in (supabase.table("sensors").select("sensor_id,sensor_type,status,install_date,fields(field_name)").eq("status", "active").execute().data or [])]
    ),
}

def run_query(fn):
    q_status.config(text="Loading...")
    queries_frame.update_idletasks()
    for w in result_container.winfo_children():
        w.destroy()
    try:
        cols, rows = fn()
    except Exception as e:
        q_status.config(text=f"Error: {e}"); return
    tree = ttk.Treeview(result_container, columns=cols, show="headings", height=14)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=130, anchor="w")
    vsb = ttk.Scrollbar(result_container, orient="vertical",   command=tree.yview)
    hsb = ttk.Scrollbar(result_container, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    hsb.pack(side="bottom", fill="x")
    tree.pack(side="left", fill="both", expand=True)
    vsb.pack(side="left", fill="y")
    for row in rows:
        tree.insert("", "end", values=row)
    q_status.config(text=f"{len(rows)} row(s) returned.")

for label, fn in PRESET_QUERIES.items():
    tk.Button(preset_bar, text=label, command=lambda f=fn: run_query(f),
              bg="#1e3a5f", fg="#93c5fd", relief="flat",
              font=("Segoe UI", 9), padx=8, pady=4,
              cursor="hand2").pack(side="left", padx=3)


show_frame("login")
root.mainloop()