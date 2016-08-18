Metrics
=======

Get statistics from the computer

Properties
----------
* **menu (dict(bool))**: Flags for turning off/on various metrics
* **interval (timedelta)**: Interval to check metrics and notify a signal

Dependencies
------------
-   [**psutil**](https://pypi.python.org/pypi/psutil)
-   [lm-sensors](http://linux.die.net/man/1/sensors): (Optional) Used for
        gathering cpu temperature info with `sensors` configuration option.
        Install on Ubuntu with with: `sudo apt-get install lm-sensors`

Commands
--------
* **cpu**: Returns the overall cpu usage
* **platform**: Returns the platform data
* **timestamp**: Returns the current system timestamp
* **report**: Returns an overall report of the gathered statistics

Input
-----
Any list of signals.

Output
------
An attibute is added for each metric read. Attribute names are the *menu* name
followed by an underscore and then then specific metric name. For example, when
reading 'CPU Percentage':
```
{
    'cpu_percentage_overall': 23.2,
    'cpu_percentage_per_cpu': [39.6, 2.5, 45.3, 6.0, 41.4, 4.6, 41.0, 5.6]
}
```

When reading *sensors*, the lm-sensors command `sensors -u` is executed and 
parsed. The attributes on the signal are similar to the psutil attributes,
taking on the format of the word 'sensors', followed by the adapter name and
temperature name, seperated by an underscore. For example when `sensors -u`
returns:
```
acpitz-virtual-0
Adapter: Virtual device
temp1:
  temp1_input: 26.800

coretemp-isa-0000
Adapter: ISA adapter
Core 0:
  temp2_input: 43.000
  temp2_max: 105.000
```
The output signal would look like:
```
{
    'sensors_acpitz-virtual-0_temp1_input': 26.8,
    'sensors_coretemp-isa-0000_temp2_input': 43.0,
    'sensors_coretemp-isa-0000_temp2_max': 105.0
}
```

------------------------------------------------------------------------------

ProcessMetrics
==============

Get process statistics from the computer

Properties
----------
* **menu (dict(bool))**: Flags for turning off/on various metrics

Dependencies
------------
-   [**psutil**](https://pypi.python.org/pypi/psutil)

Commands
--------
None

Input
-----
Any list of signals.

Output
------
TODO: document this
