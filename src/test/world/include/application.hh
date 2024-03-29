/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#ifndef MOTOR_TEST_WORLD_APPLICATION_HH
#define MOTOR_TEST_WORLD_APPLICATION_HH

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Test { namespace World {

class WorldTestApplication : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    scoped< const Package > const             m_mainPackage;

public:
    explicit WorldTestApplication(const Plugin::Context& context);
    ~WorldTestApplication() override;
};

}}}  // namespace Motor::Test::World

#endif
