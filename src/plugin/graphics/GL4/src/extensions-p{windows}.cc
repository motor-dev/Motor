/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <extensions.hh>

namespace Motor { namespace OpenGL {

Extension glGetExtension(const char* name)
{
    return (Extension)wglGetProcAddress(name);
}

}}  // namespace Motor::OpenGL
