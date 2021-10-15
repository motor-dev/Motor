/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GUI_GTK3_GTK3LOADER_HH_
#define MOTOR_GUI_GTK3_GTK3LOADER_HH_
/**************************************************************************************************/
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>
#include <gtk3plugin.hh>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin;

class Gtk3Loader : public Resource::ILoader
{
private:
    weak< Resource::ResourceManager > m_resourceManager;

public:
    Gtk3Loader(const Plugin::Context& pluginContext);
    ~Gtk3Loader();

    virtual void load(weak< const Resource::Description > script,
                      Resource::Resource&                 resource) override;
    virtual void reload(weak< const Resource::Description > oldScript,
                        weak< const Resource::Description > newScript,
                        Resource::Resource&                 resource) override;
    virtual void unload(Resource::Resource& resource) override;
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
