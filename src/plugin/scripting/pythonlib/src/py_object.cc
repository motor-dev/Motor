/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/class.meta.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/method.meta.hh>
#include <motor/meta/property.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_boundmethod.hh>
#include <py_call.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

PyMethodDef PyMotorObject::s_methodArray[]
    = {{"__dir__", &PyMotorObject::dir, METH_NOARGS, nullptr}, {nullptr, nullptr, 0, nullptr}};

static PyTypeObject::Py2NumberMethods s_py2ObjectNumber = {{nullptr, nullptr, nullptr},
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           &PyMotorObject::nonZero,
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

static PyTypeObject::Py3NumberMethods s_py3ObjectNumber = {{nullptr, nullptr, nullptr},
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           &PyMotorObject::nonZero,
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
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr,
                                                           nullptr};

PyTypeObject PyMotorObject::s_pyType = {{{0, nullptr}, 0},
                                        "py_motor.Value",
                                        sizeof(PyMotorObject),
                                        0,
                                        &PyMotorObject::dealloc,
                                        nullptr,
                                        &PyMotorObject::getattr,
                                        &PyMotorObject::setattr,
                                        nullptr,
                                        &PyMotorObject::repr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        &PyMotorObject::call,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                        "Wrapper class for the C++ class Motor::Meta::Value",
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        0,
                                        nullptr,
                                        nullptr,
                                        PyMotorObject::s_methods,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        0,
                                        nullptr,
                                        nullptr,
                                        &PyMotorObject::newinst,
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

typedef PyObject* (*CreateMethod)(PyObject* owner, Meta::Value& value);

PyObject* PyMotorObject::stealValue(PyObject* owner, Meta::Value& value)
{
    const Meta::Type& t = value.type();
    if(!value)
    {
        PyObject* result = s_library->m__Py_NoneStruct;
        Py_INCREF(result);
        return result;
    }
    else if(t.indirection != Meta::Type::Indirection::Value
            && value.as< const void* const >() == nullptr)
    {
        PyObject* result = s_library->m__Py_NoneStruct;
        Py_INCREF(result);
        return result;
    }
    else
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

PyObject* PyMotorObject::newinst(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    motor_forceuse(args);
    motor_forceuse(kwds);
    auto* inst  = static_cast< PyMotorObject* >(type->tp_alloc(type, 0));
    inst->owner = nullptr;
    new(&inst->value) Meta::Value();
    return inst;
}

PyObject* PyMotorObject::getattr(PyObject* self, const char* name)
{
    auto*                       self_     = static_cast< PyMotorObject* >(self);
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
    return nullptr;
}

int PyMotorObject::setattr(PyObject* self, const char* name, PyObject* value)
{
    auto* self_ = static_cast< PyMotorObject* >(self);
    if(self_->value.type().access == Meta::Type::Constness::Const)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_TypeError,
            minitl::format<>(FMT("instance of {0} is const"), self_->value.type()));
        return -1;
    }
    raw< const Meta::Property > prop = self_->value.type().metaclass->getProperty(istring(name));
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
    auto* v = (Meta::Value*)malloca(sizeof(Meta::Value));
    unpack(value, prop->type, v);
    prop->set(self_->value, *v);
    v->~Value();
    freea(v);
    return 0;
}

PyObject* PyMotorObject::repr(PyObject* self)
{
    auto*              self_ = static_cast< PyMotorObject* >(self);
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
    auto* self_ = static_cast< PyMotorObject* >(self);
    if(self_->owner)
    {
        Py_DECREF(self_->owner);
    }
    self_->value.~Value();
    self->py_type->tp_free(self);
}

PyObject* PyMotorObject::call(PyObject* self, PyObject* args, PyObject* kwds)
{
    auto*                self_ = static_cast< PyMotorObject* >(self);
    static const istring callName("?call");
    Meta::Value          v(self_->value[callName]);
    if(!v)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_Exception,
            minitl::format<>(FMT("{0} object is not callable"), self_->value.type()));
        return nullptr;
    }
    else
    {
        auto method = v.as< raw< const Meta::Method > >();
        if(!method)
        {
            s_library->m_PyErr_Format(
                *s_library->m_PyExc_Exception,
                minitl::format<>(FMT("{0} object is not callable"), self_->value.type()));
            return nullptr;
        }
        return Python::call(method, nullptr, args, kwds);
    }
}

