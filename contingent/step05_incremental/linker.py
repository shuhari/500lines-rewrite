from typing import Iterable


def link(ctx, name):
    """process link step to generate final html lines"""
    for line in ctx.cache.get_code('doc', name):
        for result_line in get_output_lines(ctx, line):
            yield result_line


def get_output_lines(ctx, line):
    """Expression evaluated to result, otherwise treated as plain text"""
    if line.startswith('{{') and line.endswith('}}'):
        expr = line[2:-2].strip()
        result = eval(expr, {}, {'ctx': ctx})
        if isinstance(result, str):
            yield result
        elif isinstance(result, Iterable):
            for item in result:
                yield item
        else:
            raise ValueError(f'Expected either str of list[str]', result)
    else:
        yield line
