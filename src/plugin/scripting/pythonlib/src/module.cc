/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_log.hh>
#include <py_object.hh>
#include <py_plugin.hh>

namespace Motor { namespace Python {

tls< PythonLibrary > s_library;

static PyObject* run(PyObject* self, PyObject* args)
{
    motor_forceuse(self);
    motor_forceuse(args);
    s_library->m_PyRun_InteractiveLoopFlags(stdin, "<interactive>", nullptr);
    Py_INCREF(s_library->m__Py_NoneStruct);
    return s_library->m__Py_NoneStruct;
}

static PyMethodDef s_methods[]
    = {{"run", &run, METH_NOARGS, nullptr}, {nullptr, nullptr, 0, nullptr}};

static PyModuleDef s_module
    = {PyModuleDef_HEAD_INIT, "py_motor", "", 0, s_methods, nullptr, nullptr, nullptr, nullptr};

static void setupModule(PyObject* module, bool registerLog)
{
    if(registerLog)
    {
        PyMotorLog::registerType(module);
    }
    PyMotorPlugin::registerType(module);
    PyMotorObject::registerType(module);
}

PyObject* init2_py_motor(bool registerLog)
{
    /* python 2.x module initialisation */
    PyObject* module;
    if(s_library->m_Py_InitModule4)
    {
        motor_assert(sizeof(minitl::size_t) == 4, "Python is 32bits but Motor is 64bits");
        module = (*s_library->m_Py_InitModule4)("py_motor", s_methods, "", nullptr,
                                                s_library->getApi());
    }
    else if(s_library->m_Py_InitModule4_64)
    {
        motor_assert(sizeof(minitl::size_t) == 8, "Python is 64bits but Motor is 32bits");
        module = (*s_library->m_Py_InitModule4_64)("py_motor", s_methods, "", nullptr,
                                                   s_library->getApi());
    }
    else
    {
        motor_unimplemented();
        return nullptr;
    }
    setupModule(module, registerLog);
    return module;
}

PyObject* init3_py_motor(bool registerLog)
{
    /* python 3.x module initialisation */
    PyObject* module = (*s_library->m_PyModule_Create2)(&s_module, s_library->getApi());
    setupModule(module, registerLog);
    return module;
}

static void init2_py_motor_log()
{
    motor_assert(s_library, "Current Python context not set; call setCurrentContext");
    init2_py_motor(true);
}

static PyObject* init3_py_motor_log()
{
    motor_assert(s_library, "Current Python context not set; call setCurrentContext");
    return init3_py_motor(true);
}

static void registerModule()
{
    using namespace Motor::Python;
    if(s_library->getVersion() < 30)
    {
        s_library->m_PyImport_AppendInittab2("py_motor", &init2_py_motor_log);
    }
    else
    {
        s_library->m_PyImport_AppendInittab3("py_motor", &init3_py_motor_log);
    }
}

scoped< PythonLibrary > loadPython(const char* pythonPath)
{
    scoped< PythonLibrary > library = scoped< PythonLibrary >::create(Arena::general(), pythonPath);
    if(library)
    {
        setCurrentContext(library);
        registerModule();
        library->initialize();
        clearCurrentContext();
    }
    return library;
}

void setCurrentContext(const weak< PythonLibrary >& library)
{
    s_library = library;
}

void clearCurrentContext()
{
    s_library = nullptr;
}

}}  // namespace Motor::Python
