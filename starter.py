"""
Day 2 - Sales Analytics Without Pandas
Squad Python Specialization - Data Science, AI & Analytics

Tasks 1-7 use only the standard library. pandas is allowed in task 8, to check your work.
"""
import csv
from pathlib import Path
import pandas as pd
import math

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
        quantity = parse_number(row['quantity'])
        unit_price_kes = parse_number(row['unit_price_kes'])
        if quantity is None or unit_price_kes is None:
            skipped_rows.append({'sale_id': row['sale_id']})
            continue
        clean_rows.append({
            'sale_id': row['sale_id'],
            "sale_id": row["sale_id"],
            "sale_date": row["sale_date"],
            "store": row["store"],
            "product": row["product"],
            "payment_method": row["payment_method"],
            "quantity": int(quantity),
            "unit_price": unit_price_kes,
            "revenue": int(quantity) * unit_price_kes,
        })
    return clean_rows, skipped_rows


def total_revenue(rows: list[dict]) -> float:
    total = 0
    for row in rows:
        total = row['revenue'] + total
    return total


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


def top_n(totals: dict[str, float], n: int = 3) -> list[tuple[str, float]]:
    """Return the n highest (key, value) pairs, highest first."""
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    return ranked[0:n]


def high_value(rows: list[dict], threshold: float) -> list[dict]:
    threshold_transactions = []
    for row in rows:
        total_transaction = row['revenue']
        if total_transaction >= threshold:
            threshold_transactions.append(row)
        else:
            continue
    return threshold_transactions


# Reusable statistics - implement these yourself, no statistics module.
def mean(values: list[float]) -> float:
    if len(values) == 0:
        raise ValueError(f"The list is empty, you need atleast one value!")
    else:
        total = 0
        for value in values:
            total = total + value
        return total/len(values)


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


def minimum_maximum(values: list[float]) -> tuple[float, float]:
    if len(values) == 0:
        raise ValueError(f"list  is empty, you need atleast one value")
    else:
        ordered = sorted(values)  # by default will sort in ascending order
        min = ordered[0]
        max = ordered[-1]
    return min, max


def summary(values: list[float]):
    total_rows_read = len(values)
    valid, invalid = convert_rows(values)
    sum_of_revenue = total_revenue(valid)

    by_store = dict(sorted(revenue_by(
        valid, 'store').items(), key=lambda item: item[1], reverse=True))
    by_product = dict(sorted(revenue_by(
        valid, 'product').items(), key=lambda item: item[1], reverse=True))
    by_payment = dict(sorted(revenue_by(
        valid, 'payment_method').items(), key=lambda item: item[1], reverse=True))

    top_3_products = top_n(by_product, 3)
    most_profitable = high_value(valid, threshhold)

    calculated_avg = mean([row['revenue'] for row in valid])
    calculated_mdn = median([row['revenue'] for row in valid])

    mini, maxi = minimum_maximum([row['revenue'] for row in valid])

    return {
        'total rows': total_rows_read,
        'total valid rows': len(valid),
        'total invalid rows': len(invalid),
        'total revenue': sum_of_revenue,
        'total revenue by store': by_store,
        'total revenue by product': by_product,
        'total revenue by payment': by_payment,
        'top 3 products': top_3_products,
        'high value product': most_profitable,
        'mean': calculated_avg,
        'median': calculated_mdn,
        'lowest value': mini,
        'highest value': maxi
    }


