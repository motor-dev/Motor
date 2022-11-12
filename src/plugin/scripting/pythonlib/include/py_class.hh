/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
