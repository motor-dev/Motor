/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#ifndef MOTOR_TEST_COMPUTE_UNITTESTS_APPLICATION_HH
#define MOTOR_TEST_COMPUTE_UNITTESTS_APPLICATION_HH

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Test { namespace Compute { namespace UnitTests {

class UnitTestsApplication : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_computeCudaModule;
    Plugin::Plugin< Resource::ILoader > const m_computeCLModule;
    scoped< const Package > const             m_mainPackage;

public:
    explicit UnitTestsApplication(const Plugin::Context& context);
    ~UnitTestsApplication() override;
};

}}}}  // namespace Motor::Test::Compute::UnitTests

#endif
