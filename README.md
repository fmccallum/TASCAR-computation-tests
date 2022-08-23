# TASCAR-computation-tests
Runs TASCAR scenes to calculate their computational demand on Linux
Restricted to Linux because the scripts make use of OS commands

The script reads an XML file and finds which data is missing/needs to be generated for each test.
This data is then generated for each TASCAR scene.
All the data is then plotted for each graph specified.

<myxml>
<testfile>
<data>
<tscene path="path to folder containing TASCAR scene" label="nspk"/>
<tscene path="path to folder containing TASCAR scene" label="vbap"/>
</data>
<graphs>
<renderFile sources="10 100 500 700" repeats="2" samples="5" plot="all"/>
<jackPercentage sources="10 100 500 700" repeats="2" plot="mean"/>
</graphs>
</testfile>
</myxml>

## Running tests and plotting data:

Need an XML file which details the TASCAR scenes/data to use and the graphs to be plotted
If running jackpercentage test, need jack running
Then need to run command

````
python3 computationstests.py test.xml
````
