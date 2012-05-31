/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <system/stdafx.h>
#include    <system/plugin.hh>
#include    <core/environment.hh>
#include    <rtti/classinfo.script.hh>

#include    <dlfcn.h>

#ifndef     PLUGIN_PREFIX
# define    PLUGIN_PREFIX "lib"
#endif
#ifndef     PLUGIN_EXT
# define    PLUGIN_EXT ".so"
#endif

#define BE_PLUGIN_NAMESPACE_REGISTER_NAMED(name)                                                \
    BE_PLUGIN_NAMESPACE_CREATE_(name)                                                           \
    extern "C" BE_EXPORT const BugEngine::RTTI::Class* be_pluginNamespace()                     \
    {                                                                                           \
        return BugEngine::be_##name##_Namespace().operator->();                                 \
    }
#define BE_PLUGIN_NAMESPACE_REGISTER_(name)                                                     \
    BE_PLUGIN_NAMESPACE_REGISTER_NAMED(name)
#define BE_PLUGIN_NAMESPACE_REGISTER()                                                          \
    BE_PLUGIN_NAMESPACE_REGISTER_(BE_PROJECTSHORTNAME)

#define BE_PLUGIN_REGISTER_NAMED(name, interface, klass)                                        \
    BE_PLUGIN_NAMESPACE_REGISTER_NAMED(name);                                                   \
    extern "C" BE_EXPORT interface* be_createPlugin (const ::BugEngine::PluginContext& context) \
    {                                                                                           \
        void* m = ::BugEngine::Arena::general().alloc<klass>();                                 \
        return new(m) klass(context);                                                           \
    }                                                                                           \
    extern "C" BE_EXPORT void be_destroyPlugin(klass* cls)                                      \
    {                                                                                           \
        minitl::checked_destroy(cls);                                                           \
        ::BugEngine::Arena::general().free(cls);                                                \
    }
#define BE_PLUGIN_REGISTER_NAMED_(name, interface, klass)                                       \
    BE_PLUGIN_REGISTER_NAMED(name, interface, klass)
#define BE_PLUGIN_REGISTER(interface, klass)                                                    \
    BE_PLUGIN_REGISTER_NAMED_(BE_PROJECTSHORTNAME, interface, klass)


namespace BugEngine
{

static void* loadLibrary(const inamespace& pluginName)
{
    minitl::format<> plugingFile = minitl::format<>(PLUGIN_PREFIX "%s" PLUGIN_EXT) | pluginName;
    const ipath& pluginDir = Environment::getEnvironment().getDataDirectory();
    static const ipath pluginSubdir = ipath("plugins");
    minitl::format<ifilename::MaxFilenameLength> pluginPath = (pluginDir + pluginSubdir + ifilename(plugingFile.c_str())).str();
    be_info("loading plugin %s (%s)" | pluginName | pluginPath);
    void* handle = dlopen(pluginPath.c_str(), RTLD_NOW|RTLD_LOCAL);
    if (!handle)
    {
        be_error(dlerror());
    }
    return handle;
}

template< typename Interface >
Plugin<Interface>::Plugin(const inamespace &pluginName, PreloadType /*preload*/)
:   m_handle(loadLibrary(pluginName))
,   m_interface(0)
,   m_refCount(new (Arena::general()) i_u32(1))
{
}

template< typename Interface >
Plugin<Interface>::Plugin(const inamespace &pluginName, const PluginContext& context)
:   m_handle(loadLibrary(pluginName))
,   m_interface(0)
,   m_refCount(new (Arena::general()) i_u32(1))
{
    if  (m_handle)
    {
        Interface* (*_init)(const PluginContext&) = reinterpret_cast<Interface* (*)(const PluginContext&)>(reinterpret_cast<size_t>(dlsym(m_handle, "be_createPlugin")));
        be_assert(_init, "could not find method _init in plugin %s" | pluginName);
        m_interface = (*_init)(context);
    }
}

template< typename Interface >
Plugin<Interface>::~Plugin(void)
{
    if (!--*m_refCount)
    {
        if (m_handle && m_interface)
        {
            void (*_fini)(Interface*) = reinterpret_cast<void (*)(Interface*)>(reinterpret_cast<size_t>(dlsym(m_handle, "be_destroyPlugin")));
            if (_fini)
                _fini(m_interface);
            //dlclose(m_handle); crashes on systems with TLS
        }
        minitl::checked_destroy(m_refCount);
        Arena::general().free(m_refCount);
    }
}

template< typename Interface >
Plugin<Interface>::Plugin(const Plugin<Interface>& other)
    :   m_handle(other.m_handle)
    ,   m_interface(other.m_interface)
    ,   m_refCount(other.m_refCount)
{
    (*m_refCount)++;
}

template< typename Interface >
Plugin<Interface>& Plugin<Interface>::operator =(const Plugin<Interface>& other)
{
    *(other->m_refCount)++;
    if (! --*m_refCount)
    {
        if (m_handle && m_interface)
        {
            void (*_fini)(Interface*) = reinterpret_cast<void (*)(Interface*)>(reinterpret_cast<size_t>(dlsym(m_handle, "be_destroyPlugin")));
            if (_fini)
                _fini(m_interface);
            //dlclose(m_handle); crashes on systems with TLS
        }
        minitl::checked_destroy(m_refCount);
        Arena::general().free(m_refCount);
    }
    m_refCount = other.m_refCount;
    m_handle = other.m_handle;
    m_interface = other.m_interface;
    return *this;
}

template< typename Interface >
raw<const RTTI::Class> Plugin<Interface>::pluginNamespace() const
{
    if (m_handle)
    {
        const RTTI::Class* (*be_pluginNamespace)() = reinterpret_cast<const RTTI::Class* (*)()>(reinterpret_cast<size_t>(dlsym(m_handle, "be_pluginNamespace")));
        if (be_pluginNamespace)
        {
            raw<const RTTI::Class> ci = {(*be_pluginNamespace)()};
            return ci;
        }
    }
    raw<const RTTI::Class> ci = {0};
    return ci;
}




}

