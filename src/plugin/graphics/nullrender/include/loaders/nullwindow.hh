/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/plugin.graphics.3d/renderer/irenderer.hh>
#include <motor/plugin.graphics.3d/renderer/irendertarget.hh>

namespace Motor { namespace Null {

class NullRenderer;

class NullWindow : public IRenderTarget
{
public:
    NullWindow(weak< const RenderWindowDescription > windowDescription,
               weak< const NullRenderer >            renderer);
    ~NullWindow();

private:
    void load(weak< const Resource::IDescription > windowDescription) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}  // namespace Motor::Null
