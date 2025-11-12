from us_fixed_income_calculator import USFixedIncomeBondCalculator


def main():
    # Corporate callable bond example
    corp_bond = USFixedIncomeBondCalculator(
        face_value=100,
        coupon_rate=5,
        maturity_date='2030-01-01',
        settlement_date='2025-11-12',
        frequency=2,
        bond_type='callable',
        call_schedule=[('2027-01-01', 101), ('2028-01-01', 100.5)]
    )
    yield_rate = 4.5
    market_price = 98.5
    benchmark_yield = 4.0

    print("Corporate Callable Bond:")
    print(f"Price at {yield_rate}% yield: {corp_bond.yield_to_price(yield_rate):.4f}")
    print(f"Yield for price {market_price}: {corp_bond.price_to_yield(market_price):.4f}%")
    print(f"Accrued Interest: {corp_bond.accrued_interest():.4f}")
    print(f"Accrual Days: {corp_bond.accrual_days()}")
    print(f"DV01: {corp_bond.dv01(yield_rate):.6f}")
    print(f"Convexity: {corp_bond.convexity(yield_rate):.4f}")
    print(f"Macaulay Duration: {corp_bond.macaulay_duration(yield_rate):.4f} years")
    print(f"Modified Duration: {corp_bond.modified_duration(yield_rate):.4f}")
    print(f"OAS: {corp_bond.oas(market_price, benchmark_yield):.2f} basis points")
    print(f"Yield to Call: {[(d.strftime('%Y-%m-%d'), f'{y:.4f}%') for d, y in corp_bond.yield_to_call(market_price)]}")
    print(f"Cashflows: {[(d.strftime('%Y-%m-%d'), f'{c:.2f}') for d, c in corp_bond.cashflow()]}")
    print()

    # MBS example
    mbs = USFixedIncomeBondCalculator(
        face_value=100,
        coupon_rate=4,
        maturity_date='2030-01-01',
        settlement_date='2025-11-12',
        bond_type='mbs',
        factor=0.9,
        cpr=0.08
    )
    market_price = 99.0
    print("Mortgage-Backed Security:")
    print(f"Price at {yield_rate}% yield: {mbs.yield_to_price(yield_rate):.4f}")
    print(f"OAS: {mbs.oas(market_price, benchmark_yield):.2f} basis points")


if __name__ == "__main__":
    main()