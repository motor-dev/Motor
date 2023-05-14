/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    explicit ResourceHook(ref< const RESOURCE > resource) : m_resource(resource)
    {
    }
    void onload(const Context& context)
    {
        context.resourceManager->load(m_resource);
    }
    void onunload(const weak< Resource::ResourceManager >& manager)
    {
        manager->unload(m_resource);
    }
};

}}  // namespace Motor::Plugin
