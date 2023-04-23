/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLTexture : public IGPUResource
{
public:
    GLTexture(const weak< const Resource::IDescription >& textureDescription,
              const weak< GLRenderer >&                   renderer);
    ~GLTexture() override;

    void load(const weak< const Resource::IDescription >& textureDescription) override;
    void unload() override;
};

}}  // namespace Motor::OpenGL
