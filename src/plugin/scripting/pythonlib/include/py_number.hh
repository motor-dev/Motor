/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_NUMBER_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_NUMBER_HH

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <py_object.hh>

namespace Motor { namespace Python {

template < typename T >
struct PyMotorNumber : public PyMotorObject
{
    static void registerType(PyObject* module);

    static PyObject* stealValue(PyObject* owner, Meta::Value& value);
    static int       init(PyObject* self, PyObject* args, PyObject* kwds);
    static PyObject* repr(PyObject* self);
    static PyObject* str(PyObject* self);
    static PyObject* toint(PyObject* self);
    static PyObject* tolong(PyObject* self);
    static PyObject* tofloat(PyObject* self);
    static int       nonZero(PyObject* self);

    static PyTypeObject                   s_pyType;
    static PyTypeObject::Py2NumberMethods s_py2NumberNumber;
    static PyTypeObject::Py3NumberMethods s_py3NumberNumber;
};

extern template struct PyMotorNumber< i8 >;
extern template struct PyMotorNumber< i16 >;
extern template struct PyMotorNumber< i32 >;
extern template struct PyMotorNumber< i64 >;
extern template struct PyMotorNumber< u8 >;
extern template struct PyMotorNumber< u16 >;
extern template struct PyMotorNumber< u32 >;
extern template struct PyMotorNumber< u64 >;

}}  // namespace Motor::Python

#endif
