/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <GL/glx.h>
#include <extensions.hh>

namespace Motor { namespace OpenGL {

Extension glGetExtension(const char* name)
{
    return glXGetProcAddress((const GLubyte*)name);
}

}}  // namespace Motor::OpenGL
