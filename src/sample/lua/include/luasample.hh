/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SAMPLE_LUA_LUASAMPLE_HH
#define MOTOR_SAMPLE_LUA_LUASAMPLE_HH

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
    scoped< const Package > const             m_mainPackage;

public:
    explicit LuaSample(const Plugin::Context& context);
    ~LuaSample() override;
};

}  // namespace Motor

#endif
