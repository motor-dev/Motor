/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>
#include <motor/plugin.graphics.3d/rendertarget/rendertarget.meta.hh>

#include <motor/scheduler/task/task.hh>

namespace Motor {

IRenderTarget::IRenderTarget(weak< const RenderTargetDescription > rendertarget,
                             weak< const IRenderer >               renderer)
    : IGPUResource(rendertarget, renderer)
{
}

IRenderTarget::~IRenderTarget()
{
}

weak< Task::ITask > IRenderTarget::syncTask() const
{
    return m_renderer->syncTask();
}

void IRenderTarget::drawBatches(const Batch* /*batches*/, size_t /*count*/) const
{
    begin(IRenderTarget::Clear);
    // m_renderTarget->drawBatches(m_batches);
    end(IRenderTarget::Present);
}

}  // namespace Motor
