/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/method.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_boundmethod.hh>
#include <py_call.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

PyTypeObject PyBoundMethod::s_pyType = {{{0, nullptr}, 0},
                                        "py_motor.BoundMethod",
                                        sizeof(PyBoundMethod),
                                        0,
                                        &PyBoundMethod::dealloc,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        &PyBoundMethod::repr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        &PyBoundMethod::call,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        nullptr,
                                        Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                        "Wrapper class for bound methods to C++ methods",
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

PyObject* PyBoundMethod::create(raw< const Meta::Method > method, PyMotorObject* value)
{
    auto* result   = reinterpret_cast< PyBoundMethod* >(s_pyType.tp_alloc(&s_pyType, 0));
    result->method = method;
    result->value  = static_cast< PyObject* >(value);
    Py_INCREF(result->value);
    return reinterpret_cast< PyObject* >(result);
}

PyObject* PyBoundMethod::repr(PyObject* self)
{
    auto* self_ = reinterpret_cast< PyBoundMethod* >(self);
    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromFormat("[BoundMethod %p.%s]", self_,
                                                 self_->method->name.c_str());
    }
    else
    {
        return s_library->m_PyString_FromFormat("[BoundMethod %p.%s]", self_,
                                                self_->method->name.c_str());
    }
}

void PyBoundMethod::dealloc(PyObject* self)
{
    auto* self_ = reinterpret_cast< PyBoundMethod* >(self);
    Py_DECREF(self_->value);
    self->py_type->tp_free(self);
}

PyObject* PyBoundMethod::call(PyObject* self, PyObject* args, PyObject* kwds)
{
    auto* self_ = reinterpret_cast< PyBoundMethod* >(self);
    return Python::call(self_->method, self_->value, args, kwds);
}

void PyBoundMethod::registerType(PyObject* module)
{
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, "BoundMethod", (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
