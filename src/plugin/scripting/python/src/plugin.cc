/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.python/stdafx.h>
#include <motor/plugin/plugin.hh>

class PythonVersion : public minitl::refcountable
{
    Motor::Plugin::Plugin< minitl::refcountable > m_pyPlugin;

public:
    PythonVersion(const Motor::Plugin::Plugin< minitl::refcountable >& plugin) : m_pyPlugin(plugin)
    {
    }

    ~PythonVersion()
    {
    }
};

static ref< PythonVersion > create(const Motor::Plugin::Context& context)
{
    static const char* versions[]
        = {"310", "39", "38", "37", "36", "35", "34", "33", "32", "31", "30", "27", "26"};
    for(size_t i = 0; i < sizeof(versions) / sizeof(versions[0]); ++i)
    {
        minitl::format_buffer< 1024u > pluginName
            = minitl::format< 1024u >(FMT("plugin.scripting.python{0}"), versions[i]);
        Motor::Plugin::Plugin< minitl::refcountable > p
            = Motor::Plugin::Plugin< minitl::refcountable >(pluginName.c_str(), context);
        if(p)
        {
            motor_info_format(Motor::Log::python(), "Loaded Python version {0}", versions[i]);
            return ref< PythonVersion >::create(Motor::Arena::general(), p);
        }
    }
    return ref< PythonVersion >();
}

MOTOR_PLUGIN_REGISTER_CREATE(&create);
