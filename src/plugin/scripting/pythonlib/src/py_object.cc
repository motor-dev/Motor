/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_array.hh>
#include <py_boundmethod.hh>
#include <py_call.hh>
#include <py_class.hh>
#include <py_enum.hh>
#include <py_namespace.hh>
#include <py_number.hh>
#include <py_object.hh>
#include <py_string.hh>

namespace Motor { namespace Python {

PyMethodDef PyMotorObject::s_methods[]
    = {{"__dir__", &PyMotorObject::dir, METH_NOARGS, NULL}, {NULL, NULL, 0, NULL}};

static PyTypeObject::Py2NumberMethods s_py2ObjectNumber
    = {{0, 0, 0}, 0, 0, 0, 0, 0, 0, 0, &PyMotorObject::nonZero,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0, 0,
       0};

static PyTypeObject::Py3NumberMethods s_py3ObjectNumber
    = {{0, 0, 0}, 0, 0, 0, 0, 0, 0, &PyMotorObject::nonZero,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0, 0, 0, 0, 0, 0, 0,
       0,         0};

PyTypeObject PyMotorObject::s_pyType = {{{0, 0}, 0},
                                        "py_motor.Value",
                                        sizeof(PyMotorObject),
                                        0,
                                        &PyMotorObject::dealloc,
                                        0,
                                        &PyMotorObject::getattr,
                                        &PyMotorObject::setattr,
                                        0,
                                        &PyMotorObject::repr,
                                        0,
                                        0,
                                        0,
                                        0,
                                        &PyMotorObject::call,
                                        0,
                                        0,
                                        0,
                                        0,
                                        Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                        "Wrapper class for the C++ class Motor::Meta::Value",
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        PyMotorObject::s_methods,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        0,
                                        &PyMotorObject::newinst,
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

typedef PyObject* (*CreateMethod)(PyObject* owner, Meta::Value& value);

template < typename T >
PyObject* createPyNumeric(PyObject* owner, Meta::Value& value)
{
    motor_forceuse(owner);
    unsigned long long v = static_cast< unsigned long long >(value.as< T >());
    return s_library->m_PyLong_FromUnsignedLongLong(v);
}

template <>
PyObject* createPyNumeric< bool >(PyObject* owner, Meta::Value& value)
{
    motor_forceuse(owner);
    long v = static_cast< long >(value.as< bool >());
    return s_library->m_PyBool_FromLong(v);
}

template <>
PyObject* createPyNumeric< float >(PyObject* owner, Meta::Value& value)
{
    motor_forceuse(owner);
    double v = static_cast< double >(value.as< float >());
    return s_library->m_PyFloat_FromDouble(v);
}

template <>
PyObject* createPyNumeric< double >(PyObject* owner, Meta::Value& value)
{
    motor_forceuse(owner);
    double v = value.as< double >();
    return s_library->m_PyFloat_FromDouble(v);
}

PyObject* createPyString(PyObject* owner, Meta::Value& value)
{
    motor_forceuse(owner);
    const text& t = static_cast< const text& >(value.as< const text& >());
    typedef PyObject* (*toStringType)(const char* format);
    toStringType toString = s_library->getVersion() >= 30 ? s_library->m_PyUnicode_FromString
                                                          : s_library->m_PyString_FromString;
    return toString(t.begin());
}

static CreateMethod s_createPyNumber[]
    = {&createPyNumeric< bool >,  &createPyNumeric< u8 >,    &createPyNumeric< u16 >,
       &createPyNumeric< u32 >,   &createPyNumeric< u64 >,   &createPyNumeric< i8 >,
       &createPyNumeric< i16 >,   &createPyNumeric< i32 >,   &createPyNumeric< i64 >,
       &createPyNumeric< float >, &createPyNumeric< double >};

static CreateMethod s_createNumber[]
    = {&PyMotorNumber< bool >::stealValue,  &PyMotorNumber< u8 >::stealValue,
       &PyMotorNumber< u16 >::stealValue,   &PyMotorNumber< u32 >::stealValue,
       &PyMotorNumber< u64 >::stealValue,   &PyMotorNumber< i8 >::stealValue,
       &PyMotorNumber< i16 >::stealValue,   &PyMotorNumber< i32 >::stealValue,
       &PyMotorNumber< i64 >::stealValue,   &PyMotorNumber< float >::stealValue,
       &PyMotorNumber< double >::stealValue};

static CreateMethod s_createString[]
    = {&PyMotorString< istring >::stealValue, &PyMotorString< inamespace >::stealValue,
       &PyMotorString< ifilename >::stealValue, &PyMotorString< ipath >::stealValue,
       &PyMotorString< text >::stealValue};

PyObject* PyMotorObject::stealValue(PyObject* owner, Meta::Value& value)
{
    const Meta::Type& t = value.type();
    if(!value)
    {
        PyObject* result = s_library->m__Py_NoneStruct;
        Py_INCREF(result);
        return result;
    }
    else if(t.indirection != Meta::Type::Indirection::Value && value.as< const void* const >() == 0)
    {
        PyObject* result = s_library->m__Py_NoneStruct;
        Py_INCREF(result);
        return result;
    }
    else if(t.indirection == Meta::Type::Indirection::Value
            && t.metaclass->type() == Meta::ClassType_Number)
    {
        return s_createPyNumber[t.metaclass->index()](owner, value);
    }
    else if(t.indirection == Meta::Type::Indirection::Value
            && t.metaclass->type() == Meta::ClassType_String
            && t.metaclass->index() == Meta::ClassIndex_text)
    {
        return createPyString(owner, value);
    }
    else
        switch(t.metaclass->type())
        {
        case Meta::ClassType_Number: return s_createNumber[t.metaclass->index()](owner, value);
        case Meta::ClassType_Enum: return PyMotorEnum::stealValue(owner, value);
        case Meta::ClassType_String: return s_createString[t.metaclass->index()](owner, value);
        case Meta::ClassType_Array: return PyMotorArray::stealValue(owner, value);
        case Meta::ClassType_Namespace:
        {
            const Meta::Class& cls = value.as< const Meta::Class& >();
            if(cls.constructor)
            {
                return PyMotorClass::stealValue(owner, value);
            }
            else
            {
                return PyMotorNamespace::stealValue(owner, value);
            }
        }
        default:
        {
            PyObject* result                = s_pyType.tp_alloc(&s_pyType, 0);
            ((PyMotorObject*)result)->owner = owner;
            new(&(static_cast< PyMotorObject* >(result))->value) Meta::Value();
            (static_cast< PyMotorObject* >(result))->value.swap(value);
            if(owner)
            {
                Py_INCREF(owner);
            }
            return result;
        }
        }
}

PyObject* PyMotorObject::newinst(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    motor_forceuse(args);
    motor_forceuse(kwds);
    PyMotorObject* inst = static_cast< PyMotorObject* >(type->tp_alloc(type, 0));
    inst->owner         = 0;
    new(&inst->value) Meta::Value();
    return inst;
}

PyObject* PyMotorObject::getattr(PyObject* self, const char* name)
{
    PyMotorObject*              self_     = static_cast< PyMotorObject* >(self);
    raw< const Meta::Class >    metaclass = self_->value.type().metaclass;
    istring                     name_(name);
    raw< const Meta::Property > p = metaclass->getProperty(name_);
    if(p)
    {
        Meta::Value v = p->get(self_->value);
        return stealValue(self, v);
    }
    raw< const Meta::Method > m = metaclass->getMethod(name_);
    if(m)
    {
        PyObject* result = PyBoundMethod::create(m, self_);
        return result;
    }
    s_library->m_PyErr_Format(
        *s_library->m_PyExc_AttributeError,
        minitl::format<>(FMT("{0} object has no attribute {1}"), self_->value.type(), name));
    return NULL;
}

int PyMotorObject::setattr(PyObject* self, const char* name, PyObject* value)
{
    PyMotorObject* self_ = static_cast< PyMotorObject* >(self);
    if(self_->value.type().access == Meta::Type::Constness::Const)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_TypeError,
            minitl::format<>(FMT("instance of {0} is const"), self_->value.type()));
        return -1;
    }
    raw< const Meta::Property > prop = self_->value.type().metaclass->getProperty(name);
    if(!prop)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_AttributeError,
            minitl::format<>(FMT("{0} object has no attribute {1}"), self_->value.type(), name));
        return -1;
    }
    if(prop->type.access == Meta::Type::Constness::Const)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_TypeError,
            minitl::format<>(FMT("property ({0}).{1} is const"), self_->value.type(), name));
        return -1;
    }
    Meta::ConversionCost c = distance(value, prop->type);
    if(c >= Meta::ConversionCost::s_incompatible)
    {
        s_library->m_PyErr_Format(*s_library->m_PyExc_TypeError,
                                  minitl::format<>(FMT("({0}).{1} is of type {2}"),
                                                   self_->value.type(), name, prop->type));
        return -1;
    }
    Meta::Value* v = (Meta::Value*)malloca(sizeof(Meta::Value));
    unpack(value, prop->type, v);
    prop->set(self_->value, *v);
    v->~Value();
    freea(v);
    return 0;
}

