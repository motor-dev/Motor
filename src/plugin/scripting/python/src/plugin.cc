/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin/plugin.hh>

#ifndef MOTOR_PYTHON_VERSIONS
#    define MOTOR_PYTHON_VERSIONS
#endif

class PythonVersion : public minitl::pointer
{
    Motor::Plugin::Plugin< minitl::pointer > m_pyPlugin;

public:
    explicit PythonVersion(Motor::Plugin::Plugin< minitl::pointer >&& plugin)
        : m_pyPlugin(minitl::move(plugin))
    {
    }

    ~PythonVersion() override = default;
};

static scoped< PythonVersion > create(const Motor::Plugin::Context& context)
{
    static char versionBuffer[] = MOTOR_STRINGIZE((MOTOR_PYTHON_VERSIONS));
    char*       versions        = versionBuffer + 1;
    bool        done            = *versions == ')';
    while(!done)
    {
        const char* version = versions;
        while(*versions != ')' && *versions != ',')
            versions++;
        done      = *versions == ')';
        *versions = 0;
        minitl::format_buffer< 1024u > pluginName
            = minitl::format< 1024u >(FMT("plugin.scripting.python{0}"), version);
        Motor::Plugin::Plugin< minitl::pointer > p = Motor::Plugin::Plugin< minitl::pointer >(
            Motor::inamespace(pluginName.c_str()), context);
        if(p)
        {
            motor_info_format(Motor::Log::python(), "Loaded Python version {0}", version);
            return scoped< PythonVersion >::create(Motor::Arena::general(), minitl::move(p));
        }
        versions = versions + 1;
    }
    motor_error(Motor::Log::python(), "No python plugin to load");
    return {};
}

MOTOR_PLUGIN_REGISTER_CREATE(&create)
