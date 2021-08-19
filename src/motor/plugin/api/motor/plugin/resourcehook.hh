/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PLUGIN_RESOURCEHOOK_HH_
#define MOTOR_PLUGIN_RESOURCEHOOK_HH_
/**************************************************************************************************/
#include <motor/plugin/stdafx.h>
#include <motor/plugin/hook.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Plugin {

template < typename RESOURCE >
struct ResourceHook
{
private:
    ref< const RESOURCE > m_resource;

public:
    ResourceHook(ref< const RESOURCE > resource) : m_resource(resource)
    {
    }
    void onload(const Context& context)
    {
        context.resourceManager->load(m_resource);
    }
    void onunload(weak< Resource::ResourceManager > manager)
    {
        manager->unload(m_resource);
    }
};

}}  // namespace Motor::Plugin

/**************************************************************************************************/
#endif
