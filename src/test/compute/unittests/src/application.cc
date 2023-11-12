/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */

#include <stdafx.h>
#include <motor/plugin/plugin.hh>
#include <application.hh>

namespace Motor { namespace Test { namespace Compute { namespace UnitTests {

UnitTestsApplication::UnitTestsApplication(const Plugin::Context& context)
    : Application(context.resourceManager, context.scheduler, ipath("test/compute/unittests"))
    , m_packageManager(inamespace("plugin.scripting.package"), pluginContext())
    , m_computeCudaModule(inamespace("plugin.compute.cuda"), pluginContext())
    , m_computeCLModule(inamespace("plugin.compute.opencl"), pluginContext())
    , m_mainPackage(ref< Package >::create(
          Arena::game(), pluginContext().dataFolder->openFile(ifilename("unittests.pkg"))))
{
    pluginContext().resourceManager->load(m_mainPackage);
}

UnitTestsApplication::~UnitTestsApplication()
{
    pluginContext().resourceManager->unload(m_mainPackage);
}

}}}}  // namespace Motor::Test::Compute::UnitTests

MOTOR_PLUGIN_REGISTER(Motor::Test::Compute::UnitTests::UnitTestsApplication)
