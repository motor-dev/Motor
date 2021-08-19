/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PY_PLUGIN_HH_
#define MOTOR_PYTHONLIB_PY_PLUGIN_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Python {

struct PyMotorPlugin
{
    PyObject               py_object;
    Plugin::Plugin< void > value;

    static void registerType(PyObject* module);

    static PyObject* create(PyTypeObject* type, PyObject* args, PyObject* kwds);
    static int       init(PyObject* self, PyObject* args, PyObject* kwds);
    static PyObject* getattr(PyObject* self, const char* name);
    static int       setattr(PyObject* self, const char* name, PyObject* value);
    static PyObject* repr(PyObject* self);
    static void      dealloc(PyObject* self);
};

}}  // namespace Motor::Python

/**************************************************************************************************/
#endif
