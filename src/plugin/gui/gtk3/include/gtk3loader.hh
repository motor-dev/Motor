/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GUI_GTK3_GTK3LOADER_HH_
#define MOTOR_GUI_GTK3_GTK3LOADER_HH_
/**************************************************************************************************/
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>

namespace Motor { namespace Gtk3 {

class Gtk3Loader : public Resource::ILoader
{
private:
    weak< Resource::ResourceManager > m_resourceManager;

public:
    Gtk3Loader(const Plugin::Context& pluginContext);
    ~Gtk3Loader();

    virtual void load(weak< const Resource::IDescription > script,
                      Resource::Resource&                  resource) override;
    virtual void reload(weak< const Resource::IDescription > oldScript,
                        weak< const Resource::IDescription > newScript,
                        Resource::Resource&                  resource) override;
    virtual void unload(weak< const Resource::IDescription > description,
                        Resource::Resource&                  resource) override;
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
