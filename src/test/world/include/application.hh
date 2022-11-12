/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Test { namespace World {

class WorldTestApplication : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    ref< const Package > const                m_mainPackage;

public:
    WorldTestApplication(const Plugin::Context& context);
    ~WorldTestApplication();
};

}}}  // namespace Motor::Test::World
