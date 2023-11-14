/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <help.hh>

namespace Motor {

Help::Help(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler)
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_ui(inamespace("plugin.ui.console"), pluginContext())
    , m_mainPackage(scoped< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("help.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

Help::~Help()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
