/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_string.hh>

namespace Motor { namespace Python {

template < typename T >
PyTypeObject::Py2NumberMethods PyMotorString< T >::s_py2StringNumber
    = {{0, 0, 0}, 0, 0, 0, 0, 0, 0, 0, &PyMotorString< T >::nonZero,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0};

template < typename T >
PyTypeObject::Py3NumberMethods PyMotorString< T >::s_py3StringNumber
    = {{0, 0, 0}, 0, 0, 0, 0, 0, 0, &PyMotorString< T >::nonZero,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0};

template < typename T >
PyTypeObject PyMotorString< T >::s_pyType = {
    {{0, 0}, 0},
    istring(minitl::format< 128u >(FMT("py_motor.{0}"), motor_type< T >().metaclass->name)).c_str(),
    sizeof(PyMotorString< T >),
    0,
    &PyMotorString< T >::dealloc,
    0,
    &PyMotorString< T >::getattr,
    &PyMotorString< T >::setattr,
    0,
    &PyMotorString< T >::repr,
    0,
    0,
    0,
    0,
    0,
    &PyMotorString< T >::str,
    0,
    0,
    0,
    Py_TPFLAGS_MOTOR_DEFAULT,
    "Wrapper class for the C++ Motor string types",
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    &PyMotorObject::s_pyType,
    0,
    0,
    0,
    0,
    &PyMotorString< T >::init,
    0,
    &PyMotorString< T >::newinst,
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
PyObject* PyMotorString< T >::stealValue(PyObject* owner, Meta::Value& value)
{
    const T& t = value.as< const T& >();
    motor_forceuse(t);
    motor_assert(value.type().metaclass->type() == Meta::ClassType_String,
                 "PyMotorString only accepts String types");
    motor_assert_format(value.type().metaclass->index() == motor_type< T >().metaclass->index(),
                        "expected {0}; got {1}", motor_type< T >().metaclass->name,
                        value.type().metaclass->name);
    PyObject* result                             = s_pyType.tp_alloc(&s_pyType, 0);
    static_cast< PyMotorString* >(result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }
    new(&(static_cast< PyMotorString* >(result))->value) Meta::Value();
    (static_cast< PyMotorString* >(result))->value.swap(value);
    return result;
}

template < typename T >
int PyMotorString< T >::init(PyObject* self, PyObject* args, PyObject* kwds)
{
    motor_forceuse(kwds);
    PyMotorObject* self_    = static_cast< PyMotorObject* >(self);
    Py_ssize_t     argCount = s_library->m_PyTuple_Size(args);
    if(argCount == 0)
    {
        self_->value = Meta::Value(T(""));
    }
    else if(argCount == 1)
    {
        PyObject* arg = s_library->m_PyTuple_GetItem(args, 0);
        if(arg->py_type == &s_pyType)
        {
            self_->value = static_cast< PyMotorString* >(arg)->value;
        }
        else if(arg->py_type->tp_flags & Py_TPFLAGS_STRING_SUBCLASS)
        {
            const char* value = s_library->m_PyString_AsString(arg);
            self_->value      = Meta::Value(T(value));
        }
        else if(arg->py_type->tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS)
        {
            if(s_library->getVersion() >= 33)
            {
                const char* value = s_library->m_PyUnicode_AsUTF8(arg);
                self_->value      = Meta::Value(T(value));
            }
            else
            {
                PyObject*   decodedUnicode = s_library->m_PyUnicode_AsUTF8String(arg);
                const char* value          = s_library->m_PyBytes_AsString(decodedUnicode);
                self_->value               = Meta::Value(T(value));
                Py_DECREF(decodedUnicode);
            }
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
PyObject* PyMotorString< T >::repr(PyObject* self)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value& v     = self_->value;
    typedef PyObject* (*toStringType)(const char* format, ...);
    toStringType toString = s_library->getVersion() >= 30 ? s_library->m_PyUnicode_FromFormat
                                                          : s_library->m_PyString_FromFormat;
    return toString(
        minitl::format< 1024u >(FMT("[{0} \"{1}\"]"), v.type().name(), v.as< const T& >()));
}

const char* toCharPtr(const istring& t)
{
    return t.c_str();
}

const inamespace::Path toCharPtr(const inamespace& t)
{
    return t.str();
}

const ipath::Filename toCharPtr(const ipath& t)
{
    return t.str();
}

const ifilename::Filename toCharPtr(const ifilename& t)
{
    return t.str();
}

const char* toCharPtr(const text& t)
{
    return t.begin();
}

template < typename T >
PyObject* PyMotorString< T >::str(PyObject* self)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value& v     = self_->value;
    typedef PyObject* (*toStringType)(const char* format);
    toStringType toString = s_library->getVersion() >= 30 ? s_library->m_PyUnicode_FromString
                                                          : s_library->m_PyString_FromString;
    return toString(static_cast< const char* >(toCharPtr(v.as< const T& >())));
}

template < typename T >
bool nonZeroString(const T& t)
{
    return t.size() != 0;
}

template <>
bool nonZeroString< istring >(const istring& t)
{
    return t != istring("");
}

template < typename T >
int PyMotorString< T >::nonZero(PyObject* self)
{
    PyMotorObject*   self_ = static_cast< PyMotorObject* >(self);
    const Meta::Type t     = self_->value.type();
    motor_assert(t.metaclass->type() == Meta::ClassType_String,
                 "PyMotorString expected string value");
    if(t.indirection == Meta::Type::Value)
    {
        return nonZeroString(self_->value.as< const T& >());
    }
    else
    {
        return self_->value.as< const void* const >() != 0;
    }
}

template < typename T >
void PyMotorString< T >::registerType(PyObject* module)
{
    if(s_library->getVersion() >= 30)
        s_pyType.tp_as_number = &s_py3StringNumber.nb_common;
    else
        s_pyType.tp_as_number = &s_py2StringNumber.nb_common;
    s_pyType.tp_alloc = s_library->m_PyType_GenericAlloc;
    int result        = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, motor_type< T >().metaclass->name.c_str(),
                                                (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

template struct PyMotorString< istring >;
template struct PyMotorString< inamespace >;
template struct PyMotorString< ifilename >;
template struct PyMotorString< ipath >;
template struct PyMotorString< text >;

}}  // namespace Motor::Python
