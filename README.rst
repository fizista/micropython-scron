.. role:: bash(code)
   :language: bash

.. role:: python(code)
   :language: python

***************************
Simple CRON for MicroPython
***************************

SimpleCRON is a time-based task scheduling program inspired by the well-known
CRON program for Unix systems.

The software was tested under micropython 1.10 (esp32, esp8266) and python 3.5.

`Project documentation. <https://fizista.github.io/micropython-scron/html/index.html>`_

What you can do with this library:
##################################
* Run any task at precisely defined intervals
* Delete and add tasks while the program is running.
* Run the task a certain number of times and many more.

Requirements:
#############
* The board on which the micropython is installed(v1.10)
* The board must have support for hardware timers.


Install
#######
You can install using the upip:

.. code-block:: python

    import upip
    upip.install("micropython-scron")

or

.. code-block:: bash

    micropython -m upip install -p modules micropython-scron


You can also clone this repository, and install it manually:

.. code-block:: bash

    git clone https://github.com/fizista/micropython-scron.git
    cd ./micropython-scron
    ./flash-src.sh




ESP8266
*******

The library on this processor must be compiled into binary code.

The MicroPython cross compiler is needed for this.

If you already have the mpy-cross command available, then run the bash script:

.. code-block:: bash

    ./compile.sh

and then upload the library to the device, e.g. using the following script:

.. code-block:: bash

    ./flash-byte.sh



Simple examples
###############

Simple code to run every second:

.. code-block:: python

    from scron.week import simple_cron
    # Depending on the device, you need to add a task that
    # will be started at intervals shorter than the longest
    # time the timer can count.
    # esp8266 about 5 minutes
    simple_cron.add('null', lambda *a, **k: None, minutes=5, removable=False)
    simple_cron.add('helloID', lambda *a,**k: print('hello'))
    simple_cron.run()


Code, which is activated once a Sunday at 12:00.00:

.. code-block:: python

    simple_cron.add(
        'Sunday12.00',
        lambda *a,**k: print('wake-up call'),
        weekdays=6,
        hours=12,
        minutes=0,
        seconds=0
    )


Every second minute:

.. code-block:: python

    simple_cron.add(
        'Every second minute',
        lambda *a,**k: print('second call'),
        minutes=range(0, 59, 2),
        seconds=0
    )


Other usage samples can be found in the 'examples' directory.

How to use it
#############

Somewhere in your code you have to add the following code,
and from then on SimpleCRON is ready to use.

.. code-block:: python

    from scron.week import simple_cron
    simple_cron.run() # You have to run it once. This initiates the SimpleCRON action,
                      # and reserve one timmer.



To add a task you are using:

.. code-block:: python

    simple_cron.add(<callback_id_string>, <callback>, ...)


Callbacks
#########

Example of a callback:

.. code-block:: python

    def some_counter(scorn_instance, callback_name, pointer, memory):
        if 'counter' in memory:
            memory['counter'] += 1
        else:
            memory['counter'] = 1


where:

* :python:`scorn_instance` - SimpleCRON instance, in this case scron.weekend.simple_cron
* :python:`callback_name` - Callback ID
* :python:`pointer` - This is an indicator of the time in which the task was to be run.
  Example: (6, 13, 5, 10).  This is **(** Sunday **,** 1 p.m. **,** minutes 5 **,** seconds 10 **)**
* :python:`memory` - Shared memory for this particular callback, between all calls.
  By default this is a dictionary.

Important notes:
################

* If a task takes a very long time, it blocks the execution of other tasks!
* If there are several functions to run at a given time, then they are
  started without a specific order.
* If the time has been changed (time synchronization with the network,
  own time change), run the :python:`simple_cron.sync_time()` function,
  which will set a specific point in time. Without this setting,
  it may happen that some callbacks will not be started.


What has not been tested:
#########################

* SimpleCRON operation during sleep

How to test
###########

First install the following things:

.. code-block:: bash

    git clone https://github.com/fizista/micropython-scron.git
    cd micropython-scron/
    micropython -m upip install -p modules micropython-unittest
    micropython -m upip install -p modules micropython-time


Then run the tests:

.. code-block:: bash

    ./run_tests.sh


*******************
Support and license
*******************

If you have found a mistake or other problem, write in the issues.

If you need a different license for this library (e.g. commercial),
please contact me: fizista+scron@gmail.com.


