/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <editor.hh>

namespace Motor { namespace Editor {

Editor::Editor(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler)
    , m_renderer(inamespace("plugin.graphics.GL4"), pluginContext())
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_luaScripting(inamespace("plugin.scripting.lua"), pluginContext())
    , m_mainPackage(scoped< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("main.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

Editor::~Editor()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}}  // namespace Motor::Editor
