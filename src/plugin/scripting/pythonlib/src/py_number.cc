/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_number.hh>

namespace Motor { namespace Python {

template < typename T >
PyTypeObject::Py2NumberMethods PyMotorNumber< T >::s_py2NumberNumber
    = {{0, 0, 0},
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::nonZero,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::toint,
       &PyMotorNumber< T >::tolong,
       &PyMotorNumber< T >::tofloat,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0};

template < typename T >
PyTypeObject::Py3NumberMethods PyMotorNumber< T >::s_py3NumberNumber
    = {{0, 0, 0},
       0,
       0,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::nonZero,
       0,
       0,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::tolong,
       0,
       &PyMotorNumber< T >::tofloat,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0};

template < typename T >
PyTypeObject PyMotorNumber< T >::s_pyType
    = {{{0, 0}, 0},
       istring(minitl::format< 128u >("py_motor.%s") | motor_type< T >().metaclass->name).c_str(),
       sizeof(PyMotorNumber< T >),
       0,
       &PyMotorNumber< T >::dealloc,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::repr,
       0,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::str,
       0,
       0,
       0,
       Py_TPFLAGS_MOTOR_DEFAULT,
       "Wrapper class for the C++ Motor number types",
       0,
       0,
       0,
       0,
       0,
       0,
       PyMotorObject::s_methods,
       0,
       0,
       &PyMotorObject::s_pyType,
       0,
       0,
       0,
       0,
       &PyMotorNumber< T >::init,
       0,
       &PyMotorNumber< T >::newinst,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0,
       0};

template < typename T >
PyObject* PyMotorNumber< T >::stealValue(PyObject* owner, Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Number,
                 "PyMotorNumber only accepts Number types");
    motor_assert(value.type().metaclass->index() == motor_type< T >().metaclass->index(),
                 "expected %s; got %s" | motor_type< T >().metaclass->name
                     | value.type().metaclass->name);
    PyObject* result                             = s_pyType.tp_alloc(&s_pyType, 0);
    static_cast< PyMotorNumber* >(result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }
    new(&(static_cast< PyMotorNumber* >(result))->value) Meta::Value();
    (static_cast< PyMotorNumber* >(result))->value.swap(value);
    return result;
}

template < typename T >
int PyMotorNumber< T >::init(PyObject* self, PyObject* args, PyObject* kwds)
{
    motor_forceuse(kwds);
    PyMotorObject* self_    = static_cast< PyMotorObject* >(self);
    Py_ssize_t     argCount = s_library->m_PyTuple_Size(args);
    if(argCount == 0)
    {
        self_->value = Meta::Value(T());
    }
    else if(argCount == 1)
    {
        PyObject* arg = s_library->m_PyTuple_GetItem(args, 0);
        if(arg->py_type == &s_pyType)
        {
            self_->value = static_cast< PyMotorNumber* >(arg)->value;
        }
        else if(arg->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS)
        {
            unsigned long value = s_library->m_PyInt_AsUnsignedLongMask(arg);
            self_->value        = Meta::Value(T(value));
        }
        else if(arg->py_type->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
        {
            unsigned long long value = s_library->m_PyLong_AsUnsignedLongLongMask(arg);
            self_->value             = Meta::Value(T(value));
        }
        else
        {
            s_library->m_PyErr_Format(*s_library->m_PyExc_TypeError, "Cannot convert from %s to %s",
                                      arg->py_type->tp_name,
                                      motor_type< T >().metaclass->name.c_str());
            return -1;
        }
    }
    return 0;
}

template < typename T >
PyObject* PyMotorNumber< T >::repr(PyObject* self)
{
    PyMotorObject*          self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value&      v     = self_->value;
    minitl::format< 1024u > format
        = minitl::format< 1024u >("[%s %d]") | v.type().name().c_str() | v.as< const T >();
    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromFormat(format);
    }
    else
    {
        return s_library->m_PyString_FromFormat(format);
    }
}

template < typename T >
PyObject* PyMotorNumber< T >::toint(PyObject* self)
{
    PyMotorObject* self_ = static_cast< PyMotorObject* >(self);
    long           value = (long)self_->value.as< const T >();
    return s_library->m_PyInt_FromLong(value);
}

template < typename T >
PyObject* PyMotorNumber< T >::tolong(PyObject* self)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    unsigned long long value = (unsigned long long)self_->value.as< const T >();
    return s_library->m_PyLong_FromUnsignedLongLong(value);
}

template < typename T >
PyObject* PyMotorNumber< T >::tofloat(PyObject* self)
{
    PyMotorObject* self_ = static_cast< PyMotorObject* >(self);
    double         value = (double)self_->value.as< const T >();
    return s_library->m_PyFloat_FromDouble(value);
}

template < typename T >
PyObject* PyMotorNumber< T >::str(PyObject* self)
{
    PyMotorObject*     self_                       = static_cast< PyMotorObject* >(self);
    const Meta::Value& v                           = self_->value;
    PyObject* (*tostring)(const char* format, ...) = s_library->getVersion() >= 30
                                                         ? s_library->m_PyUnicode_FromFormat
                                                         : s_library->m_PyString_FromFormat;
    return tostring(minitl::format< 1024u >("%d") | v.as< const T >());
}

template < typename T >
int PyMotorNumber< T >::nonZero(PyObject* self)
{
    PyMotorNumber*   self_ = static_cast< PyMotorNumber* >(self);
    const Meta::Type t     = self_->value.type();
    motor_assert(t.metaclass->type() == Meta::ClassType_Number,
                 "PyMotorNumber expected number value");
    if(t.indirection == Meta::Type::Value)
    {
        return self_->value.template as< const T >() != 0;
    }
    else
    {
        return self_->value.template as< const void* const >() != 0;
    }
}

template < typename T >
void PyMotorNumber< T >::registerType(PyObject* module)
{
    if(s_library->getVersion() >= 30)
        s_pyType.tp_as_number = &s_py3NumberNumber.nb_common;
    else
        s_pyType.tp_as_number = &s_py2NumberNumber.nb_common;
    s_pyType.tp_alloc = s_library->m_PyType_GenericAlloc;
    int result        = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, motor_type< T >().metaclass->name.c_str(),
                                                (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

template struct PyMotorNumber< bool >;
template struct PyMotorNumber< u8 >;
template struct PyMotorNumber< u16 >;
template struct PyMotorNumber< u32 >;
template struct PyMotorNumber< u64 >;
template struct PyMotorNumber< i8 >;
template struct PyMotorNumber< i16 >;
template struct PyMotorNumber< i32 >;
template struct PyMotorNumber< i64 >;
template struct PyMotorNumber< float >;
template struct PyMotorNumber< double >;

}}  // namespace Motor::Python
