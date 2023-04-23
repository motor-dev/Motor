/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/classinfo.meta.hh>
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

    void load(const weak< const Resource::IDescription >& script,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldScript,
                const weak< const Resource::IDescription >& newScript,
                Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         resource) override;
};

}}  // namespace Motor::Gtk3
