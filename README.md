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
The result is a list of cleaned rows called `clean_rows`, as well as a list of dictionaries `skipped_rows` with ssale Ids as values.
This is what happens in step 2:
|Raw Value            |Repaired Value          |
|---------------------|------------------------|
|'38,999'             |38999                   |
|'KES 45000'          |45000                   |
|N/A                  |Skipped                 |
|'two'                |Skipped                 |
|`blank quantity`     |Skipped                 |
|`blank price`       |Skipped                 |

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

Each `raises ValueError("... needs at least one value, got an empty list")` for an empty list, instead of a confusing `ZeroDivisionError` or `IndexError`. 

#### Step 8: Statisitc Summary
`summary(values` returns a dictionary of statistical summary , all the way from row counts for the valid and rejected data to grouping revenue by different fieldnames eg `payment_method`.

#### Step 9 : Verifying with Pandas
`verify_with_pandas(path, my_results)` re-reads the CSV using dataframes and applies the same cleaning rules as above. The cleaning is done in the two numeric column [unit_price_kes, quantity]. Rows with invalid numeric values are dropped.

```python
    
     df = df[(df['quantity'] > 0) & (df['unit_price_kes'] > 0)
            & (df['quantity'] % 1 == 0)].copy()
```
Above is the final rule for validating our rows.We are maming sure that we are selling the products as a whole number. fir instance we cant possibly sell `1.5` (quantity) of a phone, so we leave the floats as they are and drop the rows.
Having dropped those rows , we save our current dataframe to a csv file.
At the end of the function we are eventually returning 2 dictionaries: 
1. `pandas_stats` - shows statistics calculated from pandas
2. `comparison` - returns a ***match*** for those pandas statistics that match or are close to `summary()` statistics, and ***mismatch*** if otherwsise.

### Report writting and saving
All findings above are appended in a list which is written in a `report.txt` file.
The file is saved in out project folder directory.Below are some of the findings captured in our report:
1. Total number of rows
2. Total number of valid rows
3. Total number of invalid rows
4. Total revenue
5. Total revenue grouped by Payment method, Store, Product
6. mean, median, highes and lowest value
7. 3 most profitable products
8. Products of high value(above or equal to threshhold)
9. highest and lowest revenue generated

### Discripancies
We are trying to see matches and mismatches between calculated values from the parsed_data and dataframe values:

|Statisctics        |Parsed values                |df(pandas) values           |
|-------------------|-----------------------------|----------------------------|
|Mean               |28706.96                     |28495.91                    |
|Median             |10998.0                      |11097                       |
|Minimum revenue    |1499.0                       |1499.0                      |
|Maximum revenue    |259996.0                     |259996.0                    |
|Output rows        |45                           |46                          |
|HRP                |Lenovo Tab:149994.0          |HP 15 Laptop:389994.0       |

**HRP** stands for Highest Revenue_generating Product

### Data Quality Warning/Evaluation
4 rows were skipped in pandas, so the total is a definitely a lower bound. Using the prices charged elsewhere in the month, they are probably worth roughly KES `90,000+` in total:

|Transaction_id                 |Problem                          |Estuimated value                      |
|-------------------------------|---------------------------------|--------------------------------------|
|S-3006                         |quantity `two`                   |3199 * 2 = 6398                       |
|S-3035                         |quantity `blank`                 |min value= 13,499->(Tecno Spark 20)   |
|S-3030                         |price `N/A`                      |HP 15 Laptop at 64,999/=              |
|S-3039                         |price `blank`                    |	5,999 (Safaricom Neon Ray)           |

**NOTE:** S-3030 could have been included in high values Sales if it were not dropped

#### Conclusion 
We put our executable code in the `if __name__ == __main__ :` in an instance of importation of a class or a function in another python file.


