/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <motor/plugin/plugin.hh>
#include <py_array.hh>
#include <py_class.hh>
#include <py_enum.hh>
#include <py_log.hh>
#include <py_namespace.hh>
#include <py_number.hh>
#include <py_object.hh>
#include <py_plugin.hh>
#include <py_string.hh>

namespace Motor { namespace Python {

tls< PythonLibrary > s_library;
PyObject*            s_moduleObject;

static PyObject* run(PyObject* self, PyObject* args)
{
    motor_forceuse(self);
    motor_forceuse(args);
    s_library->m_PyRun_InteractiveLoopFlags(stdin, "<interactive>", 0);
    Py_INCREF(s_library->m__Py_NoneStruct);
    return s_library->m__Py_NoneStruct;
}

static PyMethodDef s_methods[] = {{"run", &run, METH_NOARGS, NULL}, {NULL, NULL, 0, NULL}};

static PyModuleDef s_module
    = {PyModuleDef_HEAD_INIT, "py_motor", "", 0, s_methods, NULL, NULL, NULL, NULL};

static void setupModule(PyObject* module, bool registerLog)
{
    if(registerLog)
    {
        PyMotorLog::registerType(module);
    }
    PyMotorPlugin::registerType(module);
    PyMotorObject::registerType(module);
    PyMotorEnum::registerType(module);
    PyMotorNumber< bool >::registerType(module);
    PyMotorNumber< u8 >::registerType(module);
    PyMotorNumber< u16 >::registerType(module);
    PyMotorNumber< u32 >::registerType(module);
    PyMotorNumber< u64 >::registerType(module);
    PyMotorNumber< i8 >::registerType(module);
    PyMotorNumber< i16 >::registerType(module);
    PyMotorNumber< i32 >::registerType(module);
    PyMotorNumber< i64 >::registerType(module);
    PyMotorNumber< float >::registerType(module);
    PyMotorNumber< double >::registerType(module);
    PyMotorString< istring >::registerType(module);
    PyMotorString< inamespace >::registerType(module);
    PyMotorString< ipath >::registerType(module);
    PyMotorString< ifilename >::registerType(module);
    PyMotorArray::registerType(module);
    PyMotorNamespace::registerType(module);
    PyMotorClass::registerType(module);
    s_moduleObject = module;
}

PyObject* init2_py_motor(bool registerLog)
{
    /* python 2.x module initialisation */
    PyObject* module;
    if(s_library->m_Py_InitModule4)
    {
        motor_assert(sizeof(minitl::size_type) == 4, "Python is 32bits but Motor is 64bits");
        module
            = (*s_library->m_Py_InitModule4)("py_motor", s_methods, "", NULL, s_library->getApi());
    }
    else if(s_library->m_Py_InitModule4_64)
    {
        motor_assert(sizeof(minitl::size_type) == 8, "Python is 64bits but Motor is 32bits");
        module = (*s_library->m_Py_InitModule4_64)("py_motor", s_methods, "", NULL,
                                                   s_library->getApi());
    }
    else
    {
        motor_unimplemented();
        return 0;
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

ref< PythonLibrary > loadPython(const char* pythonPath)
{
    ref< PythonLibrary > library = ref< PythonLibrary >::create(Arena::general(), pythonPath);
    if(library)
    {
        setCurrentContext(library);
        registerModule();
        library->initialize();
        clearCurrentContext();
    }
    return library;
}

void setCurrentContext(weak< PythonLibrary > library)
{
    s_library = library;
}

void clearCurrentContext()
{
    s_library = 0;
}

}}  // namespace Motor::Python
