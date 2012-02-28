/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <3d/stdafx.h>
#include    <3d/renderer/irenderer.hh>
#include    <3d/renderer/igpuresource.hh>
#include    <system/resource/resource.script.hh>

namespace BugEngine
{

IGPUResource::IGPUResource(weak<const Resource> owner, weak<const IRenderer> renderer)
    :   m_renderer(renderer)
    ,   m_resource(owner)
    ,   m_index(-1)
{
}

IGPUResource::~IGPUResource()
{
    if (hooked()) unhook();
}

}