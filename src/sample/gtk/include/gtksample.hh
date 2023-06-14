/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SAMPLE_GTK_GTKSAMPLE_HH
#define MOTOR_SAMPLE_GTK_GTKSAMPLE_HH

#include <stdafx.h>
#include <motor/application.hh>
#include <motor/filesystem/folder.meta.hh>
#include <motor/plugin.scripting.package/package.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {

class GtkSample : public Application
{
private:
    Plugin::Plugin< Resource::ILoader > const         m_packageManager;
    Plugin::Plugin< minitl::pointer > const           m_textManager;
    Plugin::Plugin< Resource::ResourceManager > const m_gtkManager;
    ref< const Package > const                        m_mainPackage;

public:
    explicit GtkSample(const Plugin::Context& context);
    ~GtkSample() override;
};

}  // namespace Motor

#endif
