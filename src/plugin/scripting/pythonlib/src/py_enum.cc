/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_enum.hh>
#include <py_number.hh>

namespace Motor { namespace Python {

PyTypeObject::Py2NumberMethods PyMotorEnum::s_py2EnumNumber = {{nullptr, nullptr, nullptr},
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               &PyMotorEnum::nonZero,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               &PyMotorEnum::toint,
                                                               &PyMotorEnum::tolong,
                                                               &PyMotorEnum::tofloat,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr};

PyTypeObject::Py3NumberMethods PyMotorEnum::s_py3EnumNumber = {{nullptr, nullptr, nullptr},
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               &PyMotorEnum::nonZero,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               &PyMotorEnum::tolong,
                                                               nullptr,
                                                               &PyMotorEnum::tofloat,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr,
                                                               nullptr};

PyTypeObject PyMotorEnum::s_pyType = {{{0, nullptr}, 0},
                                      "py_motor.Enum",
                                      sizeof(PyMotorEnum),
                                      0,
                                      PyMotorEnum::dealloc,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      &PyMotorEnum::str,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      &PyMotorEnum::str,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                      "Wrapper class for the C++ Motor Enum types",
                                      nullptr,
                                      nullptr,
                                      &PyMotorEnum::cmp,
                                      0,
                                      nullptr,
                                      nullptr,
                                      PyMotorObject::s_methods,
                                      nullptr,
                                      nullptr,
                                      PyMotorObject::s_pyTypePtr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      0,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      nullptr,
                                      0,
                                      nullptr,
                                      nullptr};

PyObject* PyMotorEnum::stealValue(PyObject* owner, Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Enum,
                 "PyMotorNumber only accepts Enum types");
    PyObject* result                           = s_pyType.tp_alloc(&s_pyType, 0);
    static_cast< PyMotorEnum* >(result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }
    new(&(static_cast< PyMotorEnum* >(result))->value) Meta::Value();
    (static_cast< PyMotorEnum* >(result))->value.swap(value);
    return result;
}

static istring s_toString = istring("toString");
static istring s_toInt    = istring("toInt");

PyObject* PyMotorEnum::str(PyObject* self)
{
    auto*              self_    = static_cast< PyMotorEnum* >(self);
    const Meta::Value& v        = self_->value;
    auto               toString = self_->value[s_toString].as< raw< const Meta::Method > >();
    minitl::format_buffer< 1024u > format = minitl::format< 1024u >(
        FMT("{0}.{1}"), v.type(), toString->doCall(&self_->value, 1).as< const istring >());
    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromFormat(format);
    }
    else
    {
        return s_library->m_PyString_FromFormat(format);
    }
}

