# TASCAR-computation-tests
Runs TASCAR scenes to calculate their computational demand on Linux.
Restricted to Linux because the scripts make use of OS commands

The script reads an XML file and finds which data is missing/needs to be generated for each test.
This data is then generated for each TASCAR scene.
All the data is then plotted for each graph specified.

An XML file for two different graphs each with two data sources looks like this:

```xml
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
```

## Running tests and plotting data:

Need an XML file which details the TASCAR scenes/data to use and the graphs to be plotted
If running jackpercentage test, need jack running
Then need to run command

````
python3 computationtests.py test.xml
````

## Data
Within \<data\> tags, \<tscene\> elements are placed.
These point the script to where the files used for tests are stored as well as providing options for how new data is generated.

### Data options


````xml
<tscene path="path to scene folder" label="nspk" data_option="nothing" reference="/path to reference folder"/>
````

"label" is used for the legend on the graphs

"data_option" decides whether data is generated. "missing" only generates data if the required test isn't already in the folder. "nothing" doesn't generate any data. "overwrite" deletes all previous data and geneates new data. "collate" generates data and keeps the old data.


"reference" links the data to another TASCAR scene by passing a path to a folder containing the scene. This can be used by graphs to subtract a reference performance at each test.

"ref_option" similar to "data_option" but decides how data is generated for the reference scene. Defaults to same as main scene.


## Graphs
Within \<graphs\> tags, different tests are placed, either renderFile or jackPercentage. These both share some options and have their own settings that can be changed through the xml file.

### Graph options


````xml
<type-of-graph sources="10 100 500 700" repeats="2" plot="mean" ref="True" bars="std"/>
````

"sources" is the number of sources that are placed in a scene. This is a string containing numbers seperated by a space. All the data for each scene is plotted regardless of whether it is in this string, but these numbers are used to decide the data to be generated. 

"plot" is either "mean" or "all". "all" plots all the data for generated for the test as a line graph.

"repeats" is the number of repeats of each test when generating data.

"ref" is the reference and decides whether to use the reference when plotting the data. For plotting the mean, the reference mean is subtracted at each source. When plotting all the data, the reference data is also plotted. The reference data is also generated for each source number based on the data options.

"bars" is whether to plot error bars. The options are "std" for standard deviation and "range" for the range of the data.

## renderFile

The renderFile tests uses a "sources.tsc" file in the data folder and generates a new scene with a number of sources added. A "tascar_renderfile" command is then used, which renders the audio quicker than real-time, to measures how long the scene takes to render. The result therefore depends on the length of the scene which should be kept consistent. 

### renderFile options


````xml
<renderFile sources="10 100 500 700" samples="5"/>
````

"samples" option is used because the repeats saves the reult of each test in a seperate file. Since renderfile only has one result for each test, this seems a bit wasteful. So samples just repeats the test a few times and outputs to the same file.

## jackPercentage

The jackPercentage tests uses a "sources.tsc" file in the data folder and generates a new scene with a number of sources added. The test then runs the scene in real-time and measures the jack usage using a "jack_cpu_load" command. This command outputs the cpu load every second. It was found that for some scenes the CPU load would not decrease when the TASCAR scene was closed, seemingly because jconvolver was still using resources. The script therefore uses a "killall jmatconvol" command, which won't work with other convolution tools. Also, when a plugin is too computationally demanding the load goes from 100% to something much lower. This isn't captured by these scripts so might give odd results.

### jackPercentage options


````xml
<jackPercentage sources="10 100 500 700" gui="true" run_time="15" source_time="0.1" />
````
"gui" if "true" truns the scene with the gui, if "false" runs the scene using "tascar_cli"

"run_time" time in seconds for which scene is run and jack usage measured over. Jack usage sampled once a sceond so this also decides the number of samples. 

"source_time". As the number of sources increases there is a larger time to construct and start the scene therefore this is a number that is multiplied by the number of sources to decide how many seconds to wait before measuring the jack usage. Defaults to 0.1. There is also an additional 2 seconds of waitime.
