/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SAMPLE_LUASAMPLE_HH_
#define MOTOR_SAMPLE_LUASAMPLE_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {

class LuaSample : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_luaManager;
    ref< const Package > const                m_mainPackage;

public:
    LuaSample(const Plugin::Context& context);
    ~LuaSample();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
