/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/core/environment.hh>
#include <motor/filesystem/diskfolder.meta.hh>
#include <gtksample.hh>

namespace Motor {

GtkSample::GtkSample(const Plugin::Context& context)
    : Application(
        ref< DiskFolder >::create(Arena::game(), Environment::getEnvironment().getDataDirectory()),
        context.resourceManager, context.scheduler)
    , m_packageManager("plugin.scripting.package", pluginContext())
    , m_gtkManager("plugin.gui.gtk3", pluginContext())
    , m_mainPackage(ref< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-gtk.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

GtkSample::~GtkSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
