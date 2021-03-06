/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_LOADERS_TEXTURE_GLTEXTURE_HH_
#define MOTOR_GL4_LOADERS_TEXTURE_GLTEXTURE_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLTexture : public IGPUResource
{
public:
    GLTexture(weak< const Resource::IDescription > textureDescription, weak< GLRenderer > renderer);
    ~GLTexture();

    virtual void load(weak< const Resource::IDescription > textureDescription) override;
    virtual void unload() override;
};

}}  // namespace Motor::OpenGL

/**************************************************************************************************/
#endif
