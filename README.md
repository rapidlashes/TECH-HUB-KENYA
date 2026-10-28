## TECH HUB KENYA
### Overview
Tech Hub Kenya sells phones, laptops and accessories from five stores in Nairobi, Mombasa, Kisumu and Nakuru.
The finance manager wants September's numbers: total revenue, which products earn the most, and which sales were big enough to deserve a follow-up call.

### Problem statement
The core analysis must use only the standard library. The export data is messy — some prices were typed by hand. 
Build the analysis with Python's own tools, make careful decisions about the bad values, and only then use pandas on your laptop to prove your numbers are right.

#### Prerequsites
you need to have these dependencies installed in your virtual environment:

```window powershell
uv add pandas numpy
```
We added the numpy package as a contingency incase we will need to work on the numerical data by performing heavy mathematical operations and arrays, but in our case pandas is enough to work with.

We also need to import these 2 libraries:
```python
import csv
from pathlib import Path
```

The manager has put a threshhold of `50000` in revenue for the most profitable sales, meaning all sales equal or above it deserve a follow up.
This will help evaluate what products are most profitable, fast moving products and where often do these sales occur(location)

### My Approach Step by Step

#### Step 1 : Reading the data 
`read_sales(path)` opens the file with newline="" (what the csv module requires) and reads it with `csv.DictReader`.
It returns every row as a dictionary of strings, with no conversion yet, so reading and cleaning stay separate jobs.
It prints all the rows and the columns (7 columns) in separate lists, and counts the number of rows(50).
A missing file prints a message instead of showing a traceback.

#### Step 2 : Convert numbers and decide what to do with bad values
`def parse_number(value)` converts a  messy numeric string into a float and return **None** if it cant be trusted or the value is not a digit in our case.
The function `convert_rows(rows)` allows you to call the `parse_number(value)` function after cleaning the numerical columns then filters the data doing away with the rows that cant be computated numerically.
The result is a list of cleaned rows called `clean_rows`.
This is what happens in step 2:
|Raw Value            |Repaired Value          |
|---------------------|------------------------|
|'38,999'             |38999                   |
|'KES 45000'          |45000                   |
|N/A                  |Skipped                 |
|'two'                |Skipped                 |
|`blank quantity`     |Skipped                 |
|`blalnk price`       |Skipped                 |

The rows with unknowns, blanks and string texts as values are filtered out. Other values the code rejects, even though this file doesn't contain them: `nan`, `inf` and `1e3` (Python would happily turn them into floats, but they are not till prices), negative numbers, zero quantities or prices, and fractional quantities like `1.5` (you can't sell half a phone). The check is deliberately simple: after removing spaces, commas and KES, what's left must be digits with at most one decimal point.

**An Assumption**: Why not fill in missing prices from other rows? Every product has had one price all month, so `S-3030` is almost certainly `64,999`. But "almost certainly" is a guess, and an imputed price is not recorded revenue. Instead I report what the skipped rows might be worth, below.

#### Step 3 : Total revenue
`total_revenue(rows)` sums up (`quantity` × `unit_price_kes`) for every kept row in `clean_rows`.

#### Step 4 : Revenue by product, store and payment method
`revenue_by(rows, field)` uses a plain dict: if the key isn't in the dict yet, start it at 0.0, then add the row's revenue. One function serves all three breakdowns because the field name is a parameter. No `defaultdict`, no `Counter`. Printed highest first.

#### Step 5 : Top three products
`top_n(totals, n)` returns `(product, revenue)` tuples using `sorted(..., key=lambda item:...)`. The key sorts by revenue descending, and ties are broken alphabetically by product name. I chose that because it is deterministic: the same data always gives the same order, instead of depending on dictionary insertion order. (There are no ties among the top 3 in this data, but a quick test with two products on 10 returns them A before B.)

#### Step 6 : High-value transactions
`high_value(rows: list[dict], threshold: float)` returns a list of dictionaries with revenue above the threshhold. Rather than using a list comprehension I decide to form an empty list then loop in each dictinary in the `clean_rows` list, find revenue above threshhold and appended to my empty list.

#### Step 7 : Statistical functions
functions `mean`, `median` and `minimum_maximum` are written by hand, with no statistics module and no `.min()` or `.max()` inside `minimum_maximum` function:

**mean:** running sum / count.
**median:** sort the values first, take the middle value if the count is odd, or average the two middle values for an even count.
**minimum_maximum:** sort the values(will sort from smallest to largest by default), use index to get the smallest and largest value from in and max values respectively.

Each `raises ValueError("... needs at least one value, got an empty list")` for an empty list, instead of a confusing `ZeroDivisionError` or `IndexError`. They are applied to per-transaction revenue.

#### Step 8 : Verifying with Pandas
verify_with_pandas(path, my_results) re-reads the CSV and applies the same cleaning rules but with different tools: `str.replace()` and `pd.to_numeric(errors="coerce")` instead of my `parse_number`. That way it checks my logic rather than reusing it. It returns these parameters that were earlier calculated entirely by data structures: 

```python
    print(df)                                                       #convert_rows(rows)/clean_rows
    print(f"TOTAL ROWS: {total_rows}")                              #len(clean_rows
    print(f"TOTAL_REVENUE: {total_revenue_df}")                       #total_revenue(rows)
    print(f"GROUPED REVENUE BY STORE:\n {revenue_by_store_df}")       #revenue_by(rows, field)
    print(f"GROUPED REVENUE BY PRODUCT:\n {revenue_by_product_df}")   #revenue_by(rows, field)
    print(f"GROUPED REVENUE BY PAYMENT:\n {revenue_by_payment_df}")  #revenue_by(rows, field)
    print()
    print(f"TOP 3 PRODUCTS BY REVENUE:\n {top_3_products}")   #top_n(totals, n)
    print()
    print(f"ABOVE THRESHHOLD SALES:\n {biggest_sales}")      #high_value(rows: list[dict], threshold: float)
    print()
    print(f'AVERAGE REVENUE: {average_revenue}')         #mean()
    print(f'MEDIAN REVENUE: {middle_revenue}')           #median()
    print(f"LOWEST REVENUE: {lowest_revenue}")           #minimum_maximum()
    print(f"HIGHEST REVENUE: {highest_revenue}")         #minimum_maximum()
```









#### Post Analysis Headlines(46 out of 50 rows)
|Total Revenue  

