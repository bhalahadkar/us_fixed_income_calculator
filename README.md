# US Fixed Income Bond Calculator

A Python-based calculator for US fixed income securities, supporting Corporate Bonds, Municipal Bonds, Mortgage-Backed Securities (MBS), US Treasuries, T-Bills, Callable Bonds, Prerefunded Bonds, Variable Coupon Bonds, and Stepped Coupon Bonds.

## Features
- Calculates:
  - Price from yield and yield from price
  - Accrued interest and accrual days
  - DV01 (Dollar Value of a 01) and PV01
  - Cash flows
  - Convexity
  - Macaulay and Modified Duration
  - Yield to Call for callable bonds
  - Option-Adjusted Spread (OAS) for bonds with embedded options
- Supports various day count conventions (30/360 US, Actual/Actual, Actual/360)
- Handles prepayments for MBS using a Constant Prepayment Rate (CPR)
- Supports call schedules and variable/stepped coupon schedules

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt


## Parameter
Parameters

face_value: Bond face value (default: 100)
coupon_rate: Annual coupon rate in percent (e.g., 5 for 5%)
maturity_date: Maturity date in 'YYYY-MM-DD' format
settlement_date: Settlement date in 'YYYY-MM-DD' format
frequency: Coupon payments per year (e.g., 2 for semi-annual)
day_count_convention: 0 (30/360 US), 1 (Actual/Actual), 2 (Actual/360)
bond_type: 'corporate', 'municipal', 'us_treasury', 't_bill', 'mbs', 'callable'
factor: Pool factor for MBS (default: 1.0)
call_schedule: List of tuples [('YYYY-MM-DD', call_price), ...]
prerefunded_date: Prerefunded date in 'YYYY-MM-DD' format
prerefunded_price: Prerefunded call price
step_coupon_schedule or variable_rate_schedule: List of tuples [('YYYY-MM-DD', new_rate), ...]
cpr: Constant Prepayment Rate for MBS (default: 0.06)