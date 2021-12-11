/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/texture/texture.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <loaders/texture/gltexture.hh>

namespace Motor { namespace OpenGL {

GLTexture::GLTexture(weak< const Resource::IDescription > textureDescription,
                     weak< GLRenderer >                   renderer)
    : IGPUResource(textureDescription, renderer)
{
}

GLTexture::~GLTexture()
{
}

void GLTexture::load(weak< const Resource::IDescription > /*textureDescription*/)
{
}

void GLTexture::unload()
{
}

}}  // namespace Motor::OpenGL
