/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin.scripting.python/context.hh>

namespace Motor { namespace Python {

Context::Context(const Plugin::Context& context, scoped< PythonLibrary >&& library)
    : ScriptEngine< PythonScript >(Arena::python(), context.resourceManager)
    , m_library(minitl::move(library))
    , m_pythonState(m_library->createThread())
{
}

Context::~Context()
{
    m_library->destroyThread(m_pythonState);
}

void Context::unload(const weak< const Resource::IDescription >& /*description*/,
                     Resource::Resource& /*handle*/)
{
    PythonLibrary::ThreadLock lock(m_library, m_pythonState);
}

void Context::runBuffer(const weak< const PythonScript >& script, Resource::Resource& /*resource*/,
                        const minitl::allocator::block< u8 >& buffer)
{
    runCode(reinterpret_cast< const char* >(buffer.begin()), script->getScriptName());
}

void Context::reloadBuffer(const weak< const PythonScript >& script,
                           Resource::Resource& /*resource*/,
                           const minitl::allocator::block< u8 >& buffer)
{
    runCode(reinterpret_cast< const char* >(buffer.begin()), script->getScriptName());
}

void Context::runCode(const char* buffer, const ifilename& filename)
{
    PythonLibrary::ThreadLock lock(m_library, m_pythonState);
    PyCodeObject*             code;
    if(m_library->m_Py_CompileStringExFlags)
    {
        code = (*m_library->m_Py_CompileStringExFlags)(buffer, filename.str().name, Py_file_input,
                                                       nullptr, -1);
    }
    else
    {
        code = (*m_library->m_Py_CompileStringFlags)(buffer, filename.str().name, Py_file_input,
                                                     nullptr);
    }
    if(code)
    {
        PyObject* m      = (*m_library->m_PyImport_AddModule)("__main__");
        PyObject* d      = (*m_library->m_PyModule_GetDict)(m);
        PyObject* result = (*m_library->m_PyEval_EvalCodeEx)(code, d, d, nullptr, 0, nullptr, 0,
                                                             nullptr, 0, nullptr);
        if(!result)
        {
            (*m_library->m_PyErr_Print)();
        }
        else
        {
            Py_DECREF(result);
        }
        Py_DECREF(code);
    }
    else
    {
        (*m_library->m_PyErr_Print)();
    }
}

}}  // namespace Motor::Python
