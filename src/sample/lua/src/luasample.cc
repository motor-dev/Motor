/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <luasample.hh>

namespace Motor {

LuaSample::LuaSample(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler)
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_luaManager(inamespace("plugin.scripting.lua"), pluginContext())
    , m_mainPackage(scoped< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-lua.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

LuaSample::~LuaSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
