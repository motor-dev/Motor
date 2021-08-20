/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHONLIB_PY_ARRAY_HH_
#define MOTOR_PYTHONLIB_PY_ARRAY_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <py_object.hh>

namespace Motor { namespace Python {

struct PyMotorArray : public PyMotorObject
{
    static void registerType(PyObject* module);

    static PyObject*    stealValue(PyObject* owner, Meta::Value& value);
    static PyObject*    repr(PyObject* self);
    static int          nonZero(PyObject* self);
    static Py_ssize_t   length(PyObject* self);
    static PyObject*    item(PyObject* self, Py_ssize_t index);
    static int          setItem(PyObject* self, Py_ssize_t index, PyObject* value);
    static PyTypeObject s_pyType;
};

}}  // namespace Motor::Python

/**************************************************************************************************/
#endif
