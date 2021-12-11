/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/resource/idescription.meta.hh>

namespace Motor {

IGPUResource::IGPUResource(weak< const Resource::IDescription > owner,
                           weak< const IRenderer >              renderer)
    : m_renderer(renderer)
    , m_resource(owner)
    , m_index(-1)
{
}

IGPUResource::~IGPUResource()
{
    if(hooked()) unhook();
}

}  // namespace Motor
