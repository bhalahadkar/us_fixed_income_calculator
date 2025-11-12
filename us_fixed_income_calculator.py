from datetime import datetime
import numpy as np
from scipy.optimize import brentq


class USFixedIncomeBondCalculator:
    def __init__(self, face_value=100, coupon_rate=0, maturity_date='2030-01-01', settlement_date='2025-11-12',
                 frequency=2, day_count_convention=1, bond_type='corporate', factor=1.0, call_schedule=None,
                 prerefunded_date=None, prerefunded_price=100, step_coupon_schedule=None, variable_rate_schedule=None,
                 cpr=0.06):
        self.face_value = face_value
        self.coupon_rate = coupon_rate / 100
        self.maturity_date = datetime.strptime(maturity_date, '%Y-%m-%d')
        self.settlement_date = datetime.strptime(settlement_date, '%Y-%m-%d')
        self.frequency = frequency
        self.day_count_convention = day_count_convention
        self.bond_type = bond_type.lower()
        self.factor = factor
        self.call_schedule = call_schedule if call_schedule is not None else []
        self.prerefunded_date = prerefunded_date if prerefunded_date is not None else None
        self.prerefunded_price = prerefunded_price
        self.step_coupon_schedule = step_coupon_schedule if step_coupon_schedule is not None else []
        self.variable_rate_schedule = variable_rate_schedule if variable_rate_schedule is not None else self.step_coupon_schedule
        self.cpr = cpr
        if self.bond_type in ['municipal', 'corporate']:
            self.day_count_convention = 0
        elif self.bond_type == 'us_treasury':
            self.day_count_convention = 1
        elif self.bond_type == 't_bill':
            self.day_count_convention = 2
            self.frequency = 0
            self.coupon_rate = 0
        elif self.bond_type == 'mbs':
            self.frequency = 12
            self.face_value *= factor
            self.day_count_convention = 0
        if self.prerefunded_date:
            self.call_schedule.append((self.prerefunded_date, self.prerefunded_price))

    def add_months(self, source_date, months):
        month = source_date.month - 1 + months
        year = source_date.year + month // 12
        month = month % 12 + 1
        day = source_date.day
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]
        if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
            days_in_month = 29
        day = min(day, days_in_month)
        return datetime(year, month, day)

    def days_between(self, d1, d2):
        basis = self.day_count_convention
        if basis in (0, 4):
            y1, m1, d1_day = d1.year, d1.month, d1.day
            y2, m2, d2_day = d2.year, d2.month, d2.day
            if basis == 0:
                if d1_day == 31:
                    d1_day = 30
                if d2_day == 31 and d1_day == 30:
                    d2_day = 30
            else:
                if d1_day == 31:
                    d1_day = 30
                if d2_day == 31:
                    d2_day = 30
            return 360 * (y2 - y1) + 30 * (m2 - m1) + (d2_day - d1_day)
        else:
            days = (d2 - d1).days
            return days

    def get_previous_coupon(self):
        if self.frequency == 0:
            return self.settlement_date
        period_months = 12 // self.frequency
        date = self.maturity_date
        while date > self.settlement_date:
            date = self.add_months(date, -period_months)
        return date

    def get_next_coupon(self):
        if self.frequency == 0:
            return self.maturity_date
        period_months = 12 // self.frequency
        prev = self.get_previous_coupon()
        next_date = self.add_months(prev, period_months)
        if next_date > self.maturity_date:
            next_date = self.maturity_date
        return next_date

    def accrual_days(self):
        prev = self.get_previous_coupon()
        return self.days_between(prev, self.settlement_date)

    def accrued_interest(self):
        if self.frequency == 0:
            return 0
        prev = self.get_previous_coupon()
        next_date = self.get_next_coupon()
        period_days = self.days_between(prev, next_date)
        accrual_days = self.accrual_days()
        coupon_per_period = self.coupon_rate * self.face_value / self.frequency
        return coupon_per_period * (accrual_days / period_days)

    def get_coupon_rate_for_date(self, date):
        rate = self.coupon_rate
        for change_date, new_rate in self.variable_rate_schedule:
            change_date = datetime.strptime(change_date, '%Y-%m-%d')
            if date >= change_date:
                rate = new_rate / 100
        return rate

    def get_cashflows(self, for_call=None):
        if self.bond_type == 't_bill':
            return [(self.maturity_date, self.face_value)]
        if self.bond_type == 'mbs':
            r = self.coupon_rate / 12
            months_remaining = round((self.maturity_date - self.settlement_date).days / 30.417)
            balance = self.face_value
            if months_remaining <= 0:
                return []
            if r == 0:
                pmt = balance / months_remaining
            else:
                pmt = balance * r * (1 + r) ** months_remaining / ((1 + r) ** months_remaining - 1)
            cf = []
            date = self.add_months(self.settlement_date, 1)
            for _ in range(months_remaining):
                interest = balance * r
                principal = pmt - interest
                cf.append((date, pmt))
                balance -= principal
                date = self.add_months(date, 1)
            if balance > 0.01:
                cf[-1] = (cf[-1][0], cf[-1][1] + balance)
            return cf
        cf = []
        period_months = 12 // self.frequency
        date = self.get_next_coupon()
        redemption = self.face_value
        maturity = self.maturity_date
        if for_call:
            maturity = for_call[0]
            redemption = for_call[1]
        while date <= maturity:
            current_rate = self.get_coupon_rate_for_date(date)
            amount = current_rate * self.face_value / self.frequency
            if date == maturity:
                amount += redemption
            cf.append((date, amount))
            date = self.add_months(date, period_months)
        return cf

    def get_cashflows_with_prepayment(self, for_call=None):
        if self.bond_type != 'mbs' and not for_call:
            return self.get_cashflows(for_call)
        if self.bond_type == 'mbs':
            r = self.coupon_rate / 12
            months_remaining = round((self.maturity_date - self.settlement_date).days / 30.417)
            balance = self.face_value
            if months_remaining <= 0:
                return []
            if r == 0:
                pmt = balance / months_remaining
            else:
                pmt = balance * r * (1 + r) ** months_remaining / ((1 + r) ** months_remaining - 1)
            smm = 1 - (1 - self.cpr) ** (1 / 12)
            cf = []
            date = self.add_months(self.settlement_date, 1)
            for _ in range(months_remaining):
                interest = balance * r
                scheduled_principal = pmt - interest
                prepayment = (balance - scheduled_principal) * smm
                total_principal = scheduled_principal + prepayment
                total_payment = interest + total_principal
                cf.append((date, total_payment))
                balance -= total_principal
                date = self.add_months(date, 1)
                if balance <= 0.01:
                    break
            if balance > 0.01:
                cf[-1] = (cf[-1][0], cf[-1][1] + balance)
            return cf
        return self.get_cashflows(for_call)

    def bond_price(self, yield_rate, clean=True):
        if self.bond_type == 't_bill':
            days = self.days_between(self.settlement_date, self.maturity_date)
            d = yield_rate / 100
            price = self.face_value * (1 - d * days / 360)
            return price
        y = yield_rate / 100
        r = y / self.frequency
        cf = self.get_cashflows()
        prev = self.get_previous_coupon()
        next_date = self.get_next_coupon()
        dsc = self.days_between(self.settlement_date, next_date)
        e = self.days_between(prev, next_date)
        w = dsc / e
        dirty_price = 0
        for k in range(1, len(cf) + 1):
            amount = cf[k - 1][1]
            dirty_price += amount / (1 + r) ** (w + k - 1)
        if clean:
            return dirty_price - self.accrued_interest()
        return dirty_price

    def bond_price_with_spread(self, benchmark_yield, spread, for_call=None):
        if self.bond_type == 't_bill':
            days = self.days_between(self.settlement_date, self.maturity_date)
            d = (benchmark_yield + spread) / 100
            price = self.face_value * (1 - d * days / 360)
            return price
        y = (benchmark_yield + spread) / 100
        r = y / self.frequency
        cf = self.get_cashflows_with_prepayment(for_call)
        prev = self.get_previous_coupon()
        next_date = self.get_next_coupon()
        dsc = self.days_between(self.settlement_date, next_date)
        e = self.days_between(prev, next_date)
        w = dsc / e
        dirty_price = 0
        for k in range(1, len(cf) + 1):
            amount = cf[k - 1][1]
            dirty_price += amount / (1 + r) ** (w + k - 1)
        return dirty_price - self.accrued_interest()

    def yield_to_price(self, yield_rate):
        return self.bond_price(yield_rate)

    def price_to_yield(self, price, guess=0.05):
        if self.bond_type == 't_bill':
            days = self.days_between(self.settlement_date, self.maturity_date)
            d = (self.face_value - price) / self.face_value * 360 / days
            return d * 100
        def f(y):
            return self.bond_price(y) - price
        y = brentq(f, -100, 100, xtol=1e-8)
        return y

    def cashflow(self):
        return self.get_cashflows()

    def dv01(self, yield_rate):
        p_plus = self.bond_price(yield_rate + 0.01, clean=False)
        p_minus = self.bond_price(yield_rate - 0.01, clean=False)
        return (p_minus - p_plus) / 2

    def pv01(self, yield_rate):
        return self.dv01(yield_rate)

    def convexity(self, yield_rate):
        dy = 0.0001
        p0 = self.bond_price(yield_rate, clean=False)
        p_up = self.bond_price(yield_rate + dy * 100, clean=False)
        p_down = self.bond_price(yield_rate - dy * 100, clean=False)
        return (p_up + p_down - 2 * p0) / (p0 * dy ** 2)

    def macaulay_duration(self, yield_rate):
        y = yield_rate / 100
        r = y / self.frequency
        cf = self.get_cashflows()
        prev = self.get_previous_coupon()
        next_date = self.get_next_coupon()
        dsc = self.days_between(self.settlement_date, next_date)
        e = self.days_between(prev, next_date)
        w = dsc / e
        dirty_price = 0
        weighted_time = 0
        for k in range(1, len(cf) + 1):
            amount = cf[k - 1][1]
            t_k = (w + k - 1) / self.frequency
            pv = amount / (1 + r) ** (w + k - 1)
            dirty_price += pv
            weighted_time += t_k * pv
        if dirty_price == 0:
            return 0
        return weighted_time / dirty_price

    def modified_duration(self, yield_rate):
        mac_duration = self.macaulay_duration(yield_rate)
        y = yield_rate / 100
        return mac_duration / (1 + y / self.frequency)

    def yield_to_call(self, price):
        if not self.call_schedule:
            raise ValueError("No call schedule provided")
        ytcs = []
        for call_date_str, call_price in self.call_schedule:
            call_date = datetime.strptime(call_date_str, '%Y-%m-%d')
            if call_date <= self.settlement_date:
                continue
            def f(y):
                cf = self.get_cashflows(for_call=(call_date, call_price))
                prev = self.get_previous_coupon()
                next_date = self.get_next_coupon()
                dsc = self.days_between(self.settlement_date, next_date)
                e = self.days_between(prev, next_date)
                w = dsc / e
                r = y / 100 / self.frequency
                dirty = 0
                for k in range(1, len(cf) + 1):
                    amount = cf[k - 1][1]
                    dirty += amount / (1 + r) ** (w + k - 1)
                clean = dirty - self.accrued_interest()
                return clean - price
            y = brentq(f, -100, 100, xtol=1e-8)
            ytcs.append((call_date, y))
        return ytcs

    def oas(self, market_price, benchmark_yield):
        if self.bond_type == 't_bill':
            days = self.days_between(self.settlement_date, self.maturity_date)
            implied_yield = (self.face_value - market_price) / self.face_value * 360 / days * 100
            return (implied_yield - benchmark_yield) * 100
        def f(spread):
            if self.call_schedule and self.bond_type in ['corporate', 'municipal', 'callable']:
                prices = []
                for call_date_str, call_price in self.call_schedule:
                    call_date = datetime.strptime(call_date_str, '%Y-%m-%d')
                    if call_date <= self.settlement_date:
                        continue
                    price = self.bond_price_with_spread(benchmark_yield, spread, for_call=(call_date, call_price))
                    prices.append(price)
                price_to_maturity = self.bond_price_with_spread(benchmark_yield, spread)
                prices.append(price_to_maturity)
                theoretical_price = min(prices) if prices else price_to_maturity
            else:
                theoretical_price = self.bond_price_with_spread(benchmark_yield, spread)
            return theoretical_price - market_price
        try:
            oas = brentq(f, -1000, 1000, xtol=1e-8)
            return oas * 100
        except ValueError:
            return np.nan