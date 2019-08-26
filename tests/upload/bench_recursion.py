def rec(level=0):
    try:
        print('Level %d' % level)
        rec(level + 1)
    except RuntimeError as e:
        import sys
        sys.print_exception(e)
        print('Max level: %d\n\n' % (level - 1))


def rec2(level=0):
    buf = 'X' * 500
    len(buf)
    try:
        print('Level %d' % level)
        rec2(level + 1)
    except RuntimeError as e:
        import sys
        sys.print_exception(e)
        print('Max level: %d\n\n' % (level - 1))
