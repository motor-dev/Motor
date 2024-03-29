/* Motor <motor.devel@gmail.com>
see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/call.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/value.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_call.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

struct PythonTypeInfo
{
    PyObject*     arg;
    PyTypeObject* pythonType;
    Meta::Type    motorType;

    static Meta::Type    getTypeFromPyObject(PyObject* object);
    static PyTypeObject* getPyTypeFromPyObject(PyObject* object);

    explicit PythonTypeInfo(PyObject* object);
};

Meta::ConversionCost calculateConversionTo(const PythonTypeInfo& typeInfo, const Meta::Type& other)
{
    return PyMotorObject::distance(typeInfo.arg, other);
}

void convert(const PythonTypeInfo& typeInfo, void* buffer, Meta::Type type)
{
    PyMotorObject::unpack(typeInfo.arg, type, buffer);
}

PythonTypeInfo::PythonTypeInfo(PyObject* object)
    : arg(object)
    , pythonType(getPyTypeFromPyObject(object))
    , motorType(getTypeFromPyObject(object))
{
}

Meta::Type PythonTypeInfo::getTypeFromPyObject(PyObject* object)
{
    if(object->py_type == &PyMotorObject::s_pyType)
    {
        auto* o = static_cast< PyMotorObject* >(object);
        return o->value.type();
    }
    else
    {
        return motor_type< void >();
    }
}

PyTypeObject* PythonTypeInfo::getPyTypeFromPyObject(PyObject* object)
{
    if(object->py_type == &PyMotorObject::s_pyType)
    {
        return nullptr;
    }
    else
    {
        return object->py_type;
    }
}

typedef Meta::ArgInfo< PythonTypeInfo > PythonArgInfo;

PyObject* call(raw< const Meta::Method > method, PyObject* self, PyObject* args, PyObject* kwargs)
{
    const bool selfArg      = self != nullptr;
    const u32  selfArgCount = u32(selfArg);
    const u32  unnamedArgCount
        = args ? motor_checked_numcast< u32 >(s_library->m_PyTuple_Size(args)) : 0;
    const u32 namedArgCount
        = kwargs ? motor_checked_numcast< u32 >(s_library->m_PyDict_Size(kwargs)) : 0;
    const u32 argCount = selfArgCount + unnamedArgCount + namedArgCount;
    auto* argInfos = reinterpret_cast< PythonArgInfo* >(malloca(argCount * sizeof(PythonArgInfo)));

    {
        u32 argIndex = 0;
        if(self)
        {
            new(&argInfos[argIndex]) PythonArgInfo(PythonTypeInfo(self));
            argIndex++;
        }
        for(u32 i = 0; i < unnamedArgCount; ++argIndex, ++i)
        {
            new(&argInfos[argIndex])
                PythonArgInfo(PythonTypeInfo(s_library->m_PyTuple_GetItem(args, Py_ssize_t(i))));
        }
        if(kwargs)
        {
            Py_ssize_t pos     = 0;
            PyObject*  key     = nullptr;
            PyObject*  item    = nullptr;
            int        version = s_library->getVersion();
            while(s_library->m_PyDict_Next(kwargs, &pos, &key, &item))
            {
                if(version >= 33)
                {
                    new(&argInfos[argIndex]) PythonArgInfo(
                        istring(s_library->m_PyUnicode_AsUTF8(key)), PythonTypeInfo(item));
                }
                else if(version >= 30)
                {
                    PyObject* bytes = s_library->m_PyUnicode_AsASCIIString(key);
                    if(!bytes)
                    {
                        return nullptr;
                    }
                    const char* name = s_library->m_PyBytes_AsString(bytes);
                    new(&argInfos[argIndex]) PythonArgInfo(istring(name), PythonTypeInfo(item));
                    Py_DECREF(bytes);
                }
                else
                {
                    new(&argInfos[argIndex]) PythonArgInfo(
                        istring(s_library->m_PyString_AsString(key)), PythonTypeInfo(item));
                }
                ++argIndex;
            }
        }
    }

    Meta::CallInfo info = Meta::resolve< PythonTypeInfo >(
        method, {argInfos, selfArgCount + unnamedArgCount},
        {argInfos + selfArgCount + unnamedArgCount, namedArgCount}, selfArg);
    if(info.conversion < Meta::ConversionCost::s_incompatible)
    {
        Meta::Value result = Meta::call< PythonTypeInfo >(
            method, info, {argInfos, selfArgCount + unnamedArgCount},
            {argInfos + selfArgCount + unnamedArgCount, namedArgCount}, selfArg);
        for(u32 i = argCount; i > 0; --i)
        {
            argInfos[i - 1].~PythonArgInfo();
        }
        freea(argInfos);
        return PyMotorObject::stealValue(nullptr, result);
    }
    else
    {
        for(u32 i = argCount; i > 0; --i)
        {
            argInfos[i - 1].~PythonArgInfo();
        }
        freea(argInfos);
        s_library->m_PyErr_Format(*s_library->m_PyExc_TypeError,
                                  "Could not call method %s: "
                                  "no overload could convert all parameters",
                                  method->name.c_str());
        return nullptr;
    }
}

}}  // namespace Motor::Python
