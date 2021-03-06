/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PLUGIN_PLUGIN_HH_
#define MOTOR_PLUGIN_PLUGIN_HH_
/**************************************************************************************************/
#include <motor/plugin/stdafx.h>
#include <motor/plugin/dynobject.hh>
#include <motor/plugin/hook.hh>

#include <motor/filesystem/folder.meta.hh>
#include <motor/resource/resourcemanager.hh>
#include <motor/scheduler/scheduler.hh>

namespace Motor {

namespace Meta {
struct Class;
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
    Context(weak< Resource::ResourceManager > manager    = weak< Resource::ResourceManager >(),
            ref< Folder >                     dataFolder = ref< Folder >(),
            weak< Scheduler >                 scheduler  = weak< Scheduler >());
};

template < typename Interface >
class Plugin
{
private:
    inamespace                        m_name;
    weak< Resource::ResourceManager > m_resourceManager;
    DynamicObject*                    m_dynamicObject;
    Interface*                        m_interface;
    i_u32*                            m_refCount;

private:
    typedef Interface*(CreateFunction)(const Context& context);
    typedef void(DestroyFunction)(Interface* instance, weak< Resource::ResourceManager > manager);
    typedef const Meta::Class*(GetPluginNamespace)();

public:
    enum PreloadType
    {
        Preload
    };

public:
    Plugin();
    Plugin(const inamespace& pluginName, PreloadType preload);
    Plugin(const inamespace& pluginName, const Context& context);
    Plugin(const Plugin& other);
    ~Plugin();
    Plugin& operator=(Plugin other);

    Interface* operator->()
    {
        return m_interface;
    }
    const Interface* operator->() const
    {
        return m_interface;
    }
    operator const void*() const
    {
        return m_dynamicObject ? m_dynamicObject->operator const void*() : 0;
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

    void swap(Plugin& other);
};

}  // namespace Plugin
}  // namespace Motor

#include <motor/plugin/plugin.inl>

/**************************************************************************************************/
#endif
