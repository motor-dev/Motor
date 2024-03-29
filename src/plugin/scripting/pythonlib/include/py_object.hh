/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_OBJECT_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PY_OBJECT_HH

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/value.hh>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>

namespace Motor { namespace Python {

struct PyMotorObject : public PyObject
{
    PyObject*   owner {};
    Meta::Value value {};

    static void registerType(PyObject* module);

    static PyObject*            stealValue(PyObject* owner, Meta::Value& value);
    static PyObject*            newinst(PyTypeObject* type, PyObject* args, PyObject* kwargs);
    static PyObject*            dir(raw< const Meta::Class > metaclass);
    static PyObject*            dir(PyObject* self, PyObject* args);
    static Meta::ConversionCost distance(PyObject* object, const Meta::Type& desiredType);
    static void      unpack(PyObject* object, const Meta::Type& desiredType, void* buffer);
    static void      unpackAny(PyObject* object, void* buffer);
    static PyObject* getattr(PyObject* self, const char* name);
    static int       setattr(PyObject* self, const char* name, PyObject* value);
    static PyObject* repr(PyObject* self);
    static void      dealloc(PyObject* self);
    static PyObject* call(PyObject* self, PyObject* args, PyObject* kwds);
    static int       nonZero(PyObject* self);

    static PyTypeObject            s_pyType;
    static PyMethodDef             s_methodArray[];
    static constexpr PyTypeObject* s_pyTypePtr {&s_pyType};
    static constexpr PyMethodDef*  s_methods {s_methodArray};
};

}}  // namespace Motor::Python

#endif
