/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin/plugin.hh>

class PythonVersion : public minitl::refcountable
{
    Motor::Plugin::Plugin< minitl::refcountable > m_pyPlugin;

public:
    explicit PythonVersion(const Motor::Plugin::Plugin< minitl::refcountable >& plugin)
        : m_pyPlugin(plugin)
    {
    }

    ~PythonVersion() override = default;
};

static ref< PythonVersion > create(const Motor::Plugin::Context& context)
{
    static const char* versions[]
        = {"310", "39", "38", "37", "36", "35", "34", "33", "32", "31", "30", "27", "26"};
    for(auto& version: versions)
    {
        minitl::format_buffer< 1024u > pluginName
            = minitl::format< 1024u >(FMT("plugin.scripting.python{0}"), version);
        Motor::Plugin::Plugin< minitl::refcountable > p
            = Motor::Plugin::Plugin< minitl::refcountable >(Motor::inamespace(pluginName.c_str()),
                                                            context);
        if(p)
        {
            motor_info_format(Motor::Log::python(), "Loaded Python version {0}", version);
            return ref< PythonVersion >::create(Motor::Arena::general(), p);
        }
    }
    return {};
}

MOTOR_PLUGIN_REGISTER_CREATE(&create)
