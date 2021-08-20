/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PYTHON_CONTEXT_HH_
#define MOTOR_PYTHON_CONTEXT_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/value.hh>
#include <motor/plugin.scripting.python/pythonscript.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <motor/plugin/plugin.hh>
#include <motor/scriptengine.hh>

namespace Motor { namespace Python {

class motor_api(PYTHON) Context : public ScriptEngine< PythonScript >
{
public:
    Context(const Plugin::Context& context, ref< PythonLibrary > library);
    ~Context();

private:
    virtual void unload(Resource::Resource & handle) override;
    virtual void runBuffer(weak< const PythonScript > script, Resource::Resource & resource,
                           const minitl::Allocator::Block< u8 >& buffer) override;
    virtual void reloadBuffer(weak< const PythonScript > script, Resource::Resource & resource,
                              const minitl::Allocator::Block< u8 >& buffer) override;
    static void  pythonInitialise();

private:
    void runCode(const char* buffer, const ifilename& filename);

private:
    ref< PythonLibrary > m_library;
    PyThreadState*       m_pythonState;
};

}}  // namespace Motor::Python

/**************************************************************************************************/
#endif
