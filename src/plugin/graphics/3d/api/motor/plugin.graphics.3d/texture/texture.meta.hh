/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_TEXTURE_TEXTURE_META_HH_
#define MOTOR_3D_TEXTURE_TEXTURE_META_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(3D) TextureDescription : public Resource::Description< TextureDescription >
{
public:
    TextureDescription();
    ~TextureDescription();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
