import utime
import machine
from scron.week import simple_cron

simple_cron.add('test1', lambda *a, **k: print('RETURN: test1', utime.localtime()), seconds=10)
simple_cron.add('test2', lambda *a, **k: print('RETURN: test2', utime.localtime()), seconds=9)
simple_cron.run()

# 2000-01-01 00:00:05
machine.RTC().datetime(utime.localtime(0))
print('RUN', utime.localtime())

simple_cron._sync_time()

print(list(simple_cron.list()))
utime.sleep(4)

simple_cron.remove('test2')
simple_cron.remove('test1')
print(list(simple_cron.list()))
print('END', utime.localtime())
