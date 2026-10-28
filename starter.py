"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path

DATA_PATH = Path("Data") / "electronics_sales.csv"
threshhold = 50000


def read_sales(path: Path = DATA_PATH) -> list[dict[str, str]]:
    """Read the CSV with the csv module and return the raw rows."""
    with open(path, newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        total_rows = len(rows)
        columns = reader.fieldnames
        print(f"COLUMNS:{columns}")
        print(f"TOTAL ROWS:{total_rows}")
    return rows


try:
    filepath = Path(
        r"C:\Users\ahmed\Downloads\ASSIGNMENT_2\Data\electronics_sales.csv")
    raw_rows = read_sales(filepath)
except FileNotFoundError:
    print(f"Error! could not find {DATA_PATH}")
print(raw_rows)
print()
print()


def parse_number(value: str) -> float | None:
    """Convert a messy numeric string to a float, or return None if it cannot be trusted."""
    text = value.strip().upper()  # force the string value to be upper case
    text = text.replace('KES', "")
    text = text.replace(',', '')
    if text.isdigit():
        return float(text)
    else:
        return None


# Im calling the parse_number() function here on convert_rows() function
def convert_rows(rows: list[dict[str, str]]) -> tuple[list[dict], list[dict]]:
    """Return (clean_rows, skipped_rows). Clean rows have numeric quantity, unit price and revenue."""
    clean_rows = []
    skipped_rows = []
    for row in rows:  # row is one dictinary among the whole list
        qty = parse_number(row['quantity'])
        unit_price = parse_number(row['unit_price_kes'])
        if qty is None or unit_price is None:
            skipped_rows.append({'sale_id': row['sale_id']})
            continue
        clean_rows.append({
            'sale_id': row['sale_id'],
            "sale_id": row["sale_id"],
            "sale_date": row["sale_date"],
            "store": row["store"],
            "product": row["product"],
            "payment_method": row["payment_method"],
            "quantity": int(qty),
            "unit_price": unit_price,
            "revenue": int(qty) * unit_price,
        })
    return clean_rows, skipped_rows


clean_rows, skipped_rows = convert_rows(raw_rows)
print(f"CLEANED ROWS: {clean_rows}")
print(f"TOTAL CLEANED ROWS: {len(clean_rows)}")
print()
print(f"SKIPPED ROWS (SALE ID'S): {skipped_rows}")
print(f"TOTAL SKIPPED ROWS: {len(skipped_rows)}")
print()
print()


def total_revenue(rows: list[dict]) -> float:
    total = 0
    for row in rows:
        total = row['revenue'] + total
    return total


sum_of_revenue = total_revenue(clean_rows)
print(f"REVENUE TOTAL: {sum_of_revenue}")
print()
print()


def revenue_by(rows: list[dict], field: str) -> dict[str, float]:
    """Total revenue grouped by any column (product, store, payment_method...)."""
    totals = {}
    for row in rows:
        name = row[field]
        if name not in totals:
            totals[name] = 0
        else:
            totals[name] = totals[name] + row['revenue']
    return totals


revenue_by_store = dict(sorted(revenue_by(
    clean_rows, 'store').items(), key=lambda item: item[1], reverse=True))
print(f"REVENUE BY STORE: {revenue_by_store}")


revenue_by_product = dict(sorted(revenue_by(
    clean_rows, 'product').items(), key=lambda item: item[1], reverse=True))
print(f"REVENUE BY PRODUCT: {revenue_by_product}")


revenue_by_payment = dict(sorted(revenue_by(
    clean_rows, 'payment_method').items(), key=lambda item: item[1], reverse=True))
print(f"REVENUE BY PAYMENT:{revenue_by_payment}")
print()
print()


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return ranked[0:n]


top_3 = top_n(revenue_by_product, 3)
print(top_3)
print()
print()


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    threshold_transactions = []
    for row in rows:
        total_transaction = row['revenue']
        if total_transaction >= threshold:
            threshold_transactions.append(row)
        else:
            continue
    return threshold_transactions


high = high_value(clean_rows, threshhold)
print(high)
print()
print()
# for this function Idecide to go the long way and not use (list comprehension as the brief suggested)


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    if len(values) == 0:
        raise ValueError(f"The list is empty, you need atleast one value!")
    else:
        total = 0
        for value in values:
            total = total + value
        return total/len(values)


calculated_average = mean([row['revenue'] for row in clean_rows])
print(f"CALCULATED AVERAGE: {calculated_average}")


def median(values: list[float]) -> float:
    if len(values) == 0:
        raise ValueError(f"list is empty, you need atleast one value")
    else:
        ordered = sorted(values)
        x = len(ordered) % 2
        y = len(ordered) // 2
        if x == 1:
            median_number = ordered[y]
        elif x == 0:
            median_number = (ordered[y-1] + ordered[y])/2
        return median_number


calculated_median = median([row['revenue'] for row in clean_rows])
print(f"CALCULATED MEDIAN: {calculated_median}")


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if len(values) == 0:
        raise ValueError(f"list  is empty, you need atleast one value")
    else:
        ordered = sorted(values)  # by default will sort in ascending order
        min = ordered[0]
        max = ordered[-1]
    return min, max


min, max = minimum_maximum([row['revenue'] for row in clean_rows])
print(f"SMALLEST REVENUE: {min}")
print(f"LARGEST REVENUE: {max}")
print()
print()


def verify_with_pandas(path: Path, my_results: dict) -> None:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    try:
        import pandas as pd
    except ImportError:
        print(f"pandas is not installed!")
        return {}

    # 1. read the csv file
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    # clean and convert these columns to numeric type
    for column in ['quantity', 'unit_price_kes']:
        text = df[column].str.strip().str.upper()
        text = text.str.replace("KES", "", regex=True)
        text = text.str.replace(',', '', regex=True).str.strip()

        # where values are missing after converting to numeric, replace with Nan
        df[column] = pd.to_numeric(text, errors='coerce')

    # remove rows with invalid numeric values  in either of the two columns
    df = df.dropna(subset=['quantity', 'unit_price_kes'])

    # we are making sure we are selling these product as a whole number, we cant possibly sell 1.5 of a 'phone'
    df = df[(df['quantity'] > 0) & (df['unit_price_kes'] > 0)
            & (df['quantity'] % 1 == 0)].copy()

    # calculate revenue
    df['revenue'] = df['quantity'] * df['unit_price_kes']

    # grouping the total revenue by individual products
    per_product_df = df.groupby('product')['revenue'].sum().reset_index()

    # we will sort the values first according to revenue from highest to lowetst hence the False, then when we encounter a tie in revenue, well sort according to Alphabtical order from A-Z hence the True
    top_products = per_product_df.sort_values(
        ['revenue', 'product'], ascending=[False, True])

    # we only want the top 3
    top_3_products = top_products.head(3)

    # sales whose revenue surpass threshhold
    biggest_sales = df[df['revenue'] > threshhold]

    # how many rows were maintained after cleaning
    total_rows = len(df)

    # highest,lowest, median  average and total revenue attained
    highest_revenue = df['revenue'].max()
    lowest_revenue = df['revenue'].min()
    middle_revenue = df['revenue'].median()
    average_revenue = df['revenue'].mean()
    total_revenue_df = df['revenue'].sum()

    # total revenue grouped according to payment, products, store
    revenue_by_payment_df = df.groupby('product')['revenue'].sum()
    revenue_by_product_df = df.groupby('product')['revenue'].sum()
    revenue_by_store_df = df.groupby('product')['revenue'].sum()

    print(df)
    print(f"TOTAL ROWS: {total_rows}")
    print(f"TOTAL_REVENUE: {total_revenue_df}")
    print()
    print()
    print(f"GROUPED REVENUE BY STORE:\n {revenue_by_store_df}")
    print(f"GROUPED REVENUE BY PRODUCT:\n {revenue_by_product_df}")
    print(f"GROUPED REVENUE BY PAYMENT:\n {revenue_by_payment_df}")
    print()
    print(f"TOP 3 PRODUCTS BY REVENUE:\n {top_3_products}")
    print()
    print(f"ABOVE THRESHHOLD SALES:\n {biggest_sales}")
    print()
    print(f'AVERAGE REVENUE: {average_revenue}')
    print(f'MEDIAN REVENUE: {middle_revenue}')
    print(f"LOWEST REVENUE: {lowest_revenue}")
    print(f"HIGHEST REVENUE: {highest_revenue}")

    df.to_csv(
        r"C:\Users\ahmed\Downloads\ASSIGNMENT_2\Data\electronic_sales_clean.csv", index=False)


x = verify_with_pandas(DATA_PATH,
                       [{'cleaned_rows': clean_rows},
                        {'total_cleaned_rows': len(clean_rows)},
                        {'revenue_total': sum_of_revenue},
                        {'total_revenue_by_store': revenue_by_store},
                        {'total_revenue_by_product': revenue_by_product},
                        {'total_revenue_by_payment': revenue_by_payment},
                        {'top_3_products': top_3},
                        {'products_above_threshold': high},
                        {'calculated_average': calculated_average},
                        {'calculated_median': calculated_median},
                        {'smallest_revenue': min},
                        {'largest_revenue': max}])
print(x)

# if __name__ == "__main__":
#     # TODO
#     pass
