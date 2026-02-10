import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font


class VATCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("VAT Calculator")
        self.root.geometry("900x700")
        self.root.minsize(900, 700)
        
        # Style configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('Header.TLabel', font=('Arial', 10, 'bold'))
        self.style.configure('Total.TLabel', font=('Arial', 11, 'bold'))
        self.style.configure('Blue.TFrame', background='#003366')
        
        self.rows = []
        self.max_rows = 15
        
        self.create_widgets()
        
    def create_widgets(self):
        # Header Frame
        header_frame = ttk.Frame(self.root, padding="20 20 20 10")
        header_frame.pack(fill='x')
        
        # VAT Rate Input
        vat_frame = ttk.Frame(header_frame)
        vat_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(vat_frame, text="VAT Rate (%)", font=('Arial', 10, 'bold'), 
                 background='#003366', foreground='white', padding="10 5").pack(side='left')
        
        self.vat_rate_var = tk.StringVar(value="20")
        vat_entry = ttk.Entry(vat_frame, textvariable=self.vat_rate_var, width=10, 
                             font=('Arial', 10))
        vat_entry.pack(side='left', padx=(10, 10))
        vat_entry.bind('<KeyRelease>', lambda e: self.recalculate_all())
        
        ttk.Label(vat_frame, text="Enter VAT rate here", foreground='gray').pack(side='left')
        
        # Instructions
        ttk.Label(header_frame, text="Enter the product and price information in the left hand columns", 
                 font=('Arial', 9)).pack(anchor='w')
        ttk.Label(header_frame, text="The columns on the right will automatically calculate the price excluding VAT", 
                 font=('Arial', 9)).pack(anchor='w')
        
        # Table Frame
        table_frame = ttk.Frame(self.root, padding="20 10 20 10")
        table_frame.pack(fill='both', expand=True)
        
        # Create headers
        headers = ["Item", "Price Inc. VAT", "Price Excl. VAT", "VAT Amt"]
        header_bg = '#003366'
        header_fg = 'white'
        
        # Header row
        for col, header in enumerate(headers):
            if col == 0:
                label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'),
                               bg=header_bg, fg=header_fg, width=20, height=2)
            elif col == 1:
                label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'),
                               bg=header_bg, fg=header_fg, width=18, height=2)
            else:
                label = tk.Label(table_frame, text=header, font=('Arial', 10, 'bold'),
                               bg=header_bg, fg=header_fg, width=18, height=2)
            label.grid(row=0, column=col, sticky='nsew', padx=1, pady=1)
        
        # Currency labels
        for i in range(1, self.max_rows + 1):
            tk.Label(table_frame, text="£", bg='#f0f0f0').grid(row=i, column=1, sticky='e', padx=(5, 0))
            tk.Label(table_frame, text="£", bg='#f0f0f0').grid(row=i, column=2, sticky='e', padx=(5, 0))
            tk.Label(table_frame, text="£", bg='#f0f0f0').grid(row=i, column=3, sticky='e', padx=(5, 0))
        
        # Create rows
        for i in range(1, self.max_rows + 1):
            row_widgets = {}
            
            # Item name
            item_var = tk.StringVar()
            item_entry = ttk.Entry(table_frame, textvariable=item_var, width=22)
            item_entry.grid(row=i, column=0, sticky='nsew', padx=1, pady=1, ipady=3)
            row_widgets['item'] = item_var
            
            # Price Inc. VAT
            price_inc_var = tk.StringVar()
            price_inc_entry = ttk.Entry(table_frame, textvariable=price_inc_var, width=16)
            price_inc_entry.grid(row=i, column=1, sticky='nsew', padx=1, pady=1, ipady=3)
            price_inc_entry.bind('<KeyRelease>', lambda e, row=i-1: self.calculate_row(row))
            row_widgets['price_inc'] = price_inc_var
            
            # Price Excl. VAT (calculated)
            price_excl_var = tk.StringVar(value="-")
            price_excl_label = ttk.Label(table_frame, textvariable=price_excl_var, 
                                        width=16, anchor='e', background='#f0f0f0')
            price_excl_label.grid(row=i, column=2, sticky='nsew', padx=1, pady=1)
            row_widgets['price_excl'] = price_excl_var
            
            # VAT Amount (calculated)
            vat_amt_var = tk.StringVar(value="-")
            vat_amt_label = ttk.Label(table_frame, textvariable=vat_amt_var, 
                                     width=16, anchor='e', background='#f0f0f0')
            vat_amt_label.grid(row=i, column=3, sticky='nsew', padx=1, pady=1)
            row_widgets['vat_amt'] = vat_amt_var
            
            self.rows.append(row_widgets)
        
        # Configure grid weights
        table_frame.grid_columnconfigure(0, weight=2)
        table_frame.grid_columnconfigure(1, weight=1)
        table_frame.grid_columnconfigure(2, weight=1)
        table_frame.grid_columnconfigure(3, weight=1)
        
        # Totals Frame
        totals_frame = ttk.Frame(self.root, padding="20 10 20 20")
        totals_frame.pack(fill='x', side='bottom')
        
        # Separator line
        ttk.Separator(totals_frame, orient='horizontal').pack(fill='x', pady=(0, 10))
        
        # Totals row
        totals_inner = ttk.Frame(totals_frame)
        totals_inner.pack(fill='x')
        
        ttk.Label(totals_inner, text="TOTAL", font=('Arial', 11, 'bold')).pack(side='left', padx=(0, 150))
        
        # Total Inc. VAT
        self.total_inc_var = tk.StringVar(value="£ 0.00")
        ttk.Label(totals_inner, text="£", font=('Arial', 11, 'bold')).pack(side='left', padx=(50, 0))
        ttk.Label(totals_inner, textvariable=self.total_inc_var, font=('Arial', 11, 'bold'), 
                 width=12).pack(side='left')
        
        # Total Excl. VAT
        self.total_excl_var = tk.StringVar(value="£ 0.00")
        ttk.Label(totals_inner, text="£", font=('Arial', 11, 'bold')).pack(side='left', padx=(20, 0))
        ttk.Label(totals_inner, textvariable=self.total_excl_var, font=('Arial', 11, 'bold'), 
                 width=12).pack(side='left')
        
        # Total VAT
        self.total_vat_var = tk.StringVar(value="£ 0.00")
        ttk.Label(totals_inner, text="£", font=('Arial', 11, 'bold')).pack(side='left', padx=(20, 0))
        ttk.Label(totals_inner, textvariable=self.total_vat_var, font=('Arial', 11, 'bold'), 
                 width=12).pack(side='left')
        
    def get_vat_rate(self):
        try:
            rate = float(self.vat_rate_var.get())
            return rate / 100
        except ValueError:
            return 0.20  # Default 20%
    
    def calculate_row(self, row_idx):
        if row_idx >= len(self.rows):
            return
            
        row = self.rows[row_idx]
        vat_rate = self.get_vat_rate()
        
        try:
            price_inc_text = row['price_inc'].get().strip()
            if not price_inc_text or price_inc_text == '-':
                row['price_excl'].set("-")
                row['vat_amt'].set("-")
            else:
                # Remove any currency symbols and commas
                price_inc_text = price_inc_text.replace('£', '').replace(',', '').replace('$', '')
                price_inc = float(price_inc_text)
                
                # Calculate Price Excl. VAT
                price_excl = price_inc / (1 + vat_rate)
                
                # Calculate VAT Amount
                vat_amt = price_inc - price_excl
                
                # Update display
                row['price_excl'].set(f"{price_excl:,.2f}")
                row['vat_amt'].set(f"{vat_amt:,.2f}")
        except ValueError:
            row['price_excl'].set("-")
            row['vat_amt'].set("-")
        
        self.calculate_totals()
    
    def recalculate_all(self):
        for i in range(len(self.rows)):
            self.calculate_row(i)
    
    def calculate_totals(self):
        total_inc = 0
        total_excl = 0
        total_vat = 0
        
        for row in self.rows:
            try:
                price_inc_text = row['price_inc'].get().strip()
                if price_inc_text and price_inc_text != '-':
                    price_inc_text = price_inc_text.replace('£', '').replace(',', '').replace('$', '')
                    price_inc = float(price_inc_text)
                    total_inc += price_inc
            except ValueError:
                pass
            
            try:
                price_excl_text = row['price_excl'].get().strip()
                if price_excl_text and price_excl_text != '-':
                    price_excl_text = price_excl_text.replace('£', '').replace(',', '').replace('$', '')
                    price_excl = float(price_excl_text)
                    total_excl += price_excl
            except ValueError:
                pass
            
            try:
                vat_text = row['vat_amt'].get().strip()
                if vat_text and vat_text != '-':
                    vat_text = vat_text.replace('£', '').replace(',', '').replace('$', '')
                    vat = float(vat_text)
                    total_vat += vat
            except ValueError:
                pass
        
        self.total_inc_var.set(f"{total_inc:,.2f}")
        self.total_excl_var.set(f"{total_excl:,.2f}")
        self.total_vat_var.set(f"{total_vat:,.2f}")


def main():
    root = tk.Tk()
    app = VATCalculator(root)
    root.mainloop()


if __name__ == "__main__":
    main()
