/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <textsample.hh>

namespace Motor {

TextSample::TextSample(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler)
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_textManager(inamespace("plugin.graphics.text"), pluginContext())
    , m_3ddx(inamespace("plugin.graphics.Dx9"), pluginContext())
    , m_3dgl(inamespace("plugin.graphics.GL4"), pluginContext())
    , m_mainPackage(scoped< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-text.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

TextSample::~TextSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
