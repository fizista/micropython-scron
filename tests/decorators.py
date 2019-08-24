import utime
import machine
from scron.week import simple_cron
from scron import decorators

utime.localtime(0)
# 2000-01-01 00:00:05
machine.RTC().datetime(utime.localtime(0))


@decorators.run_times(6)
@decorators.call_counter
def test_runtimes_x6(scorn_instance, callback_name, pointer, memory):
    print('RETURN: test_runtimes_x6          %d sec. %d' % (memory[decorators.call_counter.ID], utime.localtime()[5]))
    if memory[decorators.call_counter.ID] >= 6:
        scorn_instance.remove(callback_name)


@decorators.successfully_run_times(3)
@decorators.call_counter
def test_suc_runtimes_x3(scorn_instance, callback_name, pointer, memory):
    print('RETURN: test_suc_runtimes_x3      %d sec. %d' % (memory[decorators.call_counter.ID], utime.localtime()[5]))
    return not bool(memory[decorators.call_counter.ID] % 2)


@decorators.time_since_last_call
@decorators.call_counter
def test_time_since_last_call(scorn_instance, callback_name, pointer, memory):
    print('RETURN: test_time_since_last_call %d sec. %d' % (memory[decorators.call_counter.ID], utime.localtime()[5]))
    if memory[decorators.call_counter.ID] >= 6:
        scorn_instance.remove(callback_name)


print('RUN', utime.localtime())
simple_cron.add('test_runtimes_x6', test_runtimes_x6)
simple_cron.add('test_suc_runtimes_x3', test_suc_runtimes_x3)
simple_cron.add('test_time_since_last_call', test_time_since_last_call, seconds=[10, 19])
simple_cron.run()
print(list(simple_cron.list()))
utime.sleep(21)
simple_cron.remove_all()
print('END', utime.localtime())