PyObject* PyMotorObject::repr(PyObject* self)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value& v     = self_->value;
    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromString(
            minitl::format<>(FMT("[{0} {1:p}]"), v.type(), &v));
    }
    else
    {
        return s_library->m_PyString_FromString(minitl::format<>(FMT("[{0} {1:p}]"), v.type(), &v));
    }
}

void PyMotorObject::dealloc(PyObject* self)
{
    PyMotorObject* self_ = static_cast< PyMotorObject* >(self);
    if(self_->owner)
    {
        Py_DECREF(self_->owner);
    }
    self_->value.~Value();
    self->py_type->tp_free(self);
}

PyObject* PyMotorObject::call(PyObject* self, PyObject* args, PyObject* kwds)
{
    PyMotorObject*       self_ = static_cast< PyMotorObject* >(self);
    static const istring callName("?call");
    Meta::Value          v(self_->value[callName]);
    if(!v)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_Exception,
            minitl::format<>(FMT("{0} object is not callable"), self_->value.type()));
        return 0;
    }
    else
    {
        raw< const Meta::Method > method = v.as< raw< const Meta::Method > >();
        if(!method)
        {
            s_library->m_PyErr_Format(
                *s_library->m_PyExc_Exception,
                minitl::format<>(FMT("{0} object is not callable"), self_->value.type()));
            return 0;
        }
        return Python::call(method, NULL, args, kwds);
    }
}

