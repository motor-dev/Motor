/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_WINDOWING_DARWIN_RENDERER_HH_
#define MOTOR_WINDOWING_DARWIN_RENDERER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.windowing/stdafx.h>
#include <Cocoa/Cocoa.h>
#include <motor/plugin.graphics.windowing/renderer.hh>

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

/**************************************************************************************************/
#endif
