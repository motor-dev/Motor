/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
