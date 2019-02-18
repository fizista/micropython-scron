from scron.week import simple_cron
from scron.decorators import run_times, call_counter, time_since_last_call, debug_call


@debug_call
def some_counter(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1


def start_another_one_callback(scorn_instance, callback_name, pointer, memory):
    callback_name_e5s_id = 'every fifth second'
    scorn_instance.add('run only 3 times', run_times(3)(some_counter))


simple_cron.add('every 2 minutes 3 times', start_another_one_callback, seconds=0, minutes=range(0, 59, 2))
simple_cron.run()
