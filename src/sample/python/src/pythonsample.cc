/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <pythonsample.hh>

namespace Motor {

PythonSample::PythonSample(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler)
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_pythonManager(inamespace("plugin.scripting.python"), pluginContext())
    , m_mainPackage(ref< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(istring("sample-python.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

PythonSample::~PythonSample()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}  // namespace Motor
