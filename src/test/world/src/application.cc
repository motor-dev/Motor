/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */

#include <stdafx.h>
#include <application.hh>

#include <motor/plugin/plugin.hh>

namespace Motor { namespace Test { namespace World {

WorldTestApplication::WorldTestApplication(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler, ipath("test/world"))
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_mainPackage(scoped< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(ifilename("worldtest.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

WorldTestApplication::~WorldTestApplication()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}}}  // namespace Motor::Test::World

MOTOR_PLUGIN_REGISTER(Motor::Test::World::WorldTestApplication)
