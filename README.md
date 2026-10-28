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

The rows with unknowns, blanks and string texts as values are filtered out.









#### Post Analysis Headlines(46 out of 50 rows)
|Total Revenue  

