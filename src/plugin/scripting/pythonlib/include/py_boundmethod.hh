/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_BOUNDMETHOD_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_BOUNDMETHOD_HH

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>

namespace Motor { namespace Meta {
class Method;
}}  // namespace Motor::Meta

namespace Motor { namespace Python {

struct PyMotorObject;

struct PyBoundMethod
{
    PyObject                  py_object;
    raw< const Meta::Method > method {};
    PyObject*                 value {};

    static void registerType(PyObject* module);

    static PyObject* create(raw< const Meta::Method > method, PyMotorObject* value);
    static PyObject* repr(PyObject* self);
    static void      dealloc(PyObject* self);
    static PyObject* call(PyObject* self, PyObject* args, PyObject* kwds);

    static PyTypeObject s_pyType;
};

}}  // namespace Motor::Python

#endif
