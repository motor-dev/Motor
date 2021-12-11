/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_LOADERS_SHADER_GLSHADER_HH_
#define MOTOR_GL4_LOADERS_SHADER_GLSHADER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLShaderProgram : public IGPUResource
{
private:
    GLhandleARB m_shaderProgram;
    GLhandleARB m_vertexShader;
    GLhandleARB m_geometryShader;
    GLhandleARB m_fragmentShader;

private:
    GLhandleARB build(weak< const ShaderProgramDescription > program) const;
    void        attach();

public:
    GLShaderProgram(weak< const Resource::IDescription > shaderDescription,
                    weak< const GLRenderer >             renderer);
    ~GLShaderProgram();

    virtual void load(weak< const Resource::IDescription > shaderDescription) override;
    virtual void unload() override;
};

}}  // namespace Motor::OpenGL

/**************************************************************************************************/
#endif
