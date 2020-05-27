import time


TIMES = 10000000


def unoptimized_code() -> str:
    return """
lines.append("Message 1")
lines.append("Message 2")
lines.append("Message 3")
"""


def optimized_code() -> str:
    return """
c_append = lines.append    
c_append("Message 1")
c_append("Message 2")
c_append("Message 3")
"""


def test(fn):
    start = time.perf_counter()
    source = fn()
    code = compile(source, '', 'exec')
    for i in range(TIMES):
        lines = []
        exec(code, None, {"lines": lines})
        result = '\t'.join(lines)
    elapsed = time.perf_counter() - start
    print(f"Execute {fn.__name__} used time: {elapsed}, result: {result}")


def main():
    test(unoptimized_code)
    test(optimized_code)


if __name__ == '__main__':
    main()
