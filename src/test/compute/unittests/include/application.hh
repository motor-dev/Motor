/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#pragma once

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
    ref< const Package > const                m_mainPackage;

public:
    explicit UnitTestsApplication(const Plugin::Context& context);
    ~UnitTestsApplication() override;
};

}}}}  // namespace Motor::Test::Compute::UnitTests
