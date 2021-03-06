/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PY_NAMESPACE_HH_
#define MOTOR_PYTHONLIB_PY_NAMESPACE_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <py_object.hh>

namespace Motor { namespace Python {

struct PyMotorNamespace : public PyMotorObject
{
    static void registerType(PyObject* module);

    static PyObject* stealValue(PyObject* owner, Meta::Value& value);
    static int       init(PyObject* self, PyObject* args, PyObject* kwds);
    static PyObject* getattr(PyObject* self, const char* name);
    static int       setattr(PyObject* self, const char* name, PyObject* value);
    static PyObject* dir(PyObject* self, PyObject* args);
    static PyObject* repr(PyObject* self);

    static PyTypeObject s_pyType;
    static PyMethodDef  s_methods[];
};

}}  // namespace Motor::Python

/**************************************************************************************************/
#endif
