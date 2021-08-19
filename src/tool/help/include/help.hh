/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_HELP_HELP_HH_
#define MOTOR_HELP_HELP_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/application.hh>
#include <motor/plugin.scripting.package/package.script.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>

namespace Motor {

class Help : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_ui;
    ref< const Package > const                m_mainPackage;

public:
    Help(const Plugin::Context& context);
    ~Help();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
