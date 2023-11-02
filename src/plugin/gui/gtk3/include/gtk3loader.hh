/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GTK3LOADER_HH
#define MOTOR_PLUGIN_GUI_GTK3_GTK3LOADER_HH

#include <motor/plugin/plugin.hh>
#include <motor/resource/loader.hh>

namespace Motor { namespace Gtk3 {

class Gtk3Loader : public Resource::ILoader
{
private:
    weak< Resource::ResourceManager > m_resourceManager;

public:
    explicit Gtk3Loader(const Plugin::Context& pluginContext);
    ~Gtk3Loader() override;

    void load(const weak< const Resource::IDescription >& description,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldDescription,
                const weak< const Resource::IDescription >& newDescription,
                Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         resource) override;
};

}}  // namespace Motor::Gtk3

#endif
