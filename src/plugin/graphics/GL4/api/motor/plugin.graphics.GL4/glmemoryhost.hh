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
    ~GLMemoryHost() override;

    void release(const weak< KernelScheduler::IMemoryBuffer >& buffer) override;
};

}}  // namespace Motor::OpenGL
