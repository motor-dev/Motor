/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PY_CLASS_HH_
#define MOTOR_PYTHONLIB_PY_CLASS_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <py_namespace.hh>

namespace Motor { namespace Python {

struct PyMotorClass : public PyMotorNamespace
{
    static PyObject* stealValue(PyObject* owner, Meta::Value& value);

    static void         registerType(PyObject* module);
    static PyTypeObject s_pyType;
};

}}  // namespace Motor::Python

/**************************************************************************************************/
#endif
