/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/scheduler/kernel/imemoryhost.hh>

namespace Motor { namespace OpenGL {

class motor_api(GL4) GLMemoryHost : public KernelScheduler::IMemoryHost
{
public:
    GLMemoryHost();
    ~GLMemoryHost();

    void release(weak< KernelScheduler::IMemoryBuffer > buffer);
};

}}  // namespace Motor::OpenGL
