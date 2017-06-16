Details

Seeking someone to write a script that will parse a html file, extract the data required, and insert into a SQL table.

The script:
- will need a modifiable connectionstring so I can point it at my own SQL instance.
- can be written in any free Windows-based script tool (PowerShell preferred, but Python and other light-weight install apps ok; prefer not to use SSIS)
- can be written in C#, C++, VBNET if you prefer
- will need to parse from 'Closed Transactions:' and finish at 'Closed P/L:' (markers)
- is only concerned with the rows of data between these two markers
- the rows are typically in pairs
- must not insert duplicate entries

