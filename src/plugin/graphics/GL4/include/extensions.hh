/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.GL4/stdafx.h>

namespace Motor { namespace OpenGL {

typedef void (*Extension)();
Extension glGetExtension(const char* name);

struct ShaderExtensions
{
    typedef GLhandleARB(APIENTRY* glCreateProgramObjectARBProc)();
    typedef void(APIENTRY* glDeleteProgramObjectARBProc)(GLhandleARB);
    typedef void(APIENTRY* glAttachObjectARBProc)(GLhandleARB, GLhandleARB);
    typedef void(APIENTRY* glDetachObjectARBProc)(GLhandleARB, GLhandleARB);
    typedef void(APIENTRY* glLinkProgramARBProc)(GLhandleARB);

    typedef GLhandleARB(APIENTRY* glCreateShaderObjectARBProc)(GLenum);
    typedef void(APIENTRY* glDeleteShaderObjectARBProc)(GLhandleARB);
    typedef void(APIENTRY* glShaderSourceARBProc)(GLhandleARB, GLsizei, const GLcharARB**,
                                                  const GLint*);
    typedef void(APIENTRY* glCompileShaderARBProc)(GLhandleARB);
    typedef void(APIENTRY* glGetObjectParameterivARBProc)(GLhandleARB, GLenum, GLint*);
    typedef void(APIENTRY* glGetInfoLogARBProc)(GLhandleARB, GLsizei, GLsizei*, GLcharARB*);

    glCreateProgramObjectARBProc glCreateProgram;
    glDeleteProgramObjectARBProc glDeleteProgram;
    glAttachObjectARBProc        glAttachShader;
    glDetachObjectARBProc        glDetachShader;
    glLinkProgramARBProc         glLinkProgram;

    glCreateShaderObjectARBProc   glCreateShader;
    glDeleteShaderObjectARBProc   glDeleteShader;
    glShaderSourceARBProc         glShaderSource;
    glCompileShaderARBProc        glCompileShader;
    glGetObjectParameterivARBProc glGetObjectParameteriv;
    glGetInfoLogARBProc           glGetInfoLog;
    ShaderExtensions();

private:
    ShaderExtensions& operator=(const ShaderExtensions&);
};

}}  // namespace Motor::OpenGL
