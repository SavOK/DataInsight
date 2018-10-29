# The Problem
 Create frequency tables from the statistics provided by the US Department of Labor
  and its Office of Foreign Labor Certification Performance Data.
 The program should pick __top 10__ occupations and states for certified visa 
 applications.
 
 # The Approach 
 The program is written in Python3.6 and makes use of standard 
 data structures (dictionaries, set, list) and modules (pathlib, itertools, operator).
 The unit tests were written with unittest module. 
 The program reads the text file and converts it in the 
 __Table__ object (list of dictionaries) where each element of 
 the list is the row from the input table and column names from the header lines of the table are used as keys for the dictionaries
 
 # How To Run
 
 ```bash
 python3.6 ./src/h1b_counting.py ./input/data_file.txt ./output/top_10_occupations.txt ./output/top_10_states.txt
 ```
 - input data_file.txt is a semi-colon separated text file. __Must have the header line__
 - output top_10_occupations.txt and top_10_states.txt contain the Summary tables on the most frequent occupations and states for which 
 applications have been certified. 
 