int PyMotorObject::nonZero(PyObject* self)
{
    PyMotorObject*   self_ = static_cast< PyMotorObject* >(self);
    const Meta::Type t     = self_->value.type();
    if(t.indirection == Meta::Type::Indirection::Value)
    {
        return 1;
    }
    else
    {
        return self_->value.as< const void* const >() != 0;
    }
}

void PyMotorObject::registerType(PyObject* module)
{
    if(s_library->getVersion() >= 30)
        s_pyType.tp_as_number = &s_py3ObjectNumber.nb_common;
    else
        s_pyType.tp_as_number = &s_py2ObjectNumber.nb_common;
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, "Value", (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);

    PyBoundMethod::registerType(module);
}

static inline void unpackArray(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_assert_format(type.metaclass->type() == Meta::ClassType_Array
                            || type.metaclass->type() == Meta::ClassType_Variant,
                        "expected to unpack Python Array into Meta::ClassType_Array, got {0}",
                        type.metaclass->name);
    motor_unimplemented();
    motor_forceuse(arg);
    motor_forceuse(buffer);
}

static inline void unpackNumber(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_assert_format(type.metaclass->type() == Meta::ClassType_Number
                            || type.metaclass->type() == Meta::ClassType_Variant,
                        "expected to unpack Python Number into Meta::ClassType_Number, got {0}",
                        type.metaclass->name);
    unsigned long long value
        = arg->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS
              ? (unsigned long long)s_library->m_PyInt_AsUnsignedLongMask(arg)
              : (unsigned long long)s_library->m_PyLong_AsUnsignedLongLongMask(arg);
    switch(Meta::ClassIndex_Numeric(type.metaclass->index()))
    {
    case Meta::ClassIndex_bool:
    {
        bool v = value ? true : false;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_u8:
    {
        u8 v = (u8)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_u16:
    {
        u16 v = (u16)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_u32:
    {
        u32 v = (u32)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_u64:
    {
        u64 v = (u64)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_i8:
    {
        i8 v = (i8)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_i16:
    {
        i16 v = (i16)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_i32:
    {
        i32 v = (i32)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_i64:
    {
        i64 v = (i64)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_float:
    {
        float v = (float)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case Meta::ClassIndex_double:
    {
        double v = (double)value;
        new(buffer) Meta::Value(v);
        break;
    }
    default: motor_notreached(); new(buffer) Meta::Value(0);
    }
}

static inline void unpackFloat(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_assert_format(type.metaclass->type() == Meta::ClassType_Number
                            || type.metaclass->type() == Meta::ClassType_Variant,
                        "expected to unpack Python Float into Meta::ClassType_Number, got {0}",
                        type.metaclass->name);
    double value = s_library->m_PyFloat_AsDouble(arg);
    switch(type.metaclass->index())
    {
    case 0:
    {
        bool v = value ? true : false;
        new(buffer) Meta::Value(v);
        break;
    }
    case 1:
    {
        u8 v = (u8)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 2:
    {
        u16 v = (u16)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 3:
    {
        u32 v = (u32)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 4:
    {
        u64 v = (u64)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 5:
    {
        i8 v = (i8)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 6:
    {
        i16 v = (i16)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 7:
    {
        i32 v = (i32)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 8:
    {
        i64 v = (i64)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 9:
    {
        float v = (float)value;
        new(buffer) Meta::Value(v);
        break;
    }
    case 10:
    {
        double v = (double)value;
        new(buffer) Meta::Value(v);
        break;
    }
    default: motor_notreached(); new(buffer) Meta::Value(0);
    }
}

static inline void unpackString(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_assert_format(type.metaclass->type() == Meta::ClassType_String
                            || type.metaclass->type() == Meta::ClassType_Variant,
                        "expected to unpack Python String into Meta::ClassType_String, got {0}",
                        type.metaclass->name);
    char*     string;
    PyObject* decodedUnicode = 0;
    if(arg->py_type->tp_flags & Py_TPFLAGS_UNICODE_SUBCLASS)
    {
        if(s_library->getVersion() >= 33)
        {
            string = s_library->m_PyUnicode_AsUTF8(arg);
        }
        else
        {
            decodedUnicode = s_library->m_PyUnicode_AsASCIIString(arg);
            string         = s_library->m_PyBytes_AsString(decodedUnicode);
        }
    }
    else
    {
        string = s_library->m_PyString_AsString(arg);
    }
    switch(type.metaclass->index())
    {
    case 0: new(buffer) Meta::Value(istring(string)); break;
    case 1: new(buffer) Meta::Value(inamespace(string)); break;
    case 2: new(buffer) Meta::Value(ifilename(string)); break;
    case 3: new(buffer) Meta::Value(ipath(string)); break;
    default: motor_notreached(); new(buffer) Meta::Value();
    }

    if(decodedUnicode)
    {
        Py_DECREF(decodedUnicode);
    }
}

static inline void unpackPod(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_assert_format(type.metaclass->type() == Meta::ClassType_Pod,
                        "expected to unpack Python Dict into Meta::ClassType_Pod, got {0}",
                        type.metaclass->name);

    Meta::Value* result = new(buffer) Meta::Value(type, Meta::Value::Reserve);
    Meta::Value* v      = (Meta::Value*)malloca(sizeof(Meta::Value));
    for(raw< const Meta::Class > c = type.metaclass; c; c = c->parent)
    {
        for(const Meta::Property* p = c->properties.begin(); p != c->properties.end(); ++p)
        {
            PyObject* value = s_library->m_PyDict_GetItemString(arg, p->name.c_str());

            PyMotorObject::unpack(value, p->type, v);
            p->set(*result, *v);
            v->~Value();
        }
    }
    freea(v);
}

Meta::ConversionCost PyMotorObject::distance(PyObject* object, const Meta::Type& desiredType)
{
    if(desiredType.metaclass->type() == Meta::ClassType_Variant)
    {
        if(object->py_type == &PyMotorObject::s_pyType
           || object->py_type->tp_base == &PyMotorObject::s_pyType
           || object->py_type->tp_flags & (Py_TPFLAGS_INT_SUBCLASS | Py_TPFLAGS_LONG_SUBCLASS)
           || object->py_type == s_library->m_PyFloat_Type)
        {
            return Meta::ConversionCost::s_variant;
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type == &PyMotorObject::s_pyType
            || object->py_type->tp_base == &PyMotorObject::s_pyType
            || object->py_type->tp_base->tp_base == &PyMotorObject::s_pyType)
    {
        PyMotorObject* object_ = static_cast< PyMotorObject* >(object);
        return object_->value.type().calculateConversion(desiredType);
    }
    else if(object->py_type == s_library->m_PyBool_Type)
    {
        return Meta::ConversionCalculator< bool >::calculate(desiredType);
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS)
    {
        return Meta::ConversionCalculator< i32 >::calculate(desiredType);
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
    {
        return Meta::ConversionCalculator< i64 >::calculate(desiredType);
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS | Py_TPFLAGS_TUPLE_SUBCLASS))
    {
        if(desiredType.metaclass->type() == Meta::ClassType_Array)
        {
            motor_assert_format(desiredType.metaclass->operators,
                                "Array type {0} does not implement operator methods",
                                desiredType.metaclass->fullname());
            motor_assert_format(desiredType.metaclass->operators->arrayOperators,
                                "Array type {0} does not implement Array API methods",
                                desiredType.metaclass->fullname());
            PyTuple_SizeType    size = object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS)
                                           ? s_library->m_PyList_Size
                                           : s_library->m_PyTuple_Size;
            PyTuple_GetItemType get  = object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS)
                                           ? s_library->m_PyList_GetItem
                                           : s_library->m_PyTuple_GetItem;
            if(size(object) != 0)
            {
                raw< const Meta::ArrayOperatorTable > api
                    = desiredType.metaclass->operators->arrayOperators;
                const Meta::Type& subType     = api->value_type;
                PyObject*         firstObject = get(object, 0);
                return distance(firstObject, subType);
            }
            else
            {
                return Meta::ConversionCost();
            }
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_STRING_SUBCLASS | Py_TPFLAGS_UNICODE_SUBCLASS))
    {
        return desiredType.metaclass->type() == Meta::ClassType_String
                   ? Meta::ConversionCost()
                   : Meta::ConversionCost::s_incompatible;
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_DICT_SUBCLASS)
    {
        if(desiredType.metaclass->type() == Meta::ClassType_Pod)
        {
            u32 i = 0;
            for(raw< const Meta::Class > c = desiredType.metaclass; c; c = c->parent)
            {
                for(const Meta::Property* p = c->properties.begin(); p != c->properties.end(); ++p)
                {
                    PyObject* value = s_library->m_PyDict_GetItemString(object, p->name.c_str());
                    if(!value)
                    {
                        return Meta::ConversionCost::s_incompatible;
                    }
                    if(distance(value, p->type) >= Meta::ConversionCost::s_incompatible)
                    {
                        return Meta::ConversionCost::s_incompatible;
                    }
                }
            }
            return i == (u32)s_library->m_PyDict_Size(object)
                       ? Meta::ConversionCost()
                       : Meta::ConversionCost::s_incompatible;
        }
        else
        {
            motor_unimplemented();
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object == s_library->m__Py_NoneStruct)
    {
        return desiredType.indirection >= Meta::Type::Indirection::RawPtr
                   ? Meta::ConversionCost()
                   : Meta::ConversionCost::s_incompatible;
    }
    else if(object->py_type == s_library->m_PyFloat_Type)
    {
        return Meta::ConversionCalculator< float >::calculate(desiredType);
    }
    else
    {
        return Meta::ConversionCost::s_incompatible;
    }
}

void PyMotorObject::unpack(PyObject* object, const Meta::Type& desiredType, void* buffer)
{
    if(desiredType.metaclass->type() == Meta::ClassType_Variant)
    {
        unpackAny(object, buffer);
    }
    else if(object->py_type == &PyMotorObject::s_pyType
            || object->py_type->tp_base == &PyMotorObject::s_pyType)
    {
        PyMotorObject* object_ = static_cast< PyMotorObject* >(object);
        motor_assert_format(desiredType <= object_->value.type(),
                            "incompatible types: {0} is not compatible with {1}",
                            object_->value.type(), desiredType);
        new(buffer) Meta::Value(Meta::Value::ByRef(object_->value));
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_INT_SUBCLASS | Py_TPFLAGS_LONG_SUBCLASS))
    {
        unpackNumber(object, desiredType, buffer);
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS | Py_TPFLAGS_TUPLE_SUBCLASS))
    {
        unpackArray(object, desiredType, buffer);
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_STRING_SUBCLASS | Py_TPFLAGS_UNICODE_SUBCLASS))
    {
        unpackString(object, desiredType, buffer);
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_DICT_SUBCLASS))
    {
        if(desiredType.metaclass->type() == Meta::ClassType_Pod)
        {
            unpackPod(object, desiredType, buffer);
        }
    }
    else if(object->py_type == s_library->m_PyFloat_Type)
    {
        unpackFloat(object, desiredType, buffer);
    }
    else if(object == s_library->m__Py_NoneStruct)
    {
        void* ptr = 0;
        new(buffer) Meta::Value(desiredType, &ptr);
    }
    else
    {
        motor_notreached();
        new(buffer) Meta::Value();
    }
}

PyObject* PyMotorObject::dir(raw< const Meta::Class > metaclass)
{
    PyObject* result = s_library->m_PyList_New(0);
    if(!result) return NULL;
    PyString_FromStringAndSizeType fromString = s_library->getVersion() >= 30
                                                    ? s_library->m_PyUnicode_FromStringAndSize
                                                    : s_library->m_PyString_FromStringAndSize;

    for(raw< const Meta::ObjectInfo > o = metaclass->objects; o; o = o->next)
    {
        PyObject* str = fromString(o->name.c_str(), o->name.size());
        if(!str)
        {
            Py_DECREF(result);
            return NULL;
        }
        if(s_library->m_PyList_Append(result, str) == -1)
        {
            Py_DECREF(str);
            Py_DECREF(result);
            return NULL;
        }
        Py_DECREF(str);
    }
    for(raw< const Meta::Class > cls = metaclass; cls; cls = cls->parent)
    {
        for(const Meta::Property* p = cls->properties.begin(); p != cls->properties.end(); ++p)
        {
            PyObject* str = fromString(p->name.c_str(), p->name.size());
            if(!str)
            {
                Py_DECREF(result);
                return NULL;
            }
            if(s_library->m_PyList_Append(result, str) == -1)
            {
                Py_DECREF(str);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(str);
        }
        for(const Meta::Method* m = cls->methods.begin(); m != cls->methods.end(); ++m)
        {
            PyObject* str = fromString(m->name.c_str(), m->name.size());
            if(!str)
            {
                Py_DECREF(result);
                return NULL;
            }
            if(s_library->m_PyList_Append(result, str) == -1)
            {
                Py_DECREF(str);
                Py_DECREF(result);
                return NULL;
            }
            Py_DECREF(str);
        }
    }
    return result;
}

PyObject* PyMotorObject::dir(PyObject* self, PyObject* args)
{
    motor_forceuse(args);
    return dir(static_cast< PyMotorObject* >(self)->value.type().metaclass);
}

void PyMotorObject::unpackAny(PyObject* object, void* buffer)
{
    if(object->py_type == &PyMotorObject::s_pyType
       || object->py_type->tp_base == &PyMotorObject::s_pyType)
    {
        PyMotorObject* object_ = static_cast< PyMotorObject* >(object);
        new(buffer) Meta::Value(object_->value);
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS)
    {
        unpackNumber(object, motor_type< i32 >(), buffer);
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
    {
        unpackNumber(object, motor_type< i64 >(), buffer);
    }
    else if(object->py_type == s_library->m_PyFloat_Type)
    {
        unpackFloat(object, motor_type< double >(), buffer);
    }
    else if(object == s_library->m__Py_NoneStruct)
    {
        new(buffer) Meta::Value((const void*)0);
    }
    else
    {
        motor_notreached();
        new(buffer) Meta::Value();
    }
}

}}  // namespace Motor::Python
