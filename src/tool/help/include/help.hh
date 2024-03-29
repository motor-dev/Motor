/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_TOOL_HELP_HELP_HH
#define MOTOR_TOOL_HELP_HELP_HH

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>

namespace Motor {

class Help : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_ui;
    scoped< const Package > const             m_mainPackage;

public:
    explicit Help(const Plugin::Context& context);
    ~Help() override;
};

}  // namespace Motor

#endif
