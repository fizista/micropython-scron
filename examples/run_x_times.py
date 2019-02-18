from scron.week import simple_cron
from scron.decorators import run_times


def some_counter(scorn_instance, callback_name, pointer, memory):
    if 'counter' in memory:
        memory['counter'] += 1
    else:
        memory['counter'] = 1
    print('Call %d' % memory['counter'])


simple_cron.add('run only 5 times', run_times(5)(some_counter))
simple_cron.run()
