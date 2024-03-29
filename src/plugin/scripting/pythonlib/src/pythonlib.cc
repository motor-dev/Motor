/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>

namespace Motor { namespace Arena {

minitl::allocator& python()
{
    return script();
}

}}  // namespace Motor::Arena

namespace Motor { namespace Python {

PythonLibrary::ThreadLock::ThreadLock(const weak< PythonLibrary >& library, PyThreadState* thread)
    : m_library(library)
    , m_thread(thread)
{
    (*m_library->m_PyEval_AcquireThread)(m_thread);
    setCurrentContext(m_library);
}

PythonLibrary::ThreadLock::~ThreadLock()
{
    (*m_library->m_PyEval_ReleaseThread)(m_thread);
    clearCurrentContext();
}

void PythonLibrary::initialize()
{
    platformInitialize();
    (*m_Py_InitializeEx)(0);
    (*m_PyEval_InitThreads)();
    m_mainThread = (*m_PyEval_SaveThread)();
}

void PythonLibrary::finalize()
{
    (*m_PyEval_AcquireThread)(m_mainThread);
    (*m_Py_Finalize)();
}

PyThreadState* PythonLibrary::createThread()
{
    (*m_PyEval_AcquireThread)(m_mainThread);
    PyThreadState* result = (*m_Py_NewInterpreter)();
    setupPath();
    (*m_PyEval_ReleaseThread)(result);
    return result;
}

void PythonLibrary::destroyThread(PyThreadState* threadState)
{
    (*m_PyEval_AcquireThread)(threadState);
    (*m_Py_EndInterpreter)(threadState);
    (*m_PyThreadState_Swap)(m_mainThread);
    (*m_PyEval_ReleaseThread)(m_mainThread);
}

int PythonLibrary::getVersion() const
{
    return m_version;
}

int PythonLibrary::getApi() const
{
    return m_api;
}

}}  // namespace Motor::Python
