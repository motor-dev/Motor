/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
    GLhandleARB build(const weak< const ShaderProgramDescription >& program) const;
    void        attach();

public:
    GLShaderProgram(const weak< const Resource::IDescription >& shaderDescription,
                    const weak< const GLRenderer >&             renderer);
    ~GLShaderProgram() override;

    void load(const weak< const Resource::IDescription >& shaderDescription) override;
    void unload() override;
};

}}  // namespace Motor::OpenGL
