import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.font import Font
import sqlite3
import json
import csv
from datetime import datetime
from pathlib import Path
import os


class DatabaseManager:
    def __init__(self, db_path="vat_calculator.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                created_at TEXT,
                vat_rate REAL,
                data TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_calculation(self, name, vat_rate, data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO calculations (name, created_at, vat_rate, data)
            VALUES (?, ?, ?, ?)
        ''', (name, datetime.now().isoformat(), vat_rate, json.dumps(data)))
        conn.commit()
        conn.close()
        return cursor.lastrowid
    
    def get_all_calculations(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, created_at, vat_rate FROM calculations ORDER BY id DESC
        ''')
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_calculation(self, calc_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT vat_rate, data FROM calculations WHERE id = ?', (calc_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def delete_calculation(self, calc_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM calculations WHERE id = ?', (calc_id,))
        conn.commit()
        conn.close()
    
    def backup_db(self, backup_path):
        conn = sqlite3.connect(self.db_path)
        with open(backup_path, 'w') as f:
            for line in conn.iterdump():
                f.write(f'{line}\n')
        conn.close()
    
    def restore_db(self, backup_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS calculations')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS calculations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                created_at TEXT,
                vat_rate REAL,
                data TEXT
            )
        ''')
        with open(backup_path, 'r') as f:
            cursor.executescript(f.read())
        conn.commit()
        conn.close()


class ReportGenerator:
    @staticmethod
    def generate_csv(data, vat_rate, totals, filepath):
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['VAT Calculator Report'])
            writer.writerow([f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"])
            writer.writerow([f'VAT Rate: {vat_rate}%'])
            writer.writerow([])
            writer.writerow(['Item', 'Price Inc. VAT', 'Price Excl. VAT', 'VAT Amount'])
            for row in data:
                if row['item'] or row['price_inc']:
                    writer.writerow([
                        row['item'],
                        row['price_inc'] if row['price_inc'] else '',
                        row['price_excl'] if row['price_excl'] else '',
                        row['vat_amt'] if row['vat_amt'] else ''
                    ])
            writer.writerow([])
            writer.writerow(['TOTAL', totals['inc'], totals['excl'], totals['vat']])
    
    @staticmethod
    def generate_html_report(data, vat_rate, totals, filepath):
        html = f'''
<!DOCTYPE html>
<html>
<head>
    <title>VAT Calculator Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #003366; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
        th {{ background-color: #003366; color: white; padding: 10px; text-align: left; }}
        td {{ border: 1px solid #ddd; padding: 8px; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .totals {{ background-color: #003366; color: white; font-weight: bold; }}
        .summary {{ margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; }}
    </style>
</head>
<body>
    <h1>VAT Calculator Report</h1>
    <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    <p><strong>VAT Rate:</strong> {vat_rate}%</p>
    
    <table>
        <tr>
            <th>Item</th>
            <th>Price Inc. VAT</th>
            <th>Price Excl. VAT</th>
            <th>VAT Amount</th>
        </tr>
'''
        for row in data:
            if row['item'] or row['price_inc']:
                html += f'''
        <tr>
            <td>{row['item']}</td>
            <td>£{row['price_inc'] if row['price_inc'] else '-'}</td>
            <td>£{row['price_excl'] if row['price_excl'] else '-'}</td>
            <td>£{row['vat_amt'] if row['vat_amt'] else '-'}</td>
        </tr>
'''
        html += f'''
        <tr class="totals">
            <td>TOTAL</td>
            <td>£{totals['inc']}</td>
            <td>£{totals['excl']}</td>
            <td>£{totals['vat']}</td>
        </tr>
    </table>
    
    <div class="summary">
        <h3>Summary</h3>
        <p>Total Items: {len([r for r in data if r['item']])}</p>
        <p>Total Incl. VAT: £{totals['inc']}</p>
        <p>Total Excl. VAT: £{totals['excl']}</p>
        <p>Total VAT: £{totals['vat']}</p>
    </div>
</body>
</html>
'''
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)


class VATCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VAT Calculator Pro")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        self.db = DatabaseManager()
        self.rows_data = []
        self.columns = ["Item", "Price Inc. VAT", "Price Excl. VAT", "VAT Amt"]
        self.current_vat_rate = tk.StringVar(value="20")
        
        self.setup_styles()
        self.create_widgets()
        self.load_saved_calculations()
        
    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
    def create_widgets(self):
        # Menu Bar
        self.create_menu()
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Top control panel
        self.create_control_panel(main_container)
        
        # Tab control
        self.tab_control = ttk.Notebook(main_container)
        
        # Calculator tab
        self.calc_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.calc_tab, text='Calculator')
        
        # History tab
        self.history_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.history_tab, text='Saved Calculations')
        
        self.tab_control.pack(fill='both', expand=True, pady=10)
        
        # Create calculator interface
        self.create_calculator_interface(self.calc_tab)
        self.create_history_interface(self.history_tab)
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Calculation", command=self.new_calculation)
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV", command=self.export_csv)
        file_menu.add_command(label="Export to HTML Report", command=self.export_html)
        file_menu.add_separator()
        file_menu.add_command(label="Backup Database", command=self.backup_db)
        file_menu.add_command(label="Restore Database", command=self.restore_db)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Add Row", command=self.add_row)
        edit_menu.add_command(label="Remove Row", command=self.remove_row)
        edit_menu.add_command(label="Clear All", command=self.clear_all)
        
    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Settings", padding="10")
        control_frame.pack(fill='x', pady=(0, 10))
        
        # VAT Rate
        ttk.Label(control_frame, text="VAT Rate (%):").grid(row=0, column=0, padx=(0, 5))
        vat_entry = ttk.Entry(control_frame, textvariable=self.current_vat_rate, width=8)
        vat_entry.grid(row=0, column=1, padx=(0, 10))
        vat_entry.bind('<KeyRelease>', lambda e: self.recalculate_all())
        
        # Save controls
        ttk.Label(control_frame, text="Name:").grid(row=0, column=2, padx=(20, 5))
        self.calc_name_var = tk.StringVar()
        name_entry = ttk.Entry(control_frame, textvariable=self.calc_name_var, width=20)
        name_entry.grid(row=0, column=3, padx=(0, 5))
        
        save_btn = ttk.Button(control_frame, text="Save Calculation", command=self.save_calculation)
        save_btn.grid(row=0, column=4, padx=5)
        
        clear_btn = ttk.Button(control_frame, text="Clear", command=self.clear_all)
        clear_btn.grid(row=0, column=5, padx=5)
        
        # Row/Column controls
        ttk.Button(control_frame, text="+ Row", command=self.add_row).grid(row=0, column=6, padx=(20, 5))
        ttk.Button(control_frame, text="- Row", command=self.remove_row).grid(row=0, column=7, padx=5)
    
    def create_calculator_interface(self, parent):
        # Canvas with scrollbars
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg='#f0f0f0')
        
        v_scroll = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scroll = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        v_scroll.pack(side='right', fill='y')
        h_scroll.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        self.table_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.table_frame, anchor='nw')
        
        self.table_frame.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))
        
        # Create table
        self.create_table()
        
        # Mouse wheel binding
        self.canvas.bind_all('<MouseWheel>', self.on_mousewheel)
    
    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), 'units')
    
    def create_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()
        
        self.row_widgets = []
        self.entries = {}
        
        # Header
        header_bg = '#003366'
        header_fg = 'white'
        
        for col, header in enumerate(self.columns):
            label = tk.Label(self.table_frame, text=header, font=('Arial', 10, 'bold'),
                           bg=header_bg, fg=header_fg, width=18, height=2)
            label.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        # Currency labels
        for row_idx in range(1, len(self.rows_data) + 1):
            for col in range(1, 4):
                tk.Label(self.table_frame, text="£", bg='#f0f0f0', fg='gray').grid(
                    row=row_idx, column=col, sticky='e', padx=(5, 0))
        
        # Add row button
        add_btn = tk.Button(self.table_frame, text="+ Add Row", command=self.add_row,
                           bg='#4CAF50', fg='white', font=('Arial', 9))
        add_btn.grid(row=len(self.rows_data) + 1, column=0, sticky='nsew', padx=1, pady=5)
        
        # Data rows
        self.create_data_rows()
        
        # Totals section
        self.create_totals_section(len(self.rows_data) + 2)
    
    def create_data_rows(self):
        for i, row_data in enumerate(self.rows_data):
            row_idx = i + 1
            widgets = {}
            
            # Item name
            item_var = tk.StringVar(value=row_data.get('item', ''))
            item_entry = ttk.Entry(self.table_frame, textvariable=item_var, width=20)
            item_entry.grid(row=row_idx, column=0, sticky='nsew', padx=1, pady=1, ipady=3)
            widgets['item'] = item_var
            
            # Price Inc. VAT
            price_inc_var = tk.StringVar(value=row_data.get('price_inc', ''))
            price_inc_entry = ttk.Entry(self.table_frame, textvariable=price_inc_var, width=16)
            price_inc_entry.grid(row=row_idx, column=1, sticky='nsew', padx=1, pady=1, ipady=3)
            price_inc_entry.bind('<KeyRelease>', lambda e, row=i: self.calculate_row(row))
            widgets['price_inc'] = price_inc_var
            
            # Price Excl. VAT (calculated)
            price_excl_var = tk.StringVar(value=row_data.get('price_excl', '-'))
            price_excl_label = ttk.Label(self.table_frame, textvariable=price_excl_var, 
                                        width=16, anchor='e', background='#f0f0f0')
            price_excl_label.grid(row=row_idx, column=2, sticky='nsew', padx=1, pady=1)
            widgets['price_excl'] = price_excl_var
            
            # VAT Amount (calculated)
            vat_amt_var = tk.StringVar(value=row_data.get('vat_amt', '-'))
            vat_amt_label = ttk.Label(self.table_frame, textvariable=vat_amt_var, 
                                     width=16, anchor='e', background='#f0f0f0')
            vat_amt_label.grid(row=row_idx, column=3, sticky='nsew', padx=1, pady=1)
            widgets['vat_amt'] = vat_amt_var
            
            self.entries[i] = widgets
    
    def create_totals_section(self, start_row):
        # Separator
        ttk.Separator(self.table_frame, orient='horizontal').grid(
            row=start_row, column=0, columnspan=4, sticky='ew', pady=10)
        
        # Total labels
        header_bg = '#003366'
        tk.Label(self.table_frame, text="TOTAL", font=('Arial', 11, 'bold'),
                bg=header_bg, fg='white').grid(
            row=start_row + 1, column=0, sticky='nsew', padx=1, pady=5)
        
        # Total Inc. VAT
        self.total_inc_var = tk.StringVar(value="0.00")
        tk.Label(self.table_frame, text="£", font=('Arial', 11, 'bold'),
                bg='#f0f0f0').grid(row=start_row + 1, column=1, sticky='e', padx=(5, 0))
        tk.Label(self.table_frame, textvariable=self.total_inc_var, font=('Arial', 11, 'bold'),
                width=14, anchor='e', background='#f0f0f0').grid(
            row=start_row + 1, column=1, sticky='e', padx=(25, 5))
        
        # Total Excl. VAT
        self.total_excl_var = tk.StringVar(value="0.00")
        tk.Label(self.table_frame, text="£", font=('Arial', 11, 'bold'),
                bg='#f0f0f0').grid(row=start_row + 1, column=2, sticky='e', padx=(5, 0))
        tk.Label(self.table_frame, textvariable=self.total_excl_var, font=('Arial', 11, 'bold'),
                width=14, anchor='e', background='#f0f0f0').grid(
            row=start_row + 1, column=2, sticky='e', padx=(25, 5))
        
        # Total VAT
        self.total_vat_var = tk.StringVar(value="0.00")
        tk.Label(self.table_frame, text="£", font=('Arial', 11, 'bold'),
                bg='#f0f0f0').grid(row=start_row + 1, column=3, sticky='e', padx=(5, 0))
        tk.Label(self.table_frame, textvariable=self.total_vat_var, font=('Arial', 11, 'bold'),
                width=14, anchor='e', background='#f0f0f0').grid(
            row=start_row + 1, column=3, sticky='e', padx=(25, 5))
        
        self.calculate_totals()
    
    def add_row(self):
        self.rows_data.append({'item': '', 'price_inc': '', 'price_excl': '-', 'vat_amt': '-'})
        self.create_table()
    
    def remove_row(self):
        if len(self.rows_data) > 1:
            self.rows_data.pop()
            self.create_table()
    
    def get_vat_rate(self):
        try:
            return float(self.current_vat_rate.get()) / 100
        except ValueError:
            return 0.20
    
    def calculate_row(self, row_idx):
        if row_idx not in self.entries:
            return
        
        widgets = self.entries[row_idx]
        vat_rate = self.get_vat_rate()
        
        try:
            price_inc_text = widgets['price_inc'].get().strip()
            if not price_inc_text:
                widgets['price_excl'].set("-")
                widgets['vat_amt'].set("-")
                self.rows_data[row_idx]['price_excl'] = "-"
                self.rows_data[row_idx]['vat_amt'] = "-"
            else:
                price_inc_text = price_inc_text.replace('£', '').replace(',', '').replace('$', '')
                price_inc = float(price_inc_text)
                
                price_excl = price_inc / (1 + vat_rate)
                vat_amt = price_inc - price_excl
                
                price_excl_str = f"{price_excl:,.2f}"
                vat_amt_str = f"{vat_amt:,.2f}"
                
                widgets['price_excl'].set(price_excl_str)
                widgets['vat_amt'].set(vat_amt_str)
                
                self.rows_data[row_idx]['price_excl'] = price_excl_str
                self.rows_data[row_idx]['vat_amt'] = vat_amt_str
        except ValueError:
            widgets['price_excl'].set("-")
            widgets['vat_amt'].set("-")
            self.rows_data[row_idx]['price_excl'] = "-"
            self.rows_data[row_idx]['vat_amt'] = "-"
        
        self.update_rows_data()
        self.calculate_totals()
    
    def update_rows_data(self):
        for i, widgets in self.entries.items():
            self.rows_data[i]['item'] = widgets['item'].get()
            self.rows_data[i]['price_inc'] = widgets['price_inc'].get()
    
    def recalculate_all(self):
        for i in range(len(self.entries)):
            self.calculate_row(i)
    
    def calculate_totals(self):
        total_inc = 0
        total_excl = 0
        total_vat = 0
        
        for widgets in self.entries.values():
            try:
                price_inc_text = widgets['price_inc'].get().strip()
                if price_inc_text:
                    price_inc_text = price_inc_text.replace('£', '').replace(',', '')
                    total_inc += float(price_inc_text)
            except ValueError:
                pass
            
            try:
                price_excl_text = widgets['price_excl'].get().strip()
                if price_excl_text and price_excl_text != '-':
                    price_excl_text = price_excl_text.replace('£', '').replace(',', '')
                    total_excl += float(price_excl_text)
            except ValueError:
                pass
            
            try:
                vat_text = widgets['vat_amt'].get().strip()
                if vat_text and vat_text != '-':
                    vat_text = vat_text.replace('£', '').replace(',', '')
                    total_vat += float(vat_text)
            except ValueError:
                pass
        
        self.total_inc_var.set(f"{total_inc:,.2f}")
        self.total_excl_var.set(f"{total_excl:,.2f}")
        self.total_vat_var.set(f"{total_vat:,.2f}")
    
    def get_current_data(self):
        return {
            'vat_rate': self.current_vat_rate.get(),
            'rows': self.rows_data,
            'totals': {
                'inc': self.total_inc_var.get(),
                'excl': self.total_excl_var.get(),
                'vat': self.total_vat_var.get()
            }
        }
    
    def save_calculation(self):
        name = self.calc_name_var.get().strip()
        if not name:
            messagebox.showwarning("Warning", "Please enter a name for this calculation")
            return
        
        self.update_rows_data()
        calc_id = self.db.save_calculation(
            name,
            self.current_vat_rate.get(),
            self.rows_data
        )
        messagebox.showinfo("Success", f"Calculation saved as '{name}' (ID: {calc_id})")
        self.load_saved_calculations()
    
    def load_saved_calculations(self):
        self.calculations = self.db.get_all_calculations()
        self.update_history_list()
    
    def create_history_interface(self, parent):
        # Listbox with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical')
        self.history_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, 
                                       font=('Arial', 10), height=15)
        scrollbar.config(command=self.history_list.yview)
        
        scrollbar.pack(side='right', fill='y')
        self.history_list.pack(side='left', fill='both', expand=True)
        
        self.history_list.bind('<Double-1>', self.load_calculation)
        
        # Buttons frame
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(btn_frame, text="Load Selected", command=self.load_selected).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Generate Report", command=self.generate_report_for_selected).pack(side='left', padx=5)
    
    def update_history_list(self):
        self.history_list.delete(0, 'end')
        for calc_id, name, created_at, vat_rate in self.calculations:
            date_str = created_at[:10]
            self.history_list.insert('end', f"[{calc_id}] {name} - {date_str} (VAT: {vat_rate}%)")
    
    def load_selected(self):
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a calculation to load")
            return
        
        idx = selection[0]
        calc_id = self.calculations[idx][0]
        self.load_calculation_by_id(calc_id)
    
    def load_calculation_by_id(self, calc_id):
        result = self.db.get_calculation(calc_id)
        if result:
            vat_rate, data = result
            self.current_vat_rate.set(str(vat_rate))
            self.rows_data = json.loads(data)
            self.calc_name_var.set(self.calculations[[c[0] for c in self.calculations].index(calc_id)][1])
            self.create_table()
            self.tab_control.select(0)
    
    def load_calculation(self, event):
        self.load_selected()
    
    def delete_selected(self):
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a calculation to delete")
            return
        
        idx = selection[0]
        calc_id = self.calculations[idx][1]
        
        if messagebox.askyesno("Confirm", f"Delete '{calc_id}'?"):
            self.db.delete_calculation(self.calculations[idx][0])
            self.load_saved_calculations()
            messagebox.showinfo("Success", "Calculation deleted")
    
    def new_calculation(self):
        self.current_vat_rate.set("20")
        self.calc_name_var.set("")
        self.rows_data = [{'item': '', 'price_inc': '', 'price_excl': '-', 'vat_amt': '-'}]
        self.create_table()
    
    def clear_all(self):
        self.rows_data = [{'item': '', 'price_inc': '', 'price_excl': '-', 'vat_amt': '-'}]
        self.calc_name_var.set("")
        self.create_table()
    
    def export_csv(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.csv',
                                               filetypes=[("CSV files", "*.csv")])
        if filepath:
            self.update_rows_data()
            data = self.get_current_data()
            ReportGenerator.generate_csv(
                self.rows_data,
                self.current_vat_rate.get(),
                data['totals'],
                filepath
            )
            messagebox.showinfo("Success", f"Report saved to {filepath}")
    
    def export_html(self):
        filepath = filedialog.asksaveasfilename(defaultextension='.html',
                                               filetypes=[("HTML files", "*.html")])
        if filepath:
            self.update_rows_data()
            data = self.get_current_data()
            ReportGenerator.generate_html_report(
                self.rows_data,
                self.current_vat_rate.get(),
                data['totals'],
                filepath
            )
            messagebox.showinfo("Success", f"Report saved to {filepath}")
    
    def generate_report_for_selected(self):
        selection = self.history_list.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a calculation")
            return
        
        idx = selection[0]
        calc_id = self.calculations[idx][0]
        name = self.calculations[idx][1]
        
        result = self.db.get_calculation(calc_id)
        if result:
            vat_rate, data = result
            rows_data = json.loads(data)
            
            # Calculate totals
            total_inc = sum(float(r['price_inc'].replace(',', '')) for r in rows_data if r.get('price_inc'))
            total_excl = sum(float(r['price_excl'].replace(',', '')) if r.get('price_excl') != '-' else 0 for r in rows_data)
            total_vat = sum(float(r['vat_amt'].replace(',', '')) if r.get('vat_amt') != '-' else 0 for r in rows_data)
            totals = {'inc': f"{total_inc:,.2f}", 'excl': f"{total_excl:,.2f}", 'vat': f"{total_vat:,.2f}"}
            
            filepath = filedialog.asksaveasfilename(
                defaultextension='.html',
                initialfile=f"Report_{name}.html",
                filetypes=[("HTML files", "*.html")]
            )
            if filepath:
                ReportGenerator.generate_html_report(rows_data, vat_rate, totals, filepath)
                messagebox.showinfo("Success", f"Report saved")
    
    def backup_db(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension='.sql',
            filetypes=[("SQL files", "*.sql")]
        )
        if filepath:
            self.db.backup_db(filepath)
            messagebox.showinfo("Success", f"Backup saved to {filepath}")
    
    def restore_db(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("SQL files", "*.sql")]
        )
        if filepath:
            if messagebox.askyesno("Confirm", "This will replace all current data. Continue?"):
                self.db.restore_db(filepath)
                self.load_saved_calculations()
                messagebox.showinfo("Success", "Database restored")


def main():
    root = tk.Tk()
    app = VATCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
