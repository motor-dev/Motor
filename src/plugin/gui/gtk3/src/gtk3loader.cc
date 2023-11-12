/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gobject.hh>
#include <gtk3loader.hh>
#include <gtkresourcedescription.meta.hh>

namespace Motor { namespace Gtk3 {

Gtk3Loader::Gtk3Loader(const Plugin::Context& pluginContext)
    : ILoader()
    , m_resourceManager(pluginContext.resourceManager)
{
    m_resourceManager->attach(motor_class< GtkResourceDescription >(), this);
}

Gtk3Loader::~Gtk3Loader()
{
    motor_forceuse(this);
    m_resourceManager->detach(motor_class< GtkResourceDescription >(), this);
}

void Gtk3Loader::load(const weak< const Resource::IDescription >& description,
                      Resource::Resource&                         resource)
{
    motor_forceuse(description);
    motor_forceuse(resource);
}

void Gtk3Loader::reload(const weak< const Resource::IDescription >& oldDescription,
                        const weak< const Resource::IDescription >& newDescription,
                        Resource::Resource&                         resource)
{
    motor_forceuse(oldDescription);
    motor_forceuse(newDescription);
    motor_forceuse(resource);
}

void Gtk3Loader::unload(const weak< const Resource::IDescription >& /*description*/,
                        Resource::Resource& resource)
{
    resource.clearHandle();
}

}}  // namespace Motor::Gtk3

MOTOR_PLUGIN_REGISTER(Motor::Gtk3::Gtk3Loader)