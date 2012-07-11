/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <loaders/nullshader.hh>
#include    <nullrenderer.hh>


namespace BugEngine { namespace Null
{

NullShaderProgram::NullShaderProgram(weak<const ShaderProgram> resource, weak<const NullRenderer> renderer)
:   IGPUResource(resource, renderer)
{
}

NullShaderProgram::~NullShaderProgram()
{
}

void NullShaderProgram::load(weak<const Resource> /*resource*/)
{
}

void NullShaderProgram::unload()
{
}

}}
