/* Motor <motor.devel@gmail.com>
see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_CALL_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_CALL_HH

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

PyObject* call(raw< const Meta::Method > method, PyObject* self, PyObject* args, PyObject* kwargs);

}}  // namespace Motor::Python

#endif
