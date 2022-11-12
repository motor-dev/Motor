/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <Cocoa/Cocoa.h>

namespace Motor { namespace Windowing {

class Renderer::PlatformRenderer : public minitl::refcountable
{
private:
    NSAutoreleasePool* m_pool;
    NSApplication*     m_application;

public:
    PlatformRenderer();
    ~PlatformRenderer();
    void flush();
};

}}  // namespace Motor::Windowing
