/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_log.hh>

namespace Motor { namespace Python {

static PyMethodDef s_logMethods[] = {{"write", &PyMotorLog::write, METH_VARARGS, "sys.std*.write"},
                                     {"flush", &PyMotorLog::flush, METH_VARARGS, "sys.std*.flush"},
                                     {nullptr, nullptr, 0, nullptr}};

PyTypeObject PyMotorLog::s_pyType = {{{0, nullptr}, 0},
                                     "py_motor.Log",
                                     sizeof(PyMotorLog),
                                     0,
                                     &PyMotorLog::dealloc,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                     "Motor logging",
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     0,
                                     nullptr,
                                     nullptr,
                                     s_logMethods,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     0,
                                     &PyMotorLog::init,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     nullptr,
                                     0,
                                     nullptr,
                                     nullptr};

int PyMotorLog::init(PyObject* self, PyObject* args, PyObject* kwds)
{
    motor_forceuse(self);
    motor_forceuse(args);
    motor_forceuse(kwds);
    return 0;
}

void PyMotorLog::dealloc(PyObject* self)
{
    auto* self_ = reinterpret_cast< PyMotorLog* >(self);
    self_->logger.~weak();
    self->py_type->tp_free(self);
}

static char  logBuffer[65535];
static char* logCurrent = logBuffer;
PyObject*    PyMotorLog::write(PyObject* self, PyObject* args)
{
    auto*    log = reinterpret_cast< PyMotorLog* >(self);
    char*    str;
    LogLevel level = log->type == logTypeStdOut ? logInfo : logError;
    if(s_library->m__PyArg_ParseTuple_SizeT(args, "s", &str))
    {
        u32 written = 0;
        for(; *str; ++str, ++written)
        {
            if(*str == '\n')
            {
                *logCurrent = 0;
                log->logger->log(level, "TODO", 0, logBuffer);
                logCurrent = logBuffer;
            }
            else
            {
                *logCurrent = *str;
                logCurrent++;
                if(logCurrent >= logBuffer + sizeof(logBuffer) - 1)
                {
                    *logCurrent = 0;
                    log->logger->log(level, "TODO", 0, logBuffer);
                    logCurrent = logBuffer;
                }
            }
        }
        if(s_library->getVersion() >= 30)
            return s_library->m_PyLong_FromUnsignedLongLong(written);
        else
            return s_library->m_PyInt_FromLong((long)written);
    }
    else
    {
        return nullptr;
    }
}

PyObject* PyMotorLog::flush(PyObject* self, PyObject* args)
{
    motor_forceuse(self);
    motor_forceuse(args);
    Py_INCREF(s_library->m__Py_NoneStruct);
    return s_library->m__Py_NoneStruct;
}

void PyMotorLog::registerType(PyObject* module)
{
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);

    auto* ob = reinterpret_cast< PyMotorLog* >(s_pyType.tp_alloc(&s_pyType, 0));
    new(&ob->logger) weak< Logger >(Log::python());
    ob->type = logTypeStdOut;
    result   = s_library->m_PySys_SetObject("stdout", (PyObject*)ob);
    motor_assert(result >= 0, "unable to register stdout");
    Py_DECREF(ob);

    ob = reinterpret_cast< PyMotorLog* >(s_pyType.tp_alloc(&s_pyType, 0));
    new(&ob->logger) weak< Logger >(Log::python());
    ob->type = logTypeStdErr;
    result   = s_library->m_PySys_SetObject("stderr", (PyObject*)ob);
    motor_assert(result >= 0, "unable to register stderr");
    Py_DECREF(ob);
    motor_forceuse(result);
    motor_forceuse(module);
}

}}  // namespace Motor::Python
