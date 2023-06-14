/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PYTHONLIB_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHONLIB_PYTHONLIB_HH

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/core/threads/threadlocal.hh>
#include <motor/plugin.scripting.pythonlib/pythontypes.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Python {

class motor_api(PYTHONLIB) PythonLibrary : public minitl::refcountable
{
public:
    explicit PythonLibrary(const char* pythonLibraryName);
    ~PythonLibrary() override;

    operator const void*() const  // NOLINT(google-explicit-constructor
    {
        return (const void*)m_status;
    }
    bool operator!() const
    {
        return !m_status;
    }

    void initialize();
    void finalize();

    int getVersion() const;
    int getApi() const;

    PyThreadState* createThread();
    void           destroyThread(PyThreadState * threadState);

    struct motor_api(PYTHONLIB) ThreadLock
    {
        ThreadLock(const weak< PythonLibrary >& library, PyThreadState* thread);
        ~ThreadLock();

    private:
        weak< PythonLibrary > m_library;
        PyThreadState*        m_thread;
    };

private:
    void platformInitialize();
    void setupPath() const;

private:
    friend struct ThreadLock;

private:
    const char*    m_pythonLibraryName;
    void*          m_handle;
    bool           m_status;
    int            m_api;
    int            m_version;
    PyThreadState* m_mainThread {};

private:  // friend ThreadLock
    Type_Py_SetPythonHome2 m_Py_SetPythonHome2 {};
    Type_Py_SetPythonHome3 m_Py_SetPythonHome3 {};
    Type_Py_InitializeEx   m_Py_InitializeEx {};
    Type_Py_Finalize       m_Py_Finalize {};
    Type_Py_NewInterpreter m_Py_NewInterpreter {};
    Type_Py_EndInterpreter m_Py_EndInterpreter {};
    Type_Py_GetPath        m_Py_GetPath {};
    Type_Py_GetVersion     m_Py_GetVersion {};

    Type_PyEval_InitThreads   m_PyEval_InitThreads {};
    Type_PyEval_SaveThread    m_PyEval_SaveThread {};
    Type_PyEval_AcquireThread m_PyEval_AcquireThread {};
    Type_PyEval_ReleaseThread m_PyEval_ReleaseThread {};
    Type_PyEval_ReleaseLock   m_PyEval_ReleaseLock {};
    Type_PyThreadState_Swap   m_PyThreadState_Swap {};

public:
    Type_PyRun_SimpleString         m_PyRun_SimpleString {};
    Type_PyRun_InteractiveLoopFlags m_PyRun_InteractiveLoopFlags {};
    Type_Py_CompileStringFlags      m_Py_CompileStringFlags;
    Type_Py_CompileStringExFlags    m_Py_CompileStringExFlags;
    Type_PyEval_EvalCodeEx          m_PyEval_EvalCodeEx {};
    Type_Py_InitModule4             m_Py_InitModule4;
    Type_Py_InitModule4_64          m_Py_InitModule4_64;
    Type_PyModule_Create2           m_PyModule_Create2 {};
    Type_PyModule_AddObject         m_PyModule_AddObject {};
    Type_PyModule_GetDict           m_PyModule_GetDict {};
    Type_PyImport_AddModule         m_PyImport_AddModule {};
    Type_PyImport_AppendInittab2    m_PyImport_AppendInittab2 {};
    Type_PyImport_AppendInittab3    m_PyImport_AppendInittab3 {};
    Type__Py_NoneStruct             m__Py_NoneStruct {};   // NOLINT(bugprone-reserved-identifier)
    Type__Py_TrueStruct             m__Py_TrueStruct {};   // NOLINT(bugprone-reserved-identifier)
    Type__Py_FalseStruct            m__Py_FalseStruct {};  // NOLINT(bugprone-reserved-identifier)
    Type__Py_NotImplementedStruct
        m__Py_NotImplementedStruct {};                     // NOLINT(bugprone-reserved-identifier)

    Type_PyObject_SetAttrString m_PyObject_SetAttrString {};
    Type_PyObject_GetAttrString m_PyObject_GetAttrString {};
    Type__PyArg_ParseTuple_SizeT
        m__PyArg_ParseTuple_SizeT {};             // NOLINT(bugprone-reserved-identifier)
    Type__PyArg_ParseTupleAndKeywords_SizeT
        m__PyArg_ParseTupleAndKeywords_SizeT {};  // NOLINT(bugprone-reserved-identifier)
    Type_PyObject_IsTrue     m_PyObject_IsTrue {};
    Type_PyType_GenericAlloc m_PyType_GenericAlloc {};
    Type_PyType_GenericNew   m_PyType_GenericNew {};
    Type_PyType_Ready        m_PyType_Ready {};
    Type_PyCFunction_NewEx   m_PyCFunction_NewEx {};

