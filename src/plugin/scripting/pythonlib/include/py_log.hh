/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/core/logger.hh>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>

namespace Motor { namespace Python {

struct PyMotorLog
{
    enum LogType
    {
        logTypeStdOut,
        logTypeStdErr
    };

    PyObject      py_object;
    ref< Logger > logger;
    LogType       type;

    static void registerType(PyObject* module);

    static int  init(PyObject* self, PyObject* args, PyObject* kwds);
    static void dealloc(PyObject* self);

    static PyObject* write(PyObject* self, PyObject* args);
    static PyObject* flush(PyObject* self, PyObject* args);

    static PyTypeObject s_pyType;
};

}}  // namespace Motor::Python
