"""A Python byte code interpreter (for learning purpose)"""
import dis


class Interpreter:
    def __init__(self, source):
        self._code = compile(source, filename='', mode='exec')
        self._locals = {}
        self._stack = []

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

    def exec(self, dump_code=False, trace_stack=False):
        if dump_code:
            self.dump_code()
        for instruction in dis.get_instructions(self._code):
            fn = getattr(self, 'exec_' + instruction.opname)
            fn(instruction.arg)
            if trace_stack:
                self.dump_stack(instruction)

    def dump_code(self):
        print(f"====dis code of {self._code.co_name}====")
        print('co_names:', self._code.co_names)
        print('co_consts:', self._code.co_consts)
        print('co_code', self._code.co_code)
        print('co_varnames', self._code.co_varnames)
        dis.dis(self._code)

    def dump_stack(self, instruction):
        print(f'Stack after {instruction.opname}({instruction.offset}): {self._stack}')

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
        pass
