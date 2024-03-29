/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/shader/node.meta.hh>
#include <motor/plugin.graphics.3d/shader/shader.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <extensions.hh>
#include <loaders/shader/glshader.hh>
#include <loaders/shader/glshaderbuilder.hh>

namespace Motor { namespace OpenGL {

GLShaderProgram::GLShaderProgram(const weak< const Resource::IDescription >& shaderDescription,
                                 const weak< const GLRenderer >&             renderer)
    : IGPUResource(shaderDescription, renderer)
    , m_shaderProgram()
    , m_vertexShader()
    , m_geometryShader()
    , m_fragmentShader()
{
}

GLShaderProgram::~GLShaderProgram() = default;

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
    default:
        motor_error_format(Log::gl(), "Unknown shader type {0}", u32(stage));
        return GL_FRAGMENT_SHADER_ARB;
    }
}

GLhandleARB GLShaderProgram::build(const weak< const ShaderProgramDescription >& program) const
{
    motor_forceuse(program);
    motor_forceuse(this);
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
        minitl::allocator::block<GLcharARB> log(Arena::stack(), loglength);
        shaderext.glGetInfoLog(shader, maxLength, &result, log.data());
        if (!success)
        {
            motor_error(Log::gl(), log.data());
        }
        else
        {
            motor_info(Log::gl(), log.data());
        }
    }
#    endif
    return shader;
#else
    return {};
#endif
}

void GLShaderProgram::load(const weak< const Resource::IDescription >& shaderDescription)
{
    weak< const ShaderProgramDescription > program
        = motor_checked_cast< const ShaderProgramDescription >(shaderDescription);
    motor_assert(m_shaderProgram == GLhandleARB(), "shader program loaded twice?");

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
        minitl::allocator::block< GLcharARB > log(Arena::stack(), loglength);
        shaderext.glGetInfoLog(m_shaderProgram, maxLength, &result, log.data());
        if(!success)
        {
            motor_error(Log::gl(), log.data());
        }
        else
        {
            motor_info(Log::gl(), log.data());
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
        m_vertexShader = GLhandleARB();
    }
    if(m_geometryShader)
    {
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glDeleteShader(m_geometryShader);
        m_geometryShader = GLhandleARB();
    }
    if(m_fragmentShader)
    {
        motor_checked_cast< const GLRenderer >(m_renderer)
            ->shaderext()
            .glDeleteShader(m_fragmentShader);
        m_fragmentShader = GLhandleARB();
    }
    motor_checked_cast< const GLRenderer >(m_renderer)
        ->shaderext()
        .glDeleteProgram(m_shaderProgram);
    m_shaderProgram = GLhandleARB();
}

}}  // namespace Motor::OpenGL
