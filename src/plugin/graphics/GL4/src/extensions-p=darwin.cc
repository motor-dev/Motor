/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <dlfcn.h>
#include <extensions.hh>

namespace Motor { namespace OpenGL {

Extension glGetExtension(const char* name)
{
    static void* image
        = dlopen("/System/Library/Frameworks/OpenGL.framework/Versions/Current/OpenGL", RTLD_LAZY);
    if(!image)
        return NULL;
    else
        return (Extension)dlsym(image, name);
}

}}  // namespace Motor::OpenGL
