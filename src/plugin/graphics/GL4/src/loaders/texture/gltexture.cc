/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/texture/texture.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <loaders/texture/gltexture.hh>

namespace Motor { namespace OpenGL {

GLTexture::GLTexture(const weak< const Resource::IDescription >& textureDescription,
                     const weak< GLRenderer >&                   renderer)
    : IGPUResource(textureDescription, renderer)
{
}

GLTexture::~GLTexture() = default;

void GLTexture::load(const weak< const Resource::IDescription >& /*textureDescription*/)
{
}

void GLTexture::unload()
{
}

}}  // namespace Motor::OpenGL
