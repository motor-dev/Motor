/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_class.hh>

namespace Motor { namespace Python {

PyTypeObject PyMotorClass::s_pyType = {{{0, nullptr}, 0},
                                       "py_motor.Class",
                                       sizeof(PyMotorClass),
                                       0,
                                       &PyMotorNamespace::dealloc,
                                       nullptr,
                                       &PyMotorNamespace::getattr,
                                       &PyMotorNamespace::setattr,
                                       nullptr,
                                       &PyMotorNamespace::repr,
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
                                       "Wrapper class for the C++ Motor namespaces",
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       0,
                                       nullptr,
                                       nullptr,
                                       PyMotorNamespace::s_methods,
                                       nullptr,
                                       nullptr,
                                       PyMotorObject::s_pyTypePtr,
                                       nullptr,
                                       nullptr,
                                       nullptr,
                                       0,
                                       &PyMotorNamespace::init,
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

PyObject* PyMotorClass::stealValue(PyObject* owner, Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Namespace,
                 "PyMotorClass only accepts Namespace types");
    PyObject* result                            = s_pyType.tp_alloc(&s_pyType, 0);
    static_cast< PyMotorClass* >(result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }
    new(&(static_cast< PyMotorClass* >(result))->value) Meta::Value();
    (static_cast< PyMotorClass* >(result))->value.swap(value);
    return result;
}

void PyMotorClass::registerType(PyObject* module)
{
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, "Class", (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
