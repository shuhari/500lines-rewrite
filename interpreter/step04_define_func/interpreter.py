"""A Python byte code interpreter (for learning purpose)"""
import dis
from collections import ChainMap


def dump_recursive(code):

    def dump(acode):
        print(f"====dis code of {acode.co_name}====")
        print('co_names:', acode.co_names)
        print('co_consts:', acode.co_consts)
        print('co_code', acode.co_code)
        dis.dis(acode)
        #
        # print("====instructions====")
        # for instruction in dis.get_instructions(acode):
        #     print(instruction.opcode, instruction.opname, instruction.arg, instruction.offset)

    dump(code)
    for item in code.co_consts:
        if hasattr(item, 'co_code'):
            dump_recursive(item)


def builtin_scope():
    return ChainMap({
        'divmod': divmod,
    })


class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value


class Function:
    def __init__(self, interpreter, name, code, freevars, annonations, kwdefaults, defaults):
        self.interpreter = interpreter
        self.name = name
        self.code = code
        self.freevars = freevars
        self.annonations = annonations
        self.kwdefaults = kwdefaults
        self.defaults = defaults

    def __call__(self, *args, **kwargs):
        frame = Frame(self.interpreter, self.code, self.interpreter.top_frame().scope)
        for index, arg in enumerate(args):
            frame.set_var(index, arg)
        self.interpreter.frame_push(frame)
        result = frame.exec()
        self.interpreter.frame_pop()
        return result


class Frame:
    def __init__(self, interpreter, code, scope):
        self._interpreter = interpreter
        self._code = code
        self._instructions = list(dis.get_instructions(self._code))
        self._next_instruction = 0
        self.scope = scope.new_child()
        self._stack = []

    def get_local(self, name):
        return self.scope[name]

    def set_local(self, name, value):
        self.scope[name] = value

    def get_name(self, namei):
        return self._code.co_names[namei]

    def get_const(self, consti):
        return self._code.co_consts[consti]

    def set_var(self, varnum, value):
        name = self._code.co_varnames[varnum]
        self.set_local(name, value)

    def stack_push(self, value):
        self._stack.append(value)

    def stack_pop(self):
        return self._stack.pop(-1)

    def exec(self, trace_stack=False):
        # each instruction is delegated to a method found by name.
        # If the method returns True, it means it will make code jump itself,
        # or else the code will continue execution to next instruction.
        while True:
            try:
                instruction = self._instructions[self._next_instruction]
                fn = getattr(self, 'exec_' + instruction.opname)
                instruction_result = fn(instruction.arg)
                if trace_stack:
                    self.dump_stack(instruction)
                if not instruction_result:
                    self._next_instruction += 1
            except ReturnValue as e:
                return e.value

    def dump_stack(self, instruction):
        print(f'Stack after instruction {instruction.opname}({instruction.offset}): {self._stack}')

    def exec_LOAD_NAME(self, namei):
        name = self.get_name(namei)
        value = self.get_local(name)
        self.stack_push(value)

    def exec_LOAD_CONST(self, consti):
        value = self.get_const(consti)
        self.stack_push(value)

    def exec_BINARY_ADD(self, _):
        tos = self.stack_pop()
        tos1 = self.stack_pop()
        result = tos1 + tos
        self.stack_push(result)

    def exec_STORE_NAME(self, namei):
        name = self.get_name(namei)
        value = self.stack_pop()
        self.set_local(name, value)

    def exec_RETURN_VALUE(self, _):
        value = self.stack_pop()
        raise ReturnValue(value)

    def exec_CALL_FUNCTION(self, argc):
        args = []
        for i in range(argc):
            args.insert(0, self.stack_pop())
        func = self._stack.pop(-1)
        result = func(*args)
        self.stack_push(result)

    def exec_COMPARE_OP(self, opname):
        opname = dis.cmp_op[opname]
        comparers = {
            '<': lambda x, y: x < y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y,
            '!=': lambda x, y: x != y,
            '>': lambda x, y: x > y,
            '>=': lambda x, y: x >= y,
            'in': lambda x, y: x in y,
            'not in': lambda x, y: x not in y,
            'is': lambda x, y: x is y,
            'is not': lambda x, y: x is not y,
        }
        comparer = comparers[opname]
        rhs = self.stack_pop()
        lhs = self.stack_pop()
        result = comparer(lhs, rhs)
        self.stack_push(result)

    def exec_POP_JUMP_IF_FALSE(self, target):
        value = self.stack_pop()
        if not value:
            self.jump_by_offset(target)
            return True
        return False

    def jump_by_offset(self, offset):
        index = [index for index, instruction in enumerate(self._instructions)
                 if instruction.offset == offset][0]
        self._next_instruction = index

    def exec_JUMP_FORWARD(self, delta):
        offset = self._instructions[self._next_instruction + 1].offset + delta
        self.jump_by_offset(offset)
        return True

    def exec_MAKE_FUNCTION(self, flags):
        name = self.stack_pop()
        code = self.stack_pop()
        freevars, annonations, defaults, kwdefaults = None, None, None, None
        if flags & 0x8:
            freevars = self.stack_pop()
        if flags & 0x4:
            annonations = self.stack_pop()
        if flags & 0x2:
            kwdefaults = self.stack_pop()
        if flags & 0x1:
            defaults = self.stack_pop()
        func = Function(self._interpreter, name, code, freevars, annonations, kwdefaults, defaults)
        self.stack_push(func)

    def exec_LOAD_FAST(self, varnum):
        name = self._code.co_varnames[varnum]
        value = self.get_local(name)
        self.stack_push(value)


class Interpreter:
    def __init__(self, source):
        self._code = compile(source, filename='', mode='exec')
        self._scope = builtin_scope()
        self._frames = []
        main_frame = Frame(self, self._code, self._scope)
        self._frames.append(main_frame)
        # main frame treat as global scope and never pop

    def top_frame(self):
        return self._frames[-1]

    def get_local(self, name):
        return self.top_frame().get_local(name)

    def set_local(self, name, value):
        self.top_frame().set_local(name, value)

    def frame_push(self, frame):
        self._frames.append(frame)

    def frame_pop(self):
        return self._frames.pop(-1)

    def exec(self, dump_code=False, trace_stack=False):
        if dump_code:
            dump_recursive(self._code)
        self.top_frame().exec()
