/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_3D_TEXTURE_TEXTURE_META_HH
#define MOTOR_PLUGIN_GRAPHICS_3D_TEXTURE_TEXTURE_META_HH

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(3D) TextureDescription : public Resource::Description< TextureDescription >
{
public:
    TextureDescription();
    ~TextureDescription() override;
};

}  // namespace Motor

#endif
