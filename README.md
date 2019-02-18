# micropython-scron - Simple CRON for MicroPython

SimpleCRON is a time-based task scheduling program inspired by the well-known 
CRON program for Unix systems.

The software was tested under micropython 1.10 (esp32, esp8266) and python 3.5.

## What you can do with this library:
* Run any task at precisely defined intervals
* Delete and add tasks while the program is running.
* Run the task a specified number of times.

## Requirements:
* The board on which the micropython is installed(v1.10)
* The board must have support for hardware timers.
 

# Install
You can install using the upip:

```python
import upip
upip.install("micropython-scron")
```
or
```bash
micropython -m upip install -p modules micropython-scron
```

You can also clone this repository, and install it manually:

```bash
git clone https://github.com/fizista/micropython-scron.git
cd ./micropython-scron
./flash-src.sh
```



## ESP8266

The library on this processor must be compiled into binary code.

The MicroPython cross compiler is needed for this.

If you already have the mpy-cross command available, then run the bash script:

```bash
./compile.sh
```
and then upload the library to the device, e.g. using the following script:
```bash
./flash-byte.sh
```


# Simple examples

Simple code to run every second:
```python
from scron.week import simple_cron
simple_cron.add('helloID', lambda *a,**k: print('hello'))
simple_cron.run()
```

Code, which is activated once a Sunday at 12:00.00:
```python
simple_cron.add(
    'Sunday12.00', 
    lambda *a,**k: print('wake-up call'),
    weekdays=6,
    hours=12,
    minutes=0,
    seconds=0
)
```

Every second minute:
```python
simple_cron.add(
    'Every second minute', 
    lambda *a,**k: print('second call'),
    minutes=range(0, 59, 2),
    seconds=0
)
```

Other usage samples can be found in the 'examples' directory.

# How to use it

Somewhere in your code you have to add the following code, 
and from then on SimpleCRON is ready to use.
```python
from scron.week import simple_cron
simple_cron.run() # You have to run it once. This initiates the SimpleCRON action, 
                  # and reserve one timmer.
                            
```

To add a task you are using:
```python
simple_cron.add(<callback_id_string>, <callback>, ...)
```

## Callbacks

Example of a callback:
```python
def some_counter(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1
```

where:

* `scorn_instance` - SimpleCRON instance, in this case scron.weekend.simple_cron
* `callback_name` - Callback ID
* `pointer` - This is an indicator of the time in which the task was to be run. 
Example: (6, 13, 5, 10).  This is **(** Sunday **,** 1 p.m. **,** minutes 5 **,** seconds 10 **)**
* `memory` - Shared memory for this particular callback, between all calls.
By default this is a dictionary.

## Methods

### simple_cron.run
`simple_cron.run(timer_id=1)`

Initiates a list of tasks and reserves one hardware timer.

You can run this method only once!

**Warning:**
"OSError: 261" - error means a problem with the hardware timer. 
Try to set another timer ID. 
[See MicroPython documentation for machine.Timer.](https://docs.micropython.org/en/latest/library/machine.Timer.html)

### simple_cron.add
`simple_cron.add(self, callback_name, callback, seconds=simple_cron.WILDCARD, 
minutes=simple_cron.WILDCARD, hours=simple_cron.WILDCARD, weekdays=simple_cron.WILDCARD):`

Adds an entry to the current queue.

    :param callback_name: callback name ID
    :param callback: callable
    :param seconds: 0-59 or list(second, ...), default: WILDCARD_VALUE
    :param minutes: 0-59 or list(minutes, ...), default: WILDCARD_VALUE
    :param hours: 0-23 or list(hours, ...), default: WILDCARD_VALUE
    :param weekdays: 0-6 or list(days, ...) 0=monday,6=sunday, default: WILDCARD_VALUE


### simple_cron.remove
`simple_cron.remove(callback_name):`

Removes from the counters a callback that occurs under ID callback_name.

### simple_cron.remove_all
`simple_cron.remove_all()`

Removes all calls from the counters.

### simple_cron.sync_time
`simple_cron.sync_time()`

Synchronizes SimpleCRON with time.

### simple_cron.callback_exists
`simple_cron.callback_exists(callback_name)`

Checking if a callback exists

## Important notes:
* If a task takes a very long time, it blocks the execution of other tasks!
* If there are several functions to run at a given time, then they are 
started without a specific order.
* If the time has been changed (time synchronization with the network, 
own time change), run the **simple_cron.sync_time()** function, 
which will set a specific point in time. Without this setting, 
it may happen that some callbacks will not be started.


## What has not been tested:
* SimpleCRON operation during sleep

# How to test
First install the following things:
```bash
git clone https://github.com/fizista/micropython-scron.git
cd micropython-scron/
micropython -m upip install -p modules micropython-unittest
micropython -m upip install -p modules micropython-time
```

Then run the tests:

```bash
./run_tests.sh
```

# Support or license

If you have found a mistake or other problem, write in the issues.

If you need a different license for this library (e.g. commercial), 
please contact me: fizista+scron@gmail.com.
