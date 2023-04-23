/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.GL4/glmemoryhost.hh>

namespace Motor { namespace OpenGL {

GLMemoryHost::GLMemoryHost() : IMemoryHost("OpenGL")
{
}

GLMemoryHost::~GLMemoryHost() = default;

void GLMemoryHost::release(const weak< KernelScheduler::IMemoryBuffer >& buffer)
{
    motor_forceuse(buffer);
}

}}  // namespace Motor::OpenGL
