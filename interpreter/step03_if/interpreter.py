"""A Python byte code interpreter (for learning purpose)"""
import dis
import builtins


class ReturnValue(Exception):
    pass


class Interpreter:
    def __init__(self, source, local_vars=None, dump_code=False, trace_stack=False):
        self._code = compile(source, filename='', mode='exec')
        self._instructions = list(dis.get_instructions(self._code))
        self._next_instruction = 0
        self._locals = {}
        self._stack = []
        self._dump_code = dump_code
        self._trace_stack = trace_stack
        self._builtins = {x: getattr(builtins, x) for x in dir(builtins) if not x.startswith('__')}
        if local_vars:
            for k, v in local_vars.items():
                self.set_local(k, v)

    def get_local(self, name):
        return self._locals[name]

    def set_local(self, name, value):
        self._locals[name] = value

    def get_name(self, namei):
        return self._code.co_names[namei]

    def get_const(self, consti):
        return self._code.co_consts[consti]

    def stack_push(self, value):
        self._stack.append(value)

    def stack_pop(self):
        return self._stack.pop(-1)

    def stack_popn(self, count):
        if count > 0:
            result = self._stack[-count:]
            self._stack = self._stack[:-count]
            return result
        return []

    def exec(self):
        if self._dump_code:
            self.dump_code()

        # each instruction is delegated to a method found by name.
        # If the method returns True, it means it will make code jump itself,
        # or else the code will continue execution to next instruction.
        while True:
            try:
                instruction = self._instructions[self._next_instruction]
                fn = getattr(self, 'exec_' + instruction.opname)
                instruction_result = fn(instruction.arg)
                if self._trace_stack:
                    self.dump_stack(instruction)
                if not instruction_result:
                    self._next_instruction += 1
            except ReturnValue:
                break

    def dump_code(self):
        print(f"====dis code of {self._code.co_name}====")
        print('co_names:', self._code.co_names)
        print('co_consts:', self._code.co_consts)
        print('co_code', self._code.co_code)
        print('co_varnames:', self._code.co_varnames)
        dis.dis(self._code)

    def dump_stack(self, instruction):
        print(f'Stack after {instruction.opname}({instruction.offset}): {self._stack}')

    def exec_LOAD_NAME(self, namei):
        name = self.get_name(namei)
        if name in self._locals:
            value = self.get_local(name)
        elif name in self._builtins:
            value = self._builtins[name]
        else:
            raise NameError(name)
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
        raise ReturnValue()

    def exec_CALL_FUNCTION(self, argc):
        args = self.stack_popn(argc)
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
