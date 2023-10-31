from py_motor import *

p = Plugin("sample.python")
print(p.Motor.TestCases.Enum.Value1)
print(p.Motor.TestCases.Enum.Value2)
print(p.Motor.TestCases.Enum.Value3)


def motor_name(motor_type: Value) -> str:
    constness = int(motor_type.constness) == 0 and 'const ' or ''
    access = int(motor_type.access) == 0 and 'const ' or ''
    if motor_type.indirection == Motor.Meta.Type.Indirection.Value:
        return '%s%s' % (access, motor_type.metaclass.name)
    else:
        if motor_type.indirection == Motor.Meta.Type.Indirection.RawPtr:
            ptr = 'raw'
        elif motor_type.indirection == Motor.Meta.Type.Indirection.WeakPtr:
            ptr = 'weak'
        elif motor_type.indirection == Motor.Meta.Type.Indirection.RefPtr:
            ptr = 'ref'
        else:
            ptr = '???'
        return '%s%s<%s%s>' % (constness, ptr, access, motor_type.metaclass.name)


def print_method(motor_method: Value) -> None:
    for overload in motor_method.overloads:
        param_list = []
        for param in overload.params:
            param_list.append((motor_name(param.type), param.name))
        print(
            '  %s %s (%s)' % (
                motor_name(overload.returnType), motor_method.name,
                ', '.join(('%s %s' % param for param in param_list)))
        )


def motor_help(klass: Value) -> None:
    print('class %s' % klass.name)
    if klass.constructor:
        print('List of constructors:')
        print_method(klass.constructor)
    print('List of methods:')
    for motor_method in klass.methods:
        print_method(motor_method)
    print('List of properties:')
    for motor_property in klass.properties:
        print(' ', motor_name(motor_property.type), motor_property.name)
    print('List of objects:')
    motor_object = klass.objects
    while motor_object:
        print(' ', motor_object.name)
        motor_object = motor_object.next


if __name__ == '__main__':
    help(Motor.Meta.Class.ClassType.metaclass)
    help(Motor.Meta.Class)
    help(Motor.text)
    help(Motor.DiskFolder)

    sample = Plugin('sample.python')
    c = sample.TestCases.Class(y1=1, x1=3)
    assert c is not None
    c.doStuff(1, 2, True)
    print('%d - %d' % (c.x1, c.y1))
