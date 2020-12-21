"""
Using Python standard module dis to inspect byte code

ref: https://docs.python.org/3/library/dis.html#dis.Bytecode
"""
import dis


def main():
    print("====dis code====")
    source = "n = a + 1"
    code = compile(source, filename='', mode='exec')
    print('co_names:', code.co_names)
    print('co_consts:', code.co_consts)
    print('co_code', code.co_code)
    dis.dis(code)

    print("====instructions====")
    for instruction in dis.get_instructions(code):
        print(instruction.opcode, instruction.opname, instruction.arg, instruction.offset)
