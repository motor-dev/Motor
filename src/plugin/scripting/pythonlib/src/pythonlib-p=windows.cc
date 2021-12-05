/* Motor <motor.devel@gmail.com>
see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <string.h>

namespace Motor { namespace Python {

static HMODULE getPythonModuleHandle()
{
    typedef BOOL(WINAPI * EnumProcessModulesFunc)(HANDLE hProcess, HMODULE * lphModule, DWORD cb,
                                                  LPDWORD lpcbNeeded);
    EnumProcessModulesFunc EnumProcessModules = 0;
    HMODULE                h                  = LoadLibraryA("Psapi.dll");
    if(h != 0)
    {
        EnumProcessModules = motor_function_cast< EnumProcessModulesFunc >(
            GetProcAddress(h, "EnumProcessModules"));
    }
    if(!EnumProcessModules)
    {
        if(h) FreeLibrary(h);
        h                  = LoadLibraryA("kernel32.dll");
        EnumProcessModules = motor_function_cast< EnumProcessModulesFunc >(
            GetProcAddress(h, "K32EnumProcessModules"));
    }

    if(EnumProcessModules)
    {
        DWORD needed = 0;
        if(!(*EnumProcessModules)(GetCurrentProcess(), 0, 0, &needed))
        {
            motor_error("Could not locate python: EnumProcessModules failed");
            return (HMODULE)NULL;
        }
        minitl::Allocator::Block< HMODULE > modules(Arena::temporary(), needed / sizeof(HMODULE));
        if(!(*EnumProcessModules)(GetCurrentProcess(), modules.data(), (DWORD)modules.byteCount(),
                                  &needed))
        {
            motor_error("Could not locate python: EnumProcessModules failed");
            return (HMODULE)NULL;
        }
        FreeLibrary(h);

        for(u64 i = modules.count(); i > 0; --i)
        {
            if(GetProcAddress(modules[i - 1], "Py_InitializeEx"))
            {
                char filename[1024];
                if(GetModuleFileNameA(modules[i - 1], filename, sizeof(filename)))
                    motor_info("using %s" | filename);
                return modules[i - 1];
            }
        }
        motor_error("Could not locate python: could not locate module with Py_InitializeEx");
        return NULL;
    }
    else
    {
        FreeLibrary(h);
        motor_error("Could not locate python: could not locate procedure \"EnumProcessModules\" in "
                    "Psapi.dll or Kernel32.dll");
        return NULL;
    }
}

PythonLibrary::PythonLibrary(const char* pythonLibraryName)
    : m_pythonLibraryName(pythonLibraryName)
    , m_handle(m_pythonLibraryName
                   ? LoadLibraryA(minitl::format< 1024u >("%s.dll") | m_pythonLibraryName)
                   : getPythonModuleHandle())
    , m_status(m_handle != 0)
    , m_api(1013)
    , m_version(0)
{
    if(!m_status)
    {
        motor_error("unable to load library %s" | pythonLibraryName);
    }
    else
    {
#define motor_get_func_name_opt(f, dest)                                                           \
    do                                                                                             \
    {                                                                                              \
        void* tmp = (void*)(GetProcAddress((HMODULE)m_handle, #f));                                \
        if(tmp) memcpy(&m_##dest, &tmp, sizeof(dest##Type));                                       \
    } while(0)
#define motor_get_func_opt(f) motor_get_func_name_opt(f, f)
#define motor_get_func_name(f, dest)                                                               \
    do                                                                                             \
    {                                                                                              \
        motor_get_func_name_opt(f, dest);                                                          \
        if(!m_##dest)                                                                              \
        {                                                                                          \
            motor_error("could not locate function %s in module %s" | #f                           \
                        | (pythonLibraryName ? pythonLibraryName : "root"));                       \
            m_status = false;                                                                      \
        }                                                                                          \
    } while(0)
#define motor_get_func(f) motor_get_func_name(f, f)

        motor_get_func(Py_InitializeEx);
        motor_get_func(Py_Finalize);
        motor_get_func(Py_NewInterpreter);
        motor_get_func(Py_EndInterpreter);
        motor_get_func(Py_GetPath);
        motor_get_func(Py_GetVersion);
        const char* version = m_Py_GetVersion();
        m_version           = (version[0] - '0') * 10 + (version[2] - '0');
        if(m_version >= 30)
        {
            motor_get_func(PyModule_Create2);
            motor_get_func_name(PyImport_AppendInittab, PyImport_AppendInittab3);
            motor_get_func_name(Py_SetPythonHome, Py_SetPythonHome3);
        }
        else
        {
            m_Py_InitModule4    = 0;
            m_Py_InitModule4_64 = 0;
            motor_get_func_opt(Py_InitModule4);
            motor_get_func_opt(Py_InitModule4_64);
            motor_get_func_name(PyImport_AppendInittab, PyImport_AppendInittab2);
            motor_get_func_name(Py_SetPythonHome, Py_SetPythonHome2);
        }
        if(m_version >= 32)
        {
            m_Py_CompileStringFlags = 0;
            motor_get_func(Py_CompileStringExFlags);
        }
        else
        {
            m_Py_CompileStringExFlags = 0;
            motor_get_func(Py_CompileStringFlags);
        }
        motor_get_func(PyEval_EvalCodeEx);

        motor_get_func(PyModule_AddObject);
        motor_get_func(PyModule_GetDict);
        motor_get_func(PyImport_AddModule);
        motor_get_func(PyEval_InitThreads);
        motor_get_func(PyEval_SaveThread);
        motor_get_func(PyEval_AcquireThread);
        motor_get_func(PyEval_ReleaseThread);
        motor_get_func(PyEval_ReleaseLock);
        motor_get_func(PyThreadState_Swap);
        motor_get_func(PyRun_SimpleString);
        motor_get_func(PyRun_InteractiveLoopFlags);
        motor_get_func(_Py_NoneStruct);
        motor_get_func(PyObject_SetAttrString);
        motor_get_func(PyObject_GetAttrString);
        motor_get_func(_PyArg_ParseTuple_SizeT);
        motor_get_func(_PyArg_ParseTupleAndKeywords_SizeT);
        motor_get_func(PyObject_IsTrue);
        motor_get_func(PyCFunction_NewEx);
        motor_get_func(PyType_Ready);
        motor_get_func(PyType_GenericAlloc);
        motor_get_func(PyType_GenericNew);
        motor_get_func(PyList_New);
        motor_get_func(PyList_Size);
        motor_get_func(PyList_GetItem);
        motor_get_func(PyList_SetItem);
        motor_get_func(PyList_Insert);
        motor_get_func(PyList_Append);
        motor_get_func(PyList_GetSlice);
        motor_get_func(PyList_SetSlice);
        motor_get_func(PyTuple_New);
        motor_get_func(PyTuple_Size);
        motor_get_func(PyTuple_GetItem);
        motor_get_func(PyTuple_SetItem);
        motor_get_func(PyTuple_GetSlice);
        motor_get_func(PyDict_New);
        motor_get_func(PyDict_Size);
        motor_get_func(PyDict_GetItem);
        motor_get_func(PyDict_SetItem);
        motor_get_func(PyDict_DelItem);
        motor_get_func(PyDict_Next);
        motor_get_func(PyDict_GetItemString);
        motor_get_func(PyDict_SetItemString);
        if(m_version < 30)
        {
            motor_get_func(PyString_FromString);
            motor_get_func(PyString_FromStringAndSize);
            motor_get_func(PyString_FromFormat);
            motor_get_func(PyString_Size);
            motor_get_func(PyString_AsString);
            motor_get_func(PyString_AsStringAndSize);
        }
        else
        {
            motor_get_func_name_opt(PyUnicode_FromString, PyUnicode_FromString);
            motor_get_func_name_opt(PyUnicodeUCS2_FromString, PyUnicode_FromString);
            motor_get_func_name_opt(PyUnicodeUCS4_FromString, PyUnicode_FromString);
            motor_get_func_name_opt(PyUnicode_FromStringAndSize, PyUnicode_FromStringAndSize);
            motor_get_func_name_opt(PyUnicodeUCS2_FromStringAndSize, PyUnicode_FromStringAndSize);
            motor_get_func_name_opt(PyUnicodeUCS4_FromStringAndSize, PyUnicode_FromStringAndSize);
            motor_get_func_name_opt(PyUnicode_FromFormat, PyUnicode_FromFormat);
            motor_get_func_name_opt(PyUnicodeUCS2_FromFormat, PyUnicode_FromFormat);
            motor_get_func_name_opt(PyUnicodeUCS4_FromFormat, PyUnicode_FromFormat);
            motor_get_func_name_opt(PyUnicode_AsASCIIString, PyUnicode_AsASCIIString);
            motor_get_func_name_opt(PyUnicodeUCS2_AsASCIIString, PyUnicode_AsASCIIString);
            motor_get_func_name_opt(PyUnicodeUCS4_AsASCIIString, PyUnicode_AsASCIIString);
            motor_get_func_name_opt(PyUnicode_AsUTF8String, PyUnicode_AsUTF8String);
            motor_get_func_name_opt(PyUnicodeUCS2_AsUTF8String, PyUnicode_AsUTF8String);
            motor_get_func_name_opt(PyUnicodeUCS4_AsUTF8String, PyUnicode_AsUTF8String);
            if(m_version >= 33) motor_get_func(PyUnicode_AsUTF8);
            motor_get_func(PyBytes_AsString);
        }
        motor_get_func(PyBool_FromLong);
        if(m_version < 30)
        {
            motor_get_func(PyInt_AsUnsignedLongMask);
            motor_get_func(PyInt_FromLong);
        }
        motor_get_func(PyLong_AsUnsignedLongLongMask);
        motor_get_func(PyLong_FromUnsignedLongLong);
        motor_get_func(PyFloat_FromDouble);
        motor_get_func(PyFloat_AsDouble);
        motor_get_func(PyErr_Print);
        motor_get_func(PyErr_SetString);
        motor_get_func(PyErr_Format);
        motor_get_func(PyErr_BadArgument);
        motor_get_func(PyBool_Type);
        motor_get_func(PyFloat_Type);
        motor_get_func(PyExc_Exception);
        motor_get_func(PyExc_AttributeError);
        motor_get_func(PyExc_ImportError);
        motor_get_func(PyExc_IndexError);
        motor_get_func(PyExc_TypeError);
        motor_get_func(PySys_GetObject);
        motor_get_func(PySys_SetObject);
#undef motor_get_fun
#undef motor_get_fun_opt
    }
}

PythonLibrary::~PythonLibrary()
{
    if(m_status && m_pythonLibraryName)
    {
        finalize();
    }
    if(m_handle && m_pythonLibraryName)
    {
        FreeLibrary((HMODULE)m_handle);
    }
}

void PythonLibrary::platformInitialize()
{
    ifilename programPath = Environment::getEnvironment().getProgramPath();
    programPath.pop_back();
    programPath.push_back("lib");
    programPath.push_back(istring(minitl::format< 32u >("python%d") | m_version));
    if(m_version < 30)
    {
        static ifilename::Filename f = programPath.str();
        (*m_Py_SetPythonHome2)(f.name);
    }
    else
    {
        static wchar_t s_programPath[1024];
        mbstowcs(s_programPath, programPath.str(), sizeof(s_programPath));
        (*m_Py_SetPythonHome3)(s_programPath);
    }
}

void PythonLibrary::setupPath()
{
    ifilename programPath = Environment::getEnvironment().getProgramPath();
    programPath.pop_back();
    programPath.push_back("lib");
    (*m_PyRun_SimpleString)(minitl::format< 4096 >("import sys; sys.path.append(\"%s\")")
                            | programPath.str().name);
}

}}  // namespace Motor::Python