PyObject* PyMotorEnum::cmp(PyObject* self, PyObject* other, int operation)
{
    auto* self_ = static_cast< PyMotorEnum* >(self);
    auto  toInt = self_->value[s_toInt].as< raw< const Meta::Method > >();
    i64   value = toInt->doCall(&self_->value, 1).as< u32 >();
    i64   otherValue;

    if(other->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS)
    {
        otherValue = (i64)s_library->m_PyInt_AsUnsignedLongMask(other);
    }
    else if(other->py_type->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
    {
        otherValue = (i64)s_library->m_PyLong_AsUnsignedLongLongMask(other);
    }
    else if(other->py_type == &PyMotorObject::s_pyType
            || other->py_type->tp_base == &PyMotorObject::s_pyType)
    {
        auto* other_ = static_cast< PyMotorObject* >(other);
        if(other->py_type == &PyMotorEnum::s_pyType)
        {
            if(other_->value.type().metaclass != self_->value.type().metaclass)
            {
                s_library->m_PyErr_Format(
                    *s_library->m_PyExc_TypeError,
                    minitl::format<>(
                        FMT("cannot compare value of enum type {0} with value of enum type {1}"),
                        self_->value.type().metaclass->name, other_->value.type().metaclass->name));
                return nullptr;
            }
            else
            {
                otherValue = toInt->doCall(&other_->value, 1).as< u32 >();
            }
        }
        else if(other->py_type == &PyMotorNumber< i8 >::s_pyType)
        {
            otherValue = other_->value.as< i8 >();  // NOLINT
        }
        else if(other->py_type == &PyMotorNumber< i16 >::s_pyType)
        {
            otherValue = other_->value.as< i16 >();
        }
        else if(other->py_type == &PyMotorNumber< i32 >::s_pyType)
        {
            otherValue = other_->value.as< i32 >();
        }
        else if(other->py_type == &PyMotorNumber< i64 >::s_pyType)
        {
            otherValue = other_->value.as< i64 >();
        }
        else if(other->py_type == &PyMotorNumber< u8 >::s_pyType)
        {
            otherValue = other_->value.as< u8 >();
        }
        else if(other->py_type == &PyMotorNumber< u16 >::s_pyType)
        {
            otherValue = other_->value.as< u16 >();
        }
        else if(other->py_type == &PyMotorNumber< u32 >::s_pyType)
        {
            otherValue = other_->value.as< u32 >();
        }
        else if(other->py_type == &PyMotorNumber< u64 >::s_pyType)
        {
            otherValue = i64(other_->value.as< u64 >());
        }
        else
        {
            s_library->m_PyErr_Format(
                *s_library->m_PyExc_TypeError,
                minitl::format<>(
                    FMT("cannot compare value of enum type {0} with value of type {1}"),
                    self_->value.type().metaclass->name, other_->value.type().metaclass->name));
            return nullptr;
        }
    }
    else
    {
        PyObject* result = s_library->m__Py_NotImplementedStruct;
        Py_INCREF(result);
        return result;
    }
    PyObject* result;
    switch(operation)
    {
    case PythonLibrary::Py_LT:
        result = value < otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    case PythonLibrary::Py_LE:
        result = value <= otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    case PythonLibrary::Py_EQ:
        result = value == otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    case PythonLibrary::Py_NE:
        result = value != otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    case PythonLibrary::Py_GT:
        result = value > otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    case PythonLibrary::Py_GE:
        result = value >= otherValue ? s_library->m__Py_TrueStruct : s_library->m__Py_FalseStruct;
        break;
    default: result = s_library->m__Py_NotImplementedStruct; break;
    }
    Py_INCREF(result);
    return result;
}

PyObject* PyMotorEnum::toint(PyObject* self)
{
    auto* self_ = static_cast< PyMotorObject* >(self);
    auto  toInt = self_->value[s_toInt].as< raw< const Meta::Method > >();
    long  value = (long)toInt->doCall(&self_->value, 1).as< u32 >();
    return s_library->m_PyInt_FromLong(value);
}

PyObject* PyMotorEnum::tolong(PyObject* self)
{
    auto*              self_ = static_cast< PyMotorObject* >(self);
    auto               toInt = self_->value[s_toInt].as< raw< const Meta::Method > >();
    unsigned long long value = (unsigned long long)toInt->doCall(&self_->value, 1).as< u32 >();
    return s_library->m_PyLong_FromUnsignedLongLong(value);
}

PyObject* PyMotorEnum::tofloat(PyObject* self)
{
    auto*  self_ = static_cast< PyMotorObject* >(self);
    auto   toInt = self_->value[s_toInt].as< raw< const Meta::Method > >();
    double value = (double)toInt->doCall(&self_->value, 1).as< u32 >();
    return s_library->m_PyFloat_FromDouble(value);
}

int PyMotorEnum::nonZero(PyObject* self)
{
    auto* self_ = static_cast< PyMotorObject* >(self);
    auto  toInt = self_->value[s_toInt].as< raw< const Meta::Method > >();
    return toInt->doCall(&self_->value, 1).as< u32 >() != 0;
}

void PyMotorEnum::registerType(PyObject* module)
{
    if(s_library->getVersion() >= 30)
        s_pyType.tp_as_number = &s_py3EnumNumber.nb_common;
    else
        s_pyType.tp_as_number = &s_py2EnumNumber.nb_common;
    s_pyType.tp_alloc = s_library->m_PyType_GenericAlloc;
    int result        = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(module);
    motor_forceuse(result);
    Py_INCREF(&s_pyType);
}
}}  // namespace Motor::Python
