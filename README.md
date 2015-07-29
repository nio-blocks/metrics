Metrics
=======

Get statistics from the computer

Properties
----------
-   menu (dict(bool)): Flags for turning off/on various metrics
-   interval (timedelta): Interval to check metrics and notify a signal

Dependencies
------------
-   [**psutil**](https://pypi.python.org/pypi/psutil)
-   [lm-sensors](http://linux.die.net/man/1/sensors): (Optional) Used for
        gathering cpu temperature info.

Commands
--------
TODO: document this

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

------------------------------------------------------------------------------

ProcessMetrics
==============

Get process statistics from the computer

Properties
----------
TODO: document this

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
