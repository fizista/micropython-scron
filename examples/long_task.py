from utime import sleep
from scron.week import simple_cron
from scron.decorators import run_times, call_counter, time_since_last_call, debug_call


@debug_call
def some_counter(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1


@debug_call
def long_task(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1
    sleep(20)

simple_cron.add('every 10 seconds', long_task, seconds=range(0, 59, 10))
simple_cron.add('every 2 seconds', some_counter, seconds=range(0, 59, 2))
simple_cron.run()


