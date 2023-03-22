/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/core/environment.hh>
#include <motor/filesystem/diskfolder.meta.hh>
#include <luasample.hh>
/*
namespace Motor {

LuaSample::LuaSample(const Plugin::Context& context)
    : Application(
        ref< DiskFolder >::create(Arena::game(), Environment::getEnvironment().getDataDirectory()),
        context.resourceManager, context.scheduler)
    , m_packageManager("plugin.scripting.package", pluginContext())
    , m_luaManager("plugin.scripting.lua", pluginContext())
    , m_mainPackage(ref< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-lua.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

LuaSample::~LuaSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
*/