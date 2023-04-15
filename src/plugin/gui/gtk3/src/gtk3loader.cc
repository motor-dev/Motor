/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gobject.hh>
#include <gtk3loader.hh>

namespace Motor { namespace Gtk3 {

Gtk3Loader::Gtk3Loader(const Plugin::Context& pluginContext)
    : ILoader()
    , m_resourceManager(pluginContext.resourceManager)
{
    // m_resourceManager->attach(GObject::gObjectClass(), this);
}

Gtk3Loader::~Gtk3Loader()
{
    // m_resourceManager->detach(GObject::gObjectClass(), this);
}

void Gtk3Loader::load(weak< const Resource::IDescription > description,
                      Resource::Resource&                  resource)
{
    motor_forceuse(description);
    motor_forceuse(resource);
}

void Gtk3Loader::reload(weak< const Resource::IDescription > oldDescription,
                        weak< const Resource::IDescription > newDescription,
                        Resource::Resource&                  resource)
{
    motor_forceuse(oldDescription);
    motor_forceuse(newDescription);
    motor_forceuse(resource);
}

void Gtk3Loader::unload(weak< const Resource::IDescription > /*description*/,
                        Resource::Resource& resource)
{
    resource.clearRefHandle();
}

}}  // namespace Motor::Gtk3

MOTOR_PLUGIN_REGISTER(Motor::Gtk3::Gtk3Loader)