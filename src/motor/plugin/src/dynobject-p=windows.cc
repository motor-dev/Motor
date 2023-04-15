/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/core/environment.hh>
#include <motor/plugin/dynobject.hh>

#if !MOTOR_STATIC

#    define WIN32_LEAN_AND_MEAN
#    ifndef NOMINMAX
#        define NOMINMAX
#    endif
#    include <windows.h>

#    include <winerror.h>

namespace Motor { namespace Plugin {

DynamicObject::Handle DynamicObject::load(const inamespace& pluginName, const ipath& pluginPath)
{
    SetLastError(0);
    minitl::format_buffer< 1024u > plugingFile
        = minitl::format< 1024u >(FMT("{0}.dll"), pluginName);
    const ipath&        pluginDir = Environment::getEnvironment().getDataDirectory();
    ifilename::Filename fullPath  = (pluginDir + pluginPath + ifilename(plugingFile.c_str())).str();
    motor_info_format(Log::plugin(), "loading dynamic object {0} ({1})", pluginName, fullPath.name);
    HANDLE h = LoadLibrary(fullPath.name);
    if(!h)
    {
        char* errorMessage = 0;
        int   errorCode    = ::GetLastError();
        FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, NULL, errorCode,
                      MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                      reinterpret_cast< LPSTR >(&errorMessage), 0, NULL);
        motor_error_format(Log::plugin(), "Error loading dynamic object {0}: {1}", pluginName,
                           errorMessage);
        ::LocalFree(errorMessage);
    }
    return h;
}

void DynamicObject::unload(Handle handle)
{
    FreeLibrary(static_cast< HMODULE >(handle));
}

void* DynamicObject::getSymbolInternal(Handle handle, const istring& name)
{
    return (void*)(GetProcAddress(static_cast< HINSTANCE >(handle), name.c_str()));
}

}}  // namespace Motor::Plugin
#endif
