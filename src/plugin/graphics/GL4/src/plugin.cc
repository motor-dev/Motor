/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <motor/plugin/plugin.hh>

static minitl::ref< Motor::OpenGL::GLRenderer > create(const Motor::Plugin::Context& context)
{
    minitl::ref< Motor::OpenGL::GLRenderer > renderer;
    renderer = minitl::ref< Motor::OpenGL::GLRenderer >::create(Motor::Arena::game(), context);
    if(!renderer->success())
    {
        renderer = minitl::ref< Motor::OpenGL::GLRenderer >();
    }
    return renderer;
}

MOTOR_PLUGIN_REGISTER_CREATE(&create);
