/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <loaders/texture/gltexture.hh>
#include <motor/plugin.graphics.3d/texture/texture.script.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>

namespace Motor { namespace OpenGL {

GLTexture::GLTexture(weak< const Resource::Description > textureDescription,
                     weak< GLRenderer >                  renderer)
    : IGPUResource(textureDescription, renderer)
{
}

GLTexture::~GLTexture()
{
}

void GLTexture::load(weak< const Resource::Description > /*textureDescription*/)
{
}

void GLTexture::unload()
{
}

}}  // namespace Motor::OpenGL
