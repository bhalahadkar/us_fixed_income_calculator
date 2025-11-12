import tkinter as tk
from tkinter import ttk, messagebox
from us_fixed_income_calculator import USFixedIncomeBondCalculator
from datetime import datetime

class BondCalculatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("US Fixed Income Bond Calculator")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Input fields
        ttk.Label(main_frame, text="Bond Type:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.bond_type = ttk.Combobox(main_frame, values=[
            'corporate', 'municipal', 'us_treasury', 't_bill', 'mbs', 'callable'
        ], state='readonly')
        self.bond_type.set('corporate')
        self.bond_type.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Face Value:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.face_value = ttk.Entry(main_frame)
        self.face_value.insert(0, "100")
        self.face_value.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Coupon Rate (%):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.coupon_rate = ttk.Entry(main_frame)
        self.coupon_rate.insert(0, "5")
        self.coupon_rate.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Maturity Date (YYYY-MM-DD):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.maturity_date = ttk.Entry(main_frame)
        self.maturity_date.insert(0, "2030-01-01")
        self.maturity_date.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Settlement Date (YYYY-MM-DD):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.settlement_date = ttk.Entry(main_frame)
        self.settlement_date.insert(0, "2025-11-12")
        self.settlement_date.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Coupon Frequency (per year):").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.frequency = ttk.Entry(main_frame)
        self.frequency.insert(0, "2")
        self.frequency.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="MBS Factor (for MBS):").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.factor = ttk.Entry(main_frame)
        self.factor.insert(0, "1.0")
        self.factor.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="CPR (for MBS, e.g., 0.06):").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.cpr = ttk.Entry(main_frame)
        self.cpr.insert(0, "0.06")
        self.cpr.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Call Schedule (e.g., [('2027-01-01', 101)]):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.call_schedule = ttk.Entry(main_frame)
        self.call_schedule.insert(0, "")
        self.call_schedule.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Variable/Step Schedule (e.g., [('2027-01-01', 6)]):").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.variable_schedule = ttk.Entry(main_frame)
        self.variable_schedule.insert(0, "")
        self.variable_schedule.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Yield Rate (%):").grid(row=10, column=0, sticky=tk.W, pady=2)
        self.yield_rate = ttk.Entry(main_frame)
        self.yield_rate.insert(0, "4.5")
        self.yield_rate.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Market Price:").grid(row=11, column=0, sticky=tk.W, pady=2)
        self.market_price = ttk.Entry(main_frame)
        self.market_price.insert(0, "98.5")
        self.market_price.grid(row=11, column=1, sticky=(tk.W, tk.E), pady=2)

        ttk.Label(main_frame, text="Benchmark Yield (%):").grid(row=12, column=0, sticky=tk.W, pady=2)
        self.benchmark_yield = ttk.Entry(main_frame)
        self.benchmark_yield.insert(0, "4.0")
        self.benchmark_yield.grid(row=12, column=1, sticky=(tk.W, tk.E), pady=2)

        # Calculate button
        ttk.Button(main_frame, text="Calculate", command=self.calculate).grid(row=13, column=0, columnspan=2, pady=10)

        # Results display
        self.results = tk.Text(main_frame, height=15, width=60)
        self.results.grid(row=14, column=0, columnspan=2, pady=10)
        self.results.config(state='disabled')

    def validate_inputs(self):
        try:
            face_value = float(self.face_value.get())
            coupon_rate = float(self.coupon_rate.get())
            frequency = int(self.frequency.get())
            factor = float(self.factor.get())
            cpr = float(self.cpr.get())
            yield_rate = float(self.yield_rate.get())
            market_price = float(self.market_price.get())
            benchmark_yield = float(self.benchmark_yield.get())

            # Validate dates
            maturity_date = datetime.strptime(self.maturity_date.get(), '%Y-%m-%d')
            settlement_date = datetime.strptime(self.settlement_date.get(), '%Y-%m-%d')
            if settlement_date >= maturity_date:
                raise ValueError("Settlement date must be before maturity date")

            # Validate call schedule
            call_schedule = []
            if self.call_schedule.get():
                call_schedule = eval(self.call_schedule.get())
                if not isinstance(call_schedule, list):
                    raise ValueError("Call schedule must be a list of tuples")
                for date_str, price in call_schedule:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    float(price)

            # Validate variable/step schedule
            variable_schedule = []
            if self.variable_schedule.get():
                variable_schedule = eval(self.variable_schedule.get())
                if not isinstance(variable_schedule, list):
                    raise ValueError("Variable schedule must be a list of tuples")
                for date_str, rate in variable_schedule:
                    datetime.strptime(date_str, '%Y-%m-%d')
                    float(rate)

            return (face_value, coupon_rate, maturity_date.strftime('%Y-%m-%d'),
                    settlement_date.strftime('%Y-%m-%d'), frequency, factor, cpr,
                    call_schedule, variable_schedule, yield_rate, market_price, benchmark_yield)
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return None

    def calculate(self):
        inputs = self.validate_inputs()
        if not inputs:
            return

        (face_value, coupon_rate, maturity_date, settlement_date, frequency, factor, cpr,
         call_schedule, variable_schedule, yield_rate, market_price, benchmark_yield) = inputs

        try:
            bond = USFixedIncomeBondCalculator(
                face_value=face_value,
                coupon_rate=coupon_rate,
                maturity_date=maturity_date,
                settlement_date=settlement_date,
                frequency=frequency,
                bond_type=self.bond_type.get(),
                factor=factor,
                cpr=cpr,
                call_schedule=call_schedule,
                variable_rate_schedule=variable_schedule
            )

            results = []
            results.append(f"Bond Type: {self.bond_type.get().capitalize()}")
            results.append(f"Price at {yield_rate}% yield: {bond.yield_to_price(yield_rate):.4f}")
            results.append(f"Yield for price {market_price}: {bond.price_to_yield(market_price):.4f}%")
            results.append(f"Accrued Interest: {bond.accrued_interest():.4f}")
            results.append(f"Accrual Days: {bond.accrual_days()}")
            results.append(f"DV01: {bond.dv01(yield_rate):.6f}")
            results.append(f"PV01: {bond.pv01(yield_rate):.6f}")
            results.append(f"Convexity: {bond.convexity(yield_rate):.4f}")
            results.append(f"Macaulay Duration: {bond.macaulay_duration(yield_rate):.4f} years")
            results.append(f"Modified Duration: {bond.modified_duration(yield_rate):.4f}")
            results.append(f"OAS: {bond.oas(market_price, benchmark_yield):.2f} basis points")
            if bond.call_schedule and bond.bond_type in ['callable', 'corporate', 'municipal']:
                ytc = bond.yield_to_call(market_price)
                results.append(f"Yield to Call: {[(d.strftime('%Y-%m-%d'), f'{y:.4f}%') for d, y in ytc]}")
            cashflows = bond.cashflow()
            results.append(f"Cashflows: {[(d.strftime('%Y-%m-%d'), f'{c:.2f}') for d, c in cashflows[:5]]} ...")

            self.results.config(state='normal')
            self.results.delete(1.0, tk.END)
            self.results.insert(tk.END, "\n".join(results))
            self.results.config(state='disabled')
        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error: {str(e)}")

def run_gui():
    root = tk.Tk()
    app = BondCalculatorGUI(root)
    root.mainloop()