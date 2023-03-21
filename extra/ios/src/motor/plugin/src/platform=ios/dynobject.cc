/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/core/environment.hh>
#include <motor/plugin/dynobject.hh>

#if !MOTOR_STATIC

#    include <dlfcn.h>

#    ifndef PLUGIN_PREFIX
#        define PLUGIN_PREFIX "lib"
#    endif
#    ifndef PLUGIN_EXT
#        define PLUGIN_EXT ".so"
#    endif

#    define PLUGIN_FILE_NAME PLUGIN_PREFIX "{0}" PLUGIN_EXT

namespace Motor { namespace Plugin {

DynamicObject::Handle DynamicObject::load(const inamespace& pluginName, const ipath& pluginPath)
{
    motor_forceuse(pluginPath);
    const minitl::format_buffer< 1024u > pluginFile
        = minitl::format< 1024u >(FMT(PLUGIN_FILE_NAME), pluginName);
    motor_info_format(Log::plugin(), "loading dynamic object {0}", pluginName);
    void* handle = dlopen(pluginFile, RTLD_NOW | RTLD_LOCAL);
    if(!handle)
    {
        motor_error_format(Log::plugin(), "Error loading dynamic object {0}: {1}", pluginName,
                           dlerror());
    }
    return handle;
}

void DynamicObject::unload(Handle handle)
{
    // On iPhone, unloading a plugin will not call static destructors
    // They will still be called at program shutdown
    // So we can't unload a shared object
    // dlclose(handle);
    motor_forceuse(handle);
}

void* DynamicObject::getSymbolInternal(Handle handle, const istring& name)
{
    return dlsym(handle, name.c_str());
}

}}  // namespace Motor::Plugin

#endif
