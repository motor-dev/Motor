/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_EDITOR_EDITOR_HH_
#define MOTOR_EDITOR_EDITOR_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.script.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {
class Folder;
class Package;
class IKernelScheduler;
}  // namespace Motor

namespace Motor { namespace Editor {

class Editor : public Application
{
private:
    Plugin::Plugin< void > const              m_renderer;
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_luaScripting;
    ref< const Package > const                m_mainPackage;

public:
    Editor(const Plugin::Context& context);
    ~Editor();
};

}}  // namespace Motor::Editor

/**************************************************************************************************/
#endif
