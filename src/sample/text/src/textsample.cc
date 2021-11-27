/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/core/environment.hh>
#include <motor/filesystem/diskfolder.meta.hh>
#include <textsample.hh>

namespace Motor {

TextSample::TextSample(const Plugin::Context& context)
    : Application(
        ref< DiskFolder >::create(Arena::game(), Environment::getEnvironment().getDataDirectory()),
        context.resourceManager, context.scheduler)
    , m_packageManager("plugin.scripting.package", pluginContext())
    , m_textManager("plugin.graphics.text", pluginContext())
    , m_3ddx("plugin.graphics.Dx9", pluginContext())
    , m_3dgl("plugin.graphics.GL4", pluginContext())
    , m_mainPackage(ref< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-text.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

TextSample::~TextSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
