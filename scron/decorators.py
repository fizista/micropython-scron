# Copyright 2019 Wojciech Banaś
# This code is released under the GPL3 or individual commercial license.

def run_times(times):
    """
    The decorator determines how many times the given callback can be started.

    :param times: number of start-ups
    :return:
    """
    RUN_TIMES_ID = '__run_times'

    def decorator(callback):
        def wrapper(scorn_instance, callback_name, pointer, memory):
            if RUN_TIMES_ID in memory:
                memory[RUN_TIMES_ID] += 1
            else:
                memory[RUN_TIMES_ID] = 1
            out = callback(scorn_instance, callback_name, pointer, memory)
            if memory[RUN_TIMES_ID] >= times:
                scorn_instance.remove(callback_name)
            return out

        return wrapper

    return decorator


def successfully_run_times(times):
    """
    The decorator determines how many times the given callback can be started.

    Launching a task is considered correct only if the callback returns True.

    :param times: number of start-ups
    :return:
    """
    RUN_TIMES_ID = '__s_run_times'

    def decorator(callback):
        def wrapper(scorn_instance, callback_name, pointer, memory):
            out = callback(scorn_instance, callback_name, pointer, memory)

            if RUN_TIMES_ID not in memory and out == True:
                memory[RUN_TIMES_ID] = 1
            elif RUN_TIMES_ID in memory and out == True:
                memory[RUN_TIMES_ID] += 1
            elif RUN_TIMES_ID not in memory :
                memory[RUN_TIMES_ID] = 0

            if memory[RUN_TIMES_ID] >= times:
                scorn_instance.remove(callback_name)
            return out

        return wrapper

    return decorator


class call_counter:
    """
    Decorator counts the number of callback calls.

    The number of calls is stored in memory[call_counter.ID].

    :param callback:
    :return:
    """
    ID = '__call_counter'

    def __init__(self, callback):
        self.callback = callback

    def __call__(self, scorn_instance, callback_name, pointer, memory):
        if call_counter.ID in memory:
            memory[call_counter.ID] += 1
        else:
            memory[call_counter.ID] = 1
        return self.callback(scorn_instance, callback_name, pointer, memory)


class time_since_last_call:
    """
    Measures the time since the last call.

    Stores the result in memory[time_since_last_call.ID] == tuple(<seconds>, <mili_seconds>)

    :param callback:
    :return:
    """

    ID = '__time_since'
    LAST_CALL_ID = '__last_call'

    def __init__(self, callback):
        self.callback = callback

    def __call__(self, scorn_instance, callback_name, pointer, memory):
        import utime
        current_time = int(utime.time()) * 1000 + (utime.ticks_ms() % 1000)

        if time_since_last_call.LAST_CALL_ID in memory:
            diff = current_time - memory[time_since_last_call.LAST_CALL_ID]
            seconds = diff // 1000
            mili_seconds = diff % 1000
            memory[time_since_last_call.ID] = (seconds, mili_seconds)
        else:
            memory[time_since_last_call.ID] = None

        memory[time_since_last_call.LAST_CALL_ID] = current_time

        return self.callback(scorn_instance, callback_name, pointer, memory)


def debug_call(callback):
    """
    The decorator displays information about the current call

    :param callback:
    :return:
    """

    @call_counter
    @time_since_last_call
    def wrap(scorn_instance, callback_name, pointer, memory):
        print('START call(%3d): %25s,   pointer%18s' % (memory[call_counter.ID], callback_name, str(pointer)))
        if memory[time_since_last_call.ID]:
            last_call = '%d.%ds' % memory[time_since_last_call.ID]
        else:
            last_call = 'none'
        print('    Last call time: %s' % last_call)
        print('    Run pointer: %s' % str(scorn_instance.get_current_pointer()))
        mem_before = dict([(k, d) for k, d in memory.items() if not k.startswith('__')])
        print('    Memory before call: %s' % mem_before)
        out = callback(scorn_instance, callback_name, pointer, memory)
        mem_after = dict([(k, d) for k, d in memory.items() if not k.startswith('__')])
        print('    Memory after  call: %s' % mem_after)
        print('END   call(%3d): %25s,   pointer%18s' % (memory[call_counter.ID], callback_name, str(pointer)))
        print()
        return out

    return wrap
