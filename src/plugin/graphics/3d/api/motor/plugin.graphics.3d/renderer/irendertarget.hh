/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>
#include <motor/scheduler/task/group.hh>

namespace Motor {

class IRenderer;
class RenderTargetDescription;

class motor_api(3D) IRenderTarget : public IGPUResource
{
    MOTOR_NOCOPY(IRenderTarget);

public:
    enum ClearMode
    {
        DontClear,
        Clear
    };
    enum PresentMode
    {
        DontPresent,
        Present
    };
    struct Batch
    {
    };

private:
    virtual void begin(ClearMode clear) const   = 0;
    virtual void end(PresentMode present) const = 0;

protected:
    IRenderTarget(weak< const RenderTargetDescription > rendertarget,
                  weak< const IRenderer >               renderer);

public:
    virtual ~IRenderTarget();

    weak< Task::ITask > syncTask() const;
    void                drawBatches(const Batch* batches, size_t count) const;
};

}  // namespace Motor
