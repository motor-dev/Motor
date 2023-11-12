/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <motor/plugin/plugin.hh>

static scoped< Motor::OpenGL::GLRenderer > create(const Motor::Plugin::Context& context)
{
    auto renderer = scoped< Motor::OpenGL::GLRenderer >::create(Motor::Arena::game(), context);
    if(!renderer->success())
    {
        return {};
    }
    return renderer;
}

MOTOR_PLUGIN_REGISTER_CREATE(&create)
