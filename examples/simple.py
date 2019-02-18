from scron.week import simple_cron
from scron.decorators import run_times, call_counter, time_since_last_call, debug_call


@debug_call
def some_counter(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1


simple_cron.add('every second minute', some_counter, seconds=0, minutes=range(0, 59, 2))
simple_cron.run() # You have to run it once. This initiates the SimpleCRON action, and reserve one timmer.

simple_cron.add('every 10 seconds', some_counter, seconds=range(0, 59, 10))
