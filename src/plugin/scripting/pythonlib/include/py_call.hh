/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

PyObject* call(raw< const Meta::Method > method, PyObject* self, PyObject* args, PyObject* kwargs);

}}  // namespace Motor::Python
