/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    ref< const Package > const                m_mainPackage;

public:
    explicit Help(const Plugin::Context& context);
    ~Help() override;
};

}  // namespace Motor
