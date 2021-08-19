/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <loaders/rendertarget/glwindow.hh>

namespace Motor { namespace OpenGL {

void GLWindow::begin(ClearMode clear) const
{
    if(m_context)
    {
        setCurrent();
        if(clear == IRenderTarget::Clear)
        {
            glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
            glClear(GL_COLOR_BUFFER_BIT);
        }
    }
    motor_info("blabla");
}

void GLWindow::end(PresentMode presentMode) const
{
    if(m_context)
    {
        glFlush();
        if(presentMode == Present)
        {
            present();
        }
        clearCurrent();
    }
    motor_info("blabla");
}

}}  // namespace Motor::OpenGL
