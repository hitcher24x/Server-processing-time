Scenario Data Science project (python 3)
-----------------------------------------------.

--------Description and Architecture :

This program reads, cleans and analyses the data from a server containing 2 weeks of server response times.

The files are :

-Scenario.py 
-Presentation.pdf
-requirements.txt
-Readme.md

*Scenario.py provides useful plots

*requirements.txt contains libraries : pandas (data manipulation), matplotlib (plots), statsmodels (time series decomposition), scipy (fit densities), seaborn (fit densities)

*Presentation.pdf contains analysis for both scenarios


---------Run the program:

-Download the data from this url :
https://s3.amazonaws.com/dd-interview-data/data_scientist/baseball/for_candidate.tgz

-Put the files into the same forlder as Scenario.py
-Install dependancies : 'pip install -r requirements.txt'
-Run 'python3 Scenario.py file_argument'
for example, for the scenario 1 launch : 'python3 Scenario.py scenario1.txt'



