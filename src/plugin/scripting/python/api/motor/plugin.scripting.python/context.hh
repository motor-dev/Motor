/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PYTHON_CONTEXT_HH
#define MOTOR_PLUGIN_SCRIPTING_PYTHON_CONTEXT_HH

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/meta/class.meta.hh>
#include <motor/meta/value.hh>
#include <motor/plugin.scripting.python/pythonscript.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <motor/plugin/plugin.hh>
#include <motor/scriptengine.hh>

namespace Motor { namespace Python {

class motor_api(PYTHON) Context : public ScriptEngine< PythonScript >
{
public:
    Context(const Plugin::Context& context, const ref< PythonLibrary >& library);
    ~Context() override;

private:
    void unload(const weak< const Resource::IDescription >& description, Resource::Resource& handle)
        override;
    void runBuffer(const weak< const PythonScript >& script, Resource::Resource& resource,
                   const minitl::allocator::block< u8 >& buffer) override;
    void reloadBuffer(const weak< const PythonScript >& script, Resource::Resource& resource,
                      const minitl::allocator::block< u8 >& buffer) override;

private:
    void runCode(const char* buffer, const ifilename& filename);

private:
    ref< PythonLibrary > m_library;
    PyThreadState*       m_pythonState;
};

}}  // namespace Motor::Python

#endif
