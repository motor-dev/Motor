/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_TOOL_MOTOREDITOR_MAIN_EDITOR_HH
#define MOTOR_TOOL_MOTOREDITOR_MAIN_EDITOR_HH

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {
class Folder;
class Package;
}  // namespace Motor

namespace Motor { namespace Editor {

class Editor : public Application
{
private:
    Plugin::Plugin< minitl::pointer > const   m_renderer;
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_luaScripting;
    scoped< const Package > const             m_mainPackage;

public:
    explicit Editor(const Plugin::Context& context);
    ~Editor() override;
};

}}  // namespace Motor::Editor

#endif
