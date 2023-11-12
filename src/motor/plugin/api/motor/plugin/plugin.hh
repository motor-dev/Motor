/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_PLUGIN_HH
#define MOTOR_PLUGIN_PLUGIN_HH

#include <motor/plugin/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/plugin/hook.hh>

#include <motor/filesystem/folder.meta.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor {

namespace Meta {
class Class;
}

namespace Resource {
class ResourceManager;
}
class Folder;
class Scheduler;

namespace Plugin {

struct motor_api(PLUGIN) Context
{
    weak< Resource::ResourceManager > resourceManager;
    ref< Folder >                     dataFolder;
    weak< Scheduler >                 scheduler;
    explicit Context(const weak< Resource::ResourceManager >& manager
                     = weak< Resource::ResourceManager >(),
                     const ref< Folder >&     dataFolder = ref< Folder >(),
                     const weak< Scheduler >& scheduler  = weak< Scheduler >());
};

template < typename Interface >
class Plugin
{
private:
    inamespace                        m_name;
    weak< Resource::ResourceManager > m_resourceManager;
    DynamicObject*                    m_dynamicObject;
    scoped< minitl::pointer >         m_interface;

private:
    typedef void(CreateFunction)(minitl::scoped< minitl::pointer >& result, const Context& context);
    typedef void(DestroyFunction)(minitl::scoped< minitl::pointer >&& interface,
                                  weak< Resource::ResourceManager >   manager);
    typedef const Meta::Class*(GetPluginNamespace)();

public:
    enum PreloadType
    {
        Preload
    };

public:
    Plugin(const Plugin& other)            = delete;
    Plugin& operator=(const Plugin& other) = delete;

public:
    Plugin();
    Plugin(const inamespace& pluginName, PreloadType preload);
    Plugin(const inamespace& pluginName, const Context& context);
    Plugin(Plugin&& other) noexcept;
    ~Plugin();
    Plugin& operator=(Plugin&& other) noexcept;

    Interface* operator->()
    {
        return motor_checked_cast< Interface >(m_interface.operator->());
    }
    const Interface* operator->() const
    {
        return motor_checked_cast< const Interface >(m_interface.operator->());
    }
    operator const void*() const  // NOLINT(google-explicit-constructor)
    {
        return m_dynamicObject ? m_dynamicObject->operator const void*() : nullptr;
    }
    bool operator!() const
    {
        return !m_dynamicObject || !*m_dynamicObject;
    }

    raw< const Meta::Class > pluginNamespace() const;
    const inamespace&        name() const
    {
        return m_name;
    }
};

}  // namespace Plugin
}  // namespace Motor

#include <motor/plugin/plugin.inl>

#endif
