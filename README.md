# ActiGraph (Accelerometer) Data Label Tool
A simple desktop application aims to make your free living data labeling life easier. Wrote in Python with tkinter and matplotlib, it plots ActiGraph data and lets you label the sleep periods and discard transportation data.

## Features
* \[Interactive Plot\] _zoom, pan, and put the label right on the graph_
* \[Discard Data\] _throw away data recorded in transition_
* \[Task List\] _Loads entire folder and indicates which ones are done_

![Usage Example GIF](https://github.com/shi-xin/actigraph_labeler/blob/master/usage_example.gif)

## Installation
Built with Python 3.7, Matplotlib 3.0.0, and tkinter 8.6 in Windows 10.
Directly run label_tool.py in a similar environment will do.

## Quick Start
### 1 - Load
It could either read a single CSV format data from ActiGraph or load an entire folder with such data. Input data should at least contain a timestamp column (or date and time columns), 3 axis columns, and a vector magnitude column. Here is an example data:

![Input Data Example](https://github.com/shi-xin/actigraph_labeler/blob/master/input_data_example.jpg)

### 2 - Interact with Plot
Once file is loaded, it will be plotted automatically. 
* Use mouse to pan and zoom
* Use keyboard arrow keys to pan and zoom
* Right click on the plot to label that point
* Labeled sleep periods will be shaded with light gray color
* Labeled discard periods will be shaded with dark gray color

### 3 - Save
After labeling the data, remember to save a copy to the directory you desire. The output data contains two new columns:
* \[sleep\] _a binary variable, 1 indicates sleeping_
* \[discard\] _a binary variable, 1 indicates discarded_

![Output Data Example](https://github.com/shi-xin/actigraph_labeler/blob/master/output_data_example.jpg)

## TO-DO
* \[Feature\] Support AGD format

## Version
0.0.1

## Get In Touch
Send me an Email if you have any questions or suggestions.
Email: stevexinshi@gmail.com