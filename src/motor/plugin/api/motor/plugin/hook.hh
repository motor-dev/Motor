/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_HOOK_HH
#define MOTOR_PLUGIN_HOOK_HH

#include <motor/plugin/stdafx.h>
#include <motor/core/preproc.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor { namespace Plugin {
struct Context;
class IPluginHook;
}}  // namespace Motor::Plugin

namespace Motor { namespace Plugin {

typedef minitl::intrusive_list< Motor::Plugin::IPluginHook > HookList;

class motor_api(PLUGIN) IPluginHook : public minitl::intrusive_list< IPluginHook >::item
{
protected:
    explicit IPluginHook(HookList & owner)
    {
        owner.push_back(*this);
    }
    virtual ~IPluginHook();

public:
    virtual void onload(const Context& context)                             = 0;
    virtual void onunload(const weak< Resource::ResourceManager >& manager) = 0;
};

template < typename T >
class PluginHook : public IPluginHook
{
private:
    T m_hook;

public:
    PluginHook(HookList& list, const T& t) : IPluginHook(list), m_hook(t)
    {
    }
    ~PluginHook() override = default;
    void onload(const Context& context) override
    {
        m_hook.onload(context);
    }
    void onunload(const weak< Resource::ResourceManager >& manager) override
    {
        m_hook.onunload(manager);
    }
};

}}  // namespace Motor::Plugin

#endif
