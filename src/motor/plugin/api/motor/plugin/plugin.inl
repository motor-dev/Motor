/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin/stdafx.h>
#include <motor/core/environment.hh>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/value.hh>
#include <motor/plugin/dynobjectlist.hh>
#include <motor/plugin/hook.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Plugin {

#define MOTOR_PLUGIN_NAMESPACE_CREATE_(name)                                                       \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##name##_Namespace()                                                  \
    {                                                                                              \
        static Meta::Class ci                                                                      \
            = {istring(#name), 0,      0,   Meta::ClassType_Namespace,         {0}, {0}, {0}, {0}, \
               {0, 0},         {0, 0}, {0}, Meta::OperatorTable::s_emptyTable, 0,   0};            \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    }

#define MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED__(name, id)                                          \
    MOTOR_PLUGIN_NAMESPACE_CREATE_(id)                                                             \
    namespace Motor {                                                                              \
    minitl::intrusive_list< Motor::Plugin::IPluginHook > g_pluginHooks_##id;                       \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT                                                                           \
    minitl::refcountable* motor_createPlugin(const ::Motor::Plugin::Context& context)              \
    {                                                                                              \
        for(minitl::intrusive_list< Motor::Plugin::IPluginHook >::iterator it                      \
            = Motor::g_pluginHooks_##id.begin();                                                   \
            it != Motor::g_pluginHooks_##id.end(); ++it)                                           \
            it->onload(context);                                                                   \
        return 0;                                                                                  \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT void motor_destroyPlugin(                                                 \
        minitl::refcountable* cls, weak< Motor::Resource::ResourceManager > manager)               \
    {                                                                                              \
        motor_forceuse(cls);                                                                       \
        for(minitl::intrusive_list< Motor::Plugin::IPluginHook >::iterator it                      \
            = Motor::g_pluginHooks_##id.begin();                                                   \
            it != Motor::g_pluginHooks_##id.end(); ++it)                                           \
            it->onunload(manager);                                                                 \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT const Motor::Meta::Class* motor_pluginNamespace()                         \
    {                                                                                              \
        return Motor::motor_##id##_Namespace().operator->();                                       \
    }                                                                                              \
    _MOTOR_REGISTER_PLUGIN(id, name);                                                              \
    _MOTOR_REGISTER_METHOD(id, motor_createPlugin);                                                \
    _MOTOR_REGISTER_METHOD(id, motor_destroyPlugin);                                               \
    _MOTOR_REGISTER_METHOD(id, motor_pluginNamespace);

#define MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED_(name, id)                                           \
    MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED__(name, id)

#define MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED(name)                                                \
    MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED_(name, name)

#define MOTOR_PLUGIN_NAMESPACE_REGISTER()                                                          \
    MOTOR_PLUGIN_NAMESPACE_REGISTER_NAMED_(MOTOR_PROJECTNAME, MOTOR_PROJECTID)

#define MOTOR_PLUGIN_REGISTER_NAMED__(name, id, create)                                            \
    MOTOR_PLUGIN_NAMESPACE_CREATE_(id);                                                            \
    namespace Motor {                                                                              \
    minitl::intrusive_list< Motor::Plugin::IPluginHook > g_pluginHooks_##id;                       \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT                                                                           \
    minitl::refcountable* motor_createPlugin(const ::Motor::Plugin::Context& context)              \
    {                                                                                              \
        for(minitl::intrusive_list< Motor::Plugin::IPluginHook >::iterator it                      \
            = Motor::g_pluginHooks_##id.begin();                                                   \
            it != Motor::g_pluginHooks_##id.end(); ++it)                                           \
            it->onload(context);                                                                   \
        ref< minitl::refcountable > r = (*create)(context);                                        \
        if(r) r->addref();                                                                         \
        return r.operator->();                                                                     \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT void motor_destroyPlugin(                                                 \
        minitl::refcountable* cls, weak< Motor::Resource::ResourceManager > manager)               \
    {                                                                                              \
        if(cls) cls->decref();                                                                     \
        for(minitl::intrusive_list< Motor::Plugin::IPluginHook >::iterator it                      \
            = Motor::g_pluginHooks_##id.begin();                                                   \
            it != Motor::g_pluginHooks_##id.end(); ++it)                                           \
            it->onunload(manager);                                                                 \
    }                                                                                              \
    _MOTOR_PLUGIN_EXPORT const Motor::Meta::Class* motor_pluginNamespace()                         \
    {                                                                                              \
        return Motor::motor_##id##_Namespace().operator->();                                       \
    }                                                                                              \
    _MOTOR_REGISTER_PLUGIN(id, name);                                                              \
    _MOTOR_REGISTER_METHOD(id, motor_createPlugin);                                                \
    _MOTOR_REGISTER_METHOD(id, motor_destroyPlugin);                                               \
    _MOTOR_REGISTER_METHOD(id, motor_pluginNamespace);

#define MOTOR_PLUGIN_REGISTER_NAMED_(name, id, create)                                             \
    MOTOR_PLUGIN_REGISTER_NAMED__(name, id, create)

#define MOTOR_PLUGIN_REGISTER_NAMED(name, create) MOTOR_PLUGIN_REGISTER_NAMED_(name, name, create)

#define MOTOR_PLUGIN_REGISTER_CREATE(create)                                                       \
    MOTOR_PLUGIN_REGISTER_NAMED_(MOTOR_PROJECTNAME, MOTOR_PROJECTID, create)

#define MOTOR_PLUGIN_REGISTER__(klass, project)                                                    \
    static ref< klass > create(const Motor::Plugin::Context& context)                              \
    {                                                                                              \
        return ref< klass >::create(Motor::Arena::game(), context);                                \
    }                                                                                              \
    MOTOR_PLUGIN_REGISTER_CREATE(&create)

#define MOTOR_PLUGIN_REGISTER_(klass, project) MOTOR_PLUGIN_REGISTER__(klass, project)

#define MOTOR_PLUGIN_REGISTER(klass) MOTOR_PLUGIN_REGISTER_(klass, MOTOR_PROJECTID)

template < typename T >
Plugin< T >::Plugin()
    : m_name("")
    , m_dynamicObject()
    , m_interface(0)
    , m_refCount(new(Arena::general()) i_u32(i_u32::create(1)))
{
}

template < typename T >
Plugin< T >::Plugin(const inamespace& pluginName, PreloadType /*preload*/)
    : m_name(pluginName)
    , m_dynamicObject(new(Arena::general()) DynamicObject(pluginName, ipath("plugin")))
    , m_interface(0)
    , m_refCount(new(Arena::general()) i_u32(i_u32::create(1)))
{
}

template < typename T >
Plugin< T >::Plugin(const inamespace& pluginName, const Context& context)
    : m_name(pluginName)
    , m_resourceManager(context.resourceManager)
    , m_dynamicObject(new(Arena::general()) DynamicObject(pluginName, ipath("plugin")))
    , m_interface(0)
    , m_refCount(new(Arena::general()) i_u32(i_u32::create(1)))
{
    if(*m_dynamicObject)
    {
        CreateFunction* create = m_dynamicObject->getSymbol< CreateFunction >("motor_createPlugin");
        motor_assert_recover(create, "could not load method motor_createPlugin", return );
        m_interface = (*create)(context);
    }
}

template < typename T >
Plugin< T >::~Plugin()
{
    if(--*m_refCount == 0)
    {
        if(m_interface)
        {
            DestroyFunction* destroy
                = m_dynamicObject->getSymbol< DestroyFunction >("motor_destroyPlugin");
            motor_assert(destroy, "could not load method motor_destroyPlugin");
            (*destroy)(m_interface, m_resourceManager);
        }
        if(m_dynamicObject)
        {
            m_dynamicObject->~DynamicObject();
            Arena::general().free(m_dynamicObject);
        }
        Arena::general().free(m_refCount);
    }
}

template < typename T >
Plugin< T >::Plugin(const Plugin& other)
    : m_name(other.m_name)
    , m_dynamicObject(other.m_dynamicObject)
    , m_interface(other.m_interface)
    , m_refCount(other.m_refCount)
{
    ++*m_refCount;
}

template < typename T >
Plugin< T >& Plugin< T >::operator=(Plugin other)
{
    other.swap(*this);
    return *this;
}

template < typename T >
void Plugin< T >::swap(Plugin& other)
{
    minitl::swap(m_name, other.m_name);
    minitl::swap(m_dynamicObject, other.m_dynamicObject);
    minitl::swap(m_interface, other.m_interface);
    minitl::swap(m_refCount, other.m_refCount);
}

template < typename T >
raw< const Meta::Class > Plugin< T >::pluginNamespace() const
{
    if(m_dynamicObject && *m_dynamicObject)
    {
        GetPluginNamespace* getNamespace
            = m_dynamicObject->getSymbol< GetPluginNamespace >("motor_pluginNamespace");
        if(getNamespace)
        {
            raw< const Meta::Class > ci = {(*getNamespace)()};
            return ci;
        }
    }
    raw< const Meta::Class > ci = {0};
    return ci;
}

}}  // namespace Motor::Plugin
