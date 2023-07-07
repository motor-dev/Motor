/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/engine/call.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_array.hh>

namespace Motor { namespace Python {

static PyTypeObject::Py2NumberMethods s_py2ArrayNumber = {{nullptr, nullptr, nullptr},
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          &PyMotorArray::nonZero,
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

static PyTypeObject::Py3NumberMethods s_py3ArrayNumber = {{nullptr, nullptr, nullptr},
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          nullptr,
                                                          &PyMotorArray::nonZero,
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

static PyTypeObject::PySequenceMethods s_pyArraySequence = {&PyMotorArray::length,
                                                            nullptr,
                                                            nullptr,
                                                            &PyMotorArray::item,
                                                            nullptr,
                                                            &PyMotorArray::setItem,
                                                            nullptr,
                                                            nullptr,
                                                            nullptr,
                                                            nullptr};

PyTypeObject PyMotorArray::s_pyType = {{{0, nullptr}, 0},
                                       "py_motor.Array",
                                       sizeof(PyMotorArray),
                                       0,
                                       &PyMotorArray::dealloc,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       &PyMotorArray::repr,
                                       nullptr,
                                       &s_pyArraySequence,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                       "Wrapper class for the C++ Motor array types",
                                       nullptr,
                                       nullptr,
                                       nullptr,
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

PyObject* PyMotorArray::stealValue(PyObject* owner, Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Array,
                 "PyMotorArray only accepts Array types");
    auto* result    = static_cast< PyMotorArray* >(s_pyType.tp_alloc(&s_pyType, 0));
    (result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }

    raw< const Meta::Class > arrayClass = value.type().metaclass;
    new(&(static_cast< PyMotorArray* >(result))->value) Meta::Value();
    (static_cast< PyMotorArray* >(result))->value.swap(value);
    motor_assert_format(arrayClass->operators, "Array type {0} does not implement operator methods",
                        arrayClass->name);
    motor_assert_format(arrayClass->operators->arrayOperators,
                        "Array type {0} does not implement Array API methods", arrayClass->name);
    motor_forceuse(arrayClass);
    return result;
}

PyObject* PyMotorArray::repr(PyObject* self)
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
        return s_library->m_PyString_FromFormat(minitl::format<>(FMT("[{0} {1:p}]"), v.type(), &v));
    }
}

int PyMotorArray::nonZero(PyObject* self)
{
    return length(self) > 0;
}

Py_ssize_t PyMotorArray::length(PyObject* self)
{
    auto*            self_ = static_cast< PyMotorArray* >(self);
    const Meta::Type t     = self_->value.type();
    motor_assert(t.metaclass->type() == Meta::ClassType_Array, "PyMotorArray expected array value");
    return Py_ssize_t(t.metaclass->operators->arrayOperators->size(self_->value));
}

PyObject* PyMotorArray::item(PyObject* self, Py_ssize_t index)
{
    auto* self_ = static_cast< PyMotorArray* >(self);
    if(index >= 0 && index < length(self))
    {
        u32              index_ = motor_checked_numcast< u32 >(index);
        const Meta::Type t      = self_->value.type();
        Meta::Value      v
            = t.isConst() ? t.metaclass->operators->arrayOperators->indexConst(self_->value, index_)
                          : t.metaclass->operators->arrayOperators->index(self_->value, index_);
        return PyMotorObject::stealValue(nullptr, v);
    }
    else
    {
        s_library->m_PyErr_Format(*s_library->m_PyExc_IndexError, "Index out of range");
        return nullptr;
    }
}

int PyMotorArray::setItem(PyObject* self, Py_ssize_t index, PyObject* value)
{
    auto*                                 self_    = static_cast< PyMotorArray* >(self);
    const Meta::Type                      t        = self_->value.type();
    raw< const Meta::ArrayOperatorTable > arrayApi = t.metaclass->operators->arrayOperators;
    if(t.isConst())
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_TypeError,
            minitl::format< 1024 >(FMT("instance of {0} is const"), self_->value.type()));
        return -1;
    }
    else if(distance(value, arrayApi->value_type) >= Meta::ConversionCost::s_incompatible)
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_TypeError,
            minitl::format< 1024 >(FMT("Cannot convert to array value_type {0}"),
                                   arrayApi->value_type));
        return -1;
    }
    else
    {
        u32   index_ = motor_checked_numcast< u32 >(index);
        auto* v      = (Meta::Value*)malloca(sizeof(Meta::Value));
        PyMotorObject::unpack(value, arrayApi->value_type, v);
        arrayApi->index(self_->value, index_) = *v;
        v->~Value();
        freea(v);
        return 0;
    }
}

void PyMotorArray::registerType(PyObject* module)
{
    if(s_library->getVersion() >= 30)
        s_pyType.tp_as_number = &s_py3ArrayNumber.nb_common;
    else
        s_pyType.tp_as_number = &s_py2ArrayNumber.nb_common;
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, "Array", (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