int PyMotorObject::nonZero(PyObject* self)
{
    auto*            self_ = static_cast< PyMotorObject* >(self);
    const Meta::Type t     = self_->value.type();
    if(t.indirection == Meta::Type::Indirection::Value)
    {
        return 1;
    }
    else
    {
        return self_->value.as< const void* const >() != nullptr;
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
    motor_unimplemented();
    motor_forceuse(arg);
    motor_forceuse(type);
    motor_forceuse(buffer);
}

static inline void unpackNumber(PyObject* arg, const Meta::Type& type, void* buffer)
{
    unsigned long long value
        = arg->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS
              ? (unsigned long long)s_library->m_PyInt_AsUnsignedLongMask(arg)
              : (unsigned long long)s_library->m_PyLong_AsUnsignedLongLongMask(arg);
    raw< const Meta::InterfaceTable > interfaces = type.metaclass->interfaces;
    if(interfaces->i64Interface)
        new(buffer) Meta::Value(interfaces->i64Interface->construct(i64(value)));
    else if(interfaces->u64Interface)
        new(buffer) Meta::Value(interfaces->u64Interface->construct(u64(value)));
    else if(interfaces->doubleInterface)
        new(buffer) Meta::Value(interfaces->doubleInterface->construct(double(value)));
    else if(interfaces->floatInterface)
        new(buffer) Meta::Value(interfaces->floatInterface->construct(float(value)));
    else
        motor_notreached();
}

static inline void unpackFloat(PyObject* arg, const Meta::Type& type, void* buffer)
{
    double                            value      = s_library->m_PyFloat_AsDouble(arg);
    raw< const Meta::InterfaceTable > interfaces = type.metaclass->interfaces;
    if(interfaces->doubleInterface)
        new(buffer) Meta::Value(interfaces->doubleInterface->construct(double(value)));
    else if(interfaces->floatInterface)
        new(buffer) Meta::Value(interfaces->floatInterface->construct(float(value)));
    else if(interfaces->i64Interface)
        new(buffer) Meta::Value(interfaces->i64Interface->construct(i64(value)));
    else if(interfaces->u64Interface)
        new(buffer) Meta::Value(interfaces->u64Interface->construct(u64(value)));
    else
        motor_notreached();
}

static inline void unpackString(PyObject* arg, const Meta::Type& type, void* buffer)
{
    char*     string;
    PyObject* decodedUnicode = nullptr;
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
    raw< const Meta::InterfaceTable::TypeInterface< const char* > > charpInterface
        = type.metaclass->interfaces->charpInterface;
    motor_assert_format(charpInterface != nullptr, "type {0} is missing the string interface",
                        type);
    new(buffer) Meta::Value(charpInterface->construct(string));

    if(decodedUnicode)
    {
        Py_DECREF(decodedUnicode);
    }
}

static inline void unpackMap(PyObject* arg, const Meta::Type& type, void* buffer)
{
    motor_unimplemented();
    motor_forceuse(arg);
    motor_forceuse(type);
    motor_forceuse(buffer);
}

Meta::ConversionCost PyMotorObject::distance(PyObject* object, const Meta::Type& desiredType)
{
    raw< const Meta::InterfaceTable > interfaces = desiredType.metaclass->interfaces;
    if(interfaces->variantInterface)
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
        auto* object_ = static_cast< PyMotorObject* >(object);
        return object_->value.type().calculateConversionTo(desiredType);
    }
    else if(object->py_type == s_library->m_PyBool_Type)
    {
        if(interfaces->boolInterface)
        {
            return Meta::ConversionCost();
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_INT_SUBCLASS)
    {
        if(interfaces->i64Interface != nullptr || interfaces->u64Interface != nullptr)
        {
            return Meta::ConversionCost();
        }
        else if(interfaces->floatInterface != nullptr || interfaces->doubleInterface != nullptr)
        {
            return Meta::ConversionCost(0, 1);
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_LONG_SUBCLASS)
    {
        if(interfaces->i64Interface != nullptr || interfaces->u64Interface != nullptr)
        {
            return Meta::ConversionCost();
        }
        else if(interfaces->floatInterface != nullptr || interfaces->doubleInterface != nullptr)
        {
            return Meta::ConversionCost(0, 1);
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS | Py_TPFLAGS_TUPLE_SUBCLASS))
    {
        if(interfaces->arrayInterface)
        {
            Type_PyTuple_Size    size = object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS)
                                            ? s_library->m_PyList_Size
                                            : s_library->m_PyTuple_Size;
            Type_PyTuple_GetItem get  = object->py_type->tp_flags & (Py_TPFLAGS_LIST_SUBCLASS)
                                            ? s_library->m_PyList_GetItem
                                            : s_library->m_PyTuple_GetItem;
            if(size(object) != 0)
            {
                const Meta::Type& subType     = interfaces->arrayInterface->valueType;
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
        if(interfaces->charpInterface)
        {
            return Meta::ConversionCost();
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else if(object->py_type->tp_flags & Py_TPFLAGS_DICT_SUBCLASS)
    {
        if(interfaces->mapInterface)
        {
            return Meta::ConversionCost();
        }
        else
        {
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
        if(interfaces->floatInterface != nullptr || interfaces->doubleInterface != nullptr)
        {
            return Meta::ConversionCost();
        }
        else if(interfaces->i64Interface != nullptr || interfaces->u64Interface != nullptr)
        {
            return Meta::ConversionCost(0, 1);
        }
        else
        {
            return Meta::ConversionCost::s_incompatible;
        }
    }
    else
    {
        return Meta::ConversionCost::s_incompatible;
    }
}

void PyMotorObject::unpack(PyObject* object, const Meta::Type& desiredType, void* buffer)
{
    if(desiredType.metaclass->interfaces->variantInterface)
    {
        unpackAny(object, buffer);
    }
    else if(object->py_type == &PyMotorObject::s_pyType
            || object->py_type->tp_base == &PyMotorObject::s_pyType)
    {
        auto* object_ = static_cast< PyMotorObject* >(object);
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
        unpackMap(object, desiredType, buffer);
    }
    else if(object->py_type == s_library->m_PyFloat_Type)
    {
        unpackFloat(object, desiredType, buffer);
    }
    else if(object == s_library->m__Py_NoneStruct)
    {
        void* ptr = nullptr;
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
    if(!result) return nullptr;
    Type_PyString_FromStringAndSize fromString = s_library->getVersion() >= 30
                                                     ? s_library->m_PyUnicode_FromStringAndSize
                                                     : s_library->m_PyString_FromStringAndSize;

    for(raw< const Meta::Object > o = metaclass->objects; o; o = o->next)
    {
        PyObject* str = fromString(o->name.c_str(), Py_ssize_t(o->name.size()));
        if(!str)
        {
            Py_DECREF(result);
            return nullptr;
        }
        if(s_library->m_PyList_Append(result, str) == -1)
        {
            Py_DECREF(str);
            Py_DECREF(result);
            return nullptr;
        }
        Py_DECREF(str);
    }
    for(raw< const Meta::Class > cls = metaclass; cls; cls = cls->base)
    {
        for(raw< const Meta::Property > property = cls->properties; property;
            property                             = property->next)
        {
            PyObject* str = fromString(property->name.c_str(), Py_ssize_t(property->name.size()));
            if(!str)
            {
                Py_DECREF(result);
                return nullptr;
            }
            if(s_library->m_PyList_Append(result, str) == -1)
            {
                Py_DECREF(str);
                Py_DECREF(result);
                return nullptr;
            }
            Py_DECREF(str);
        }

        for(raw< const Meta::Method > method = cls->methods; method; method = method->next)
        {
            PyObject* str = fromString(method->name.c_str(), Py_ssize_t(method->name.size()));
            if(!str)
            {
                Py_DECREF(result);
                return nullptr;
            }
            if(s_library->m_PyList_Append(result, str) == -1)
            {
                Py_DECREF(str);
                Py_DECREF(result);
                return nullptr;
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
        auto* object_ = static_cast< PyMotorObject* >(object);
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
        new(buffer) Meta::Value((const void*)nullptr);
    }
    else
    {
        motor_notreached();
        new(buffer) Meta::Value();
    }
}

}}  // namespace Motor::Python
