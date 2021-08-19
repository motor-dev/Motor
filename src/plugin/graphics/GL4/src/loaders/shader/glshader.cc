/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <extensions.hh>
#include <loaders/shader/glshader.hh>
#include <loaders/shader/glshaderbuilder.hh>
#include <motor/plugin.graphics.3d/shader/node.script.hh>
#include <motor/plugin.graphics.3d/shader/shader.script.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>

namespace Motor { namespace OpenGL {

GLShaderProgram::GLShaderProgram(weak< const Resource::Description > shaderDescription,
                                 weak< const GLRenderer >            renderer)
    : IGPUResource(shaderDescription, renderer)
    , m_shaderProgram(0)
    , m_vertexShader(0)
    , m_geometryShader(0)
    , m_fragmentShader(0)
{
}

GLShaderProgram::~GLShaderProgram()
{
}

void GLShaderProgram::attach()
{
    motor_assert(m_shaderProgram, "no program created");

    if(m_vertexShader)
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glAttachShader(m_shaderProgram, m_vertexShader);
    if(m_geometryShader)
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glAttachShader(m_shaderProgram, m_geometryShader);
    if(m_fragmentShader)
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glAttachShader(m_shaderProgram, m_fragmentShader);
}

static GLenum toGLShaderStage(Shaders::Stage stage)
{
    switch(stage)
    {
    case Shaders::VertexStage: return GL_VERTEX_SHADER_ARB;
    case Shaders::GeometryStage: return GL_GEOMETRY_SHADER_EXT;
    case Shaders::FragmentStage: return GL_FRAGMENT_SHADER_ARB;
    default: motor_error("Unknown shader type %d" | stage); return GL_FRAGMENT_SHADER_ARB;
    }
}

GLhandleARB GLShaderProgram::build(weak< const ShaderProgramDescription > program) const
{
    motor_forceuse(program);
    toGLShaderStage(Shaders::FragmentStage);
#if 0
    //GLenum shaderType = toGLShaderStage(stage);
    GLShaderBuilder builder(shaderType);
    program->buildSource(builder);

    const ShaderExtensions& shaderext = motor_checked_cast<const GLRenderer>(m_renderer)->shaderext();
    GLhandleARB shader = shaderext.glCreateShader(shaderType);
    GLint size = motor_checked_numcast<GLint>(builder.textSize());
    const GLcharARB* text = (GLcharARB*)builder.text();
    shaderext.glShaderSource(shader, 1, &text, &size);
    shaderext.glCompileShader(shader);
#    ifdef MOTOR_DEBUG
    GLint success, loglength;
    shaderext.glGetObjectParameteriv(shader, GL_COMPILE_STATUS, &success);
    shaderext.glGetObjectParameteriv(shader, GL_INFO_LOG_LENGTH, &loglength);
    if (!success || loglength)
    {
        GLsizei maxLength = loglength, result;
        minitl::Allocator::Block<GLcharARB> log(Arena::stack(), loglength);
        shaderext.glGetInfoLog(shader, maxLength, &result, log.data());
        if (!success)
        {
            motor_error(log.data());
        }
        else
        {
            motor_info(log.data());
        }
    }
#    endif
    return shader;
#else
    return 0;
#endif
}

void GLShaderProgram::load(weak< const Resource::Description > shaderDescription)
{
    weak< const ShaderProgramDescription > program
        = motor_checked_cast< const ShaderProgramDescription >(shaderDescription);
    motor_assert(m_shaderProgram == 0, "shader program loaded twice?");

    const ShaderExtensions& shaderext
        = motor_checked_cast< const GLRenderer >(m_renderer)->shaderext();
    m_shaderProgram = shaderext.glCreateProgram();

    m_vertexShader   = build(program);
    m_geometryShader = build(program);
    m_fragmentShader = build(program);
    attach();
    shaderext.glLinkProgram(m_shaderProgram);

#ifdef MOTOR_DEBUG
    GLint success, loglength;
    shaderext.glGetObjectParameteriv(m_shaderProgram, GL_LINK_STATUS, &success);
    shaderext.glGetObjectParameteriv(m_shaderProgram, GL_INFO_LOG_LENGTH, &loglength);
    if(!success || loglength)
    {
        GLsizei                               maxLength = loglength, result;
        minitl::Allocator::Block< GLcharARB > log(Arena::stack(), loglength);
        shaderext.glGetInfoLog(m_shaderProgram, maxLength, &result, log.data());
        if(!success)
        {
            motor_error(log.data());
        }
        else
        {
            motor_info(log.data());
        }
    }
#endif
}

void GLShaderProgram::unload()
{
    if(m_vertexShader)
    {
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glDeleteShader(m_vertexShader);
        m_vertexShader = 0;
    }
    if(m_geometryShader)
    {
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glDeleteShader(m_geometryShader);
        m_geometryShader = 0;
    }
    if(m_fragmentShader)
    {
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glDeleteShader(m_fragmentShader);
        m_fragmentShader = 0;
    }
    motor_checked_cast< const GLRenderer >(m_renderer)
        ->shaderext()
        .glDeleteProgram(m_shaderProgram);
    m_shaderProgram = 0;
}

}}  // namespace Motor::OpenGL