    Type_PyList_New      m_PyList_New {};
    Type_PyList_Size     m_PyList_Size {};
    Type_PyList_GetItem  m_PyList_GetItem {};
    Type_PyList_SetItem  m_PyList_SetItem {};
    Type_PyList_Insert   m_PyList_Insert {};
    Type_PyList_Append   m_PyList_Append {};
    Type_PyList_GetSlice m_PyList_GetSlice {};
    Type_PyList_SetSlice m_PyList_SetSlice {};

    Type_PyTuple_New      m_PyTuple_New {};
    Type_PyTuple_Size     m_PyTuple_Size {};
    Type_PyTuple_GetItem  m_PyTuple_GetItem {};
    Type_PyTuple_SetItem  m_PyTuple_SetItem {};
    Type_PyTuple_GetSlice m_PyTuple_GetSlice {};

    Type_PyDict_New           m_PyDict_New {};
    Type_PyDict_Size          m_PyDict_Size {};
    Type_PyDict_GetItem       m_PyDict_GetItem {};
    Type_PyDict_SetItem       m_PyDict_SetItem {};
    Type_PyDict_DelItem       m_PyDict_DelItem {};
    Type_PyDict_Next          m_PyDict_Next {};
    Type_PyDict_GetItemString m_PyDict_GetItemString {};
    Type_PyDict_SetItemString m_PyDict_SetItemString {};

    Type_PyString_FromString        m_PyString_FromString {};
    Type_PyString_FromStringAndSize m_PyString_FromStringAndSize {};
    Type_PyString_FromFormat        m_PyString_FromFormat {};
    Type_PyString_Size              m_PyString_Size {};
    Type_PyString_AsString          m_PyString_AsString {};
    Type_PyString_AsStringAndSize   m_PyString_AsStringAndSize {};

    Type_PyUnicode_FromString        m_PyUnicode_FromString {};
    Type_PyUnicode_FromStringAndSize m_PyUnicode_FromStringAndSize {};
    Type_PyUnicode_FromFormat        m_PyUnicode_FromFormat {};
    Type_PyUnicode_AsUTF8            m_PyUnicode_AsUTF8 {};
    Type_PyUnicode_AsUTF8String      m_PyUnicode_AsUTF8String {};
    Type_PyUnicode_AsASCIIString     m_PyUnicode_AsASCIIString {};
    Type_PyBytes_AsString            m_PyBytes_AsString {};

    Type_PyBool_FromLong               m_PyBool_FromLong {};
    Type_PyLong_FromUnsignedLongLong   m_PyLong_FromUnsignedLongLong {};
    Type_PyLong_AsUnsignedLongLongMask m_PyLong_AsUnsignedLongLongMask {};
    Type_PyInt_FromLong                m_PyInt_FromLong {};
    Type_PyInt_AsUnsignedLongMask      m_PyInt_AsUnsignedLongMask {};
    Type_PyFloat_FromDouble            m_PyFloat_FromDouble {};
    Type_PyFloat_AsDouble              m_PyFloat_AsDouble {};

    Type_PyErr_Print       m_PyErr_Print {};
    Type_PyErr_SetString   m_PyErr_SetString {};
    Type_PyErr_Format      m_PyErr_Format {};
    Type_PyErr_BadArgument m_PyErr_BadArgument {};

    Type_PyBool_Type          m_PyBool_Type {};
    Type_PyFloat_Type         m_PyFloat_Type {};
    Type_PyExc_Exception      m_PyExc_Exception {};
    Type_PyExc_AttributeError m_PyExc_AttributeError {};
    Type_PyExc_ImportError    m_PyExc_ImportError {};
    Type_PyExc_IndexError     m_PyExc_IndexError {};
    Type_PyExc_TypeError      m_PyExc_TypeError {};

    Type_PySys_GetObject m_PySys_GetObject {};
    Type_PySys_SetObject m_PySys_SetObject {};

    constexpr static int Py_LT = 0;
    constexpr static int Py_LE = 1;
    constexpr static int Py_EQ = 2;
    constexpr static int Py_NE = 3;
    constexpr static int Py_GT = 4;
    constexpr static int Py_GE = 5;
};

extern tls< PythonLibrary > s_library;

motor_api(PYTHONLIB) PyObject* init2_py_motor(bool registerLog);
motor_api(PYTHONLIB) PyObject* init3_py_motor(bool registerLog);
motor_api(PYTHONLIB) ref< PythonLibrary > loadPython(const char* pythonPath);
motor_api(PYTHONLIB) void setCurrentContext(const weak< PythonLibrary >& library);
motor_api(PYTHONLIB) void clearCurrentContext();

}}  // namespace Motor::Python

#endif
