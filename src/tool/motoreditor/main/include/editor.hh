/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    Plugin::Plugin< void > const              m_renderer;
    Plugin::Plugin< Resource::ILoader > const m_packageManager;
    Plugin::Plugin< Resource::ILoader > const m_luaScripting;
    ref< const Package > const                m_mainPackage;

public:
    explicit Editor(const Plugin::Context& context);
    ~Editor() override;
};

}}  // namespace Motor::Editor
