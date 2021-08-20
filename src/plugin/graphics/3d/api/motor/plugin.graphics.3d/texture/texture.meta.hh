/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_TEXTURE_TEXTURE_SCRIPT_HH_
#define MOTOR_3D_TEXTURE_TEXTURE_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/resource/description.meta.hh>

namespace Motor {

class motor_api(3D) TextureDescription : public Resource::Description
{
public:
    TextureDescription();
    ~TextureDescription();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
