/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <shaderpipeline.hh>
#include    <renderer.hh>
#include    <cgshader.hh>
#include    <cgshaderparam.hh>

#include    <core/memory/streams.hh>
#include    <system/filesystem.hh>

namespace BugEngine { namespace Graphics { namespace DirectX9
{

ShaderPipeline::ShaderPipeline(weak<Renderer> owner)
    :   m_owner(owner)
    ,   m_vertexProfile(cgGetProfile("vs_2_x"))
    ,   m_fragmentProfile(cgGetProfile("ps_2_x"))
{
    cgD3D9EnableDebugTracing(true);
}

ShaderPipeline::~ShaderPipeline()
{
}

_Shader* ShaderPipeline::load(const ifilename& filename)
{
    ref<IMemoryStream> file = FileSystem::instance()->open(filename, eReadOnly);
    const char *ext = filename[filename.size()-1].c_str();
    size_t extpos = strlen(ext) - 5;
    CGprofile p = m_vertexProfile;
    if(stricmp(ext+extpos, "_f.cg") == 0)
        p = m_fragmentProfile;

    CGprogram program = cgCreateProgram(m_owner->m_context, CG_SOURCE, (const char *)file->basememory(), p, 0, 0);
    cgCompileProgram(program);
    cgD3D9LoadProgram(program, 0, 0);

    CgShader* s = new CgShader(program);
    CGparameter param = cgGetFirstParameter(program, CG_PROGRAM);
    while(param)
    {
        const char *name = cgGetParameterName(param);
        ref<CgShaderParam> wrapped;
        if(isSystemParameter(name))
        {
            wrapped = getSystemParameter(name);
            cgConnectParameter(wrapped->m_shaderParam, param);
        }
        else
        {
            wrapped = ref<CgShaderParam>::create(param);
        }
        s->addParam(wrapped);
        param = cgGetNextParameter(param);
    }

    return s;
}

void ShaderPipeline::unload(_Shader* s)
{
    delete s;
}

bool ShaderPipeline::isSystemParameter(const char *name)
{
    return name && name[0] == '_' && name[1] == '_';
}

ref<CgShaderParam> ShaderPipeline::getSystemParameter(const char* name)
{
    return m_systemParams[name];
}

const char *ShaderPipeline::getTypeName(ShaderParam::Type t)
{
    return cgGetTypeString(CGtype(t));
}

ShaderParam::Type ShaderPipeline::getTypeByName(const char *name)
{
    return cgGetType(name);
}

ref<CgShaderParam> ShaderPipeline::createSystemParameter(const istring& name, ShaderParam::Type type)
{
    CGparameter p = cgCreateParameter(m_owner->m_context, CGtype(type));
    cgSetParameterVariability(p, CG_UNIFORM);
    be_assert(cgGetParameterType(p) == type, "type conflict");
    ref<CgShaderParam> param(ref<CgShaderParam>::create(p));
    bool result = m_systemParams.insert(std::make_pair(name, param)).second;
    be_assert(result, "system parameter %s already exists" | name.c_str());
	UNUSED(result);
    return param;
}

}}}