def verify_with_pandas(path: Path, my_results: dict) -> None:
    """Recompute the headline numbers with pandas and print whether each one matches."""
    try:
        import pandas as pd
    except ImportError:
        print(f"pandas is not installed!")
        return {}

    # 1. read the csv file
    df_original = pd.read_csv(path, dtype=str, keep_default_na=False)

    # clean and convert these columns to numeric type
    for column in ['quantity', 'unit_price_kes']:
        text = df_original[column].str.strip().str.upper()
        text = text.str.replace("KES", "", regex=True)
        text = text.str.replace(',', '', regex=True).str.strip()

        # where values are missing after converting to numeric, replace with Nan
        df_original[column] = pd.to_numeric(text, errors='coerce')

    # remove rows with invalid numeric values  in either of the two columns
    df = df_original.dropna(subset=['quantity', 'unit_price_kes'])

    # we are making sure we are selling these product as a whole number, we cant possibly sell 1.5 of a 'phone'
    df = df[(df['quantity'] > 0) & (df['unit_price_kes'] > 0)
            & (df['quantity'] % 1 == 0)].copy()

    # adding a column of revenue to our dataframe
    df['revenue'] = df['quantity'] * df['unit_price_kes']

    # saving the df now back to a csv
    saving_filepath = Path('Data') / 'electronic_sales_clean.csv'
    df.to_csv(saving_filepath, index=False)

    # STATISTICS
    # grouping the total revenue by individual products
    per_product_df = df.groupby('product')['revenue'].sum().reset_index()

    # we will sort the values first according to revenue from highest to lowetst hence the False, then when we encounter a tie in revenue, well sort according to Alphabtical order from A-Z hence the True
    top_products = per_product_df.sort_values(
        ['revenue', 'product'], ascending=[False, True])

    # we only want the top 3
    # it is inform of a dataframe, convert it to a list of tuples as the one in summary() later on
    top_3_products = top_products.head(3)

    # sales whose revenue surpass threshhold
    biggest_sales = df[df['revenue'] >= threshhold]

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
    # remeber, all the above groups are in form of dataframes, later one youll have to convert them to dictionaries to be able to compare them to the ones in summary()

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

    pandas_stats = {
        'total rows': len(df_original),
        'total valid rows': total_rows,
        'total invalid rows': (len(df_original))-total_rows,
        'total revenue': total_revenue_df,
        'total revenue by store': revenue_by_store_df.to_dict(),  # was inititally a dataframe
        # was inititally a dataframe
        'total revenue by product': revenue_by_product_df.to_dict(),
        # was inititally a dataframe
        'total revenue by payment': revenue_by_payment_df.to_dict(),
        # was inititally a dataframe
        'top 3 products': list(zip(top_3_products)),
        'high value product': biggest_sales.to_dict(),  # was inititally a dataframe
        'mean': average_revenue,
        'median': middle_revenue,
        'lowest value': lowest_revenue,
        'highest value': highest_revenue
    }

    comparison = {}  # {count :match, mean: mismatch...etc}

    # unpacking the dict i returned in summary
    my_results = summary(raw_rows)
    for key, value in my_results.items():
        # pandas_stats[key] -> will automatically bring value of that key
        pandas_value = pandas_stats[key]
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            comparison[key] = ('match' if math.isclose(
                value, pandas_value) else 'mismatch')
        else:  # creates an option where by the value of dictionary my_results can be inform of a list or dic, and goes hard on it saying the list or the dic from my_results must match the one in pandas_stats word for word or number for number
            comparison[key] = ('match' if value ==
                               pandas_value else 'mismatch')

    return pandas_stats, comparison


def report(values):
    lines = []
    # 1. call out the summary() here to get the list, unpack it, put it in lines
    statistical_summary = summary(values)
    for key, value in statistical_summary.items():
        lines.append(f"{key}: {value}")
    lines.append("")

    # 2. call out the verify_with_pandas() here to get the list,unpck it, put it in lines
    pandas_stats, comparison = verify_with_pandas(DATA_PATH, y)
    lines.append(f"PANDAS STATISTICS:")
    for key, value in pandas_stats.items():
        lines.append(f"{key} : {value}")
    lines.append("")

    lines.append(f"COMPARING THE STATS FROM PANDAS AND THOSE CALCULATED ABOVE")
    for key, value in comparison.items():
        lines.append(f"{key} : {value}")
    lines.append("")

    print("\n".join(lines))
    return lines


def save_report(path):
    report_lines = report(raw_rows)
    with open(path, 'w') as file:
        for l in report_lines:
            file.write(f"{l}\n")


if __name__ == "__main__":
    # function 1:
    try:
        raw_rows = read_sales()
    except FileNotFoundError:
        print(f"Error! could not find {DATA_PATH}")
    print(raw_rows)
    print()

    # function 2:
    clean_rows, skipped_rows = convert_rows(raw_rows)
    print(f"CLEANED ROWS: {clean_rows}")
    print(f"TOTAL CLEANED ROWS: {len(clean_rows)}")
    print()
    print(f"SKIPPED ROWS (SALE ID'S): {skipped_rows}")
    print(f"TOTAL SKIPPED ROWS: {len(skipped_rows)}")
    print()

    # function 3:
    sum_of_revenue = total_revenue(clean_rows)
    print(f"REVENUE TOTAL: {sum_of_revenue}")
    print()

    # function 4:
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

    # function 5:
    top_3 = top_n(revenue_by_product, 3)
    print(top_3)
    print()

    # function 6:
    high = high_value(clean_rows, threshhold)
    print(high)
    print()
    # for this function Idecide to go the long way and not use (list comprehension as the brief suggested)

    # function 7:
    calculated_average = mean([row['revenue'] for row in clean_rows])
    print(f"CALCULATED AVERAGE: {calculated_average}")

    # function 8:
    calculated_median = median([row['revenue'] for row in clean_rows])
    print(f"CALCULATED MEDIAN: {calculated_median}")

    # function 9:
    min, max = minimum_maximum([row['revenue'] for row in clean_rows])
    print(f"SMALLEST REVENUE: {min}")
    print(f"LARGEST REVENUE: {max}")
    print()

    # function 10:
    y = summary(raw_rows)
    print(y)

    # function 11:
    pandas_stats, comparison = verify_with_pandas(DATA_PATH, y)
    print(pandas_stats)
    print(comparison)

    # function 12:
    h = report(raw_rows)
    print(h)

    # fucntion 13:
    report_path = Path(__file__).resolve().parent / 'report.txt'
    z = save_report(report_path)
    print(z)
