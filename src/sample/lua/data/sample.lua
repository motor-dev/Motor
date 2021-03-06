function name(type)
    local constness = tonumber(type.constness) == 0 and 'const ' or ''
    local access = tonumber(type.access) == 0 and 'const ' or ''
    local ptr
    if type.indirection == 0 then
        return(tostring("%s%s"):format(access, type.metaclass.name))
    else
        if type.indirection == 1 then
            ptr = "raw"
        elseif type.indirection == 2 then
            ptr = "weak"
        elseif type.indirection == 3 then
            ptr = "ref"
        else
            ptr = "???"
        end
        return(tostring("%s%s<%s%s>"):format(constness,
                                   ptr,
                                   access,
                                   type.metaclass.name))
    end
end

function help(klass)
    function print_method(method)
        for i=1, method.overloads:size(), 1 do
            local overload = method.overloads[i]
            local param_list = {}
            for j=1, overload.params:size(), 1 do
                local param = overload.params[j]
                param_list[#param_list+1] = tostring('%s %s'):format(name(param.type), param.name)
            end
            print(tostring('  %s %s (%s)'):format(name(overload.returnType),
                                                  method.name,
                                                  table.concat(param_list, ', ')))
        end
    end

    print(tostring('class %s'):format(klass.name))
    if klass.constructor then
        print('List of constructors:')
        print_method(klass.constructor)
    end
    print('List of methods:')
    for i=1, klass.methods:size(), 1 do
        local method = klass.methods[i]
        print_method(method)
    end
    print('List of properties:')
    for i=1, klass.properties:size(), 1 do
        local property = klass.properties[i]
        print(tostring(' %s %s'):format(name(property.type), property.name))
    end
    print('List of objects:')
    local object = klass.objects
    while object do
        print(tostring(' %s'):format(object.name))
        object = object.next
    end
end

p = plugin('sample.lua')

help(Motor.Meta.Class.ClassType.metaclass)
help(p.LuaTest)

local property = p.LuaTest.properties[1]
help(property.type.metaclass)

tuple = property.type.metaclass(1, 2, 3, 4)
print(tuple)
function print_tuple(tuple)
    print(tuple.__index)
    result = '( '
    for i=1, tuple.__type.metaclass.properties:size(), 1 do
        local property = tuple.__type.metaclass.properties[i]
        result = result .. tostring('%s[%s]:%s '):format(name(property.type), property.name, property:get(tuple))
    end
    result = result .. ')'
    print(result)
end

print_tuple(tuple)
tuple._0 = 5
tuple._2 = 7
print_tuple(tuple)

