def link(ctx, name):
    """process link step to generate final html lines"""
    lines = ctx.get_doc(name)
    result = []
    for x in lines:
        result.extend(link_line(ctx, x))
    return result


def link_line(ctx, line):
    if line.startswith('{{') and line.endswith('}}'):
        expr = line[2:-2].strip()
        result = eval(expr, {}, {'ctx': ctx})
        if isinstance(result, list):
            for item in result:
                yield item
        else:
            yield result
    else:
        yield line
