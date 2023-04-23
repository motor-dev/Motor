/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/world/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor { namespace World {

class motor_api(WORLD) SubWorld : public Resource::Description< SubWorld >
{
published:
    SubWorld();
    ~SubWorld() override;
};

}}  // namespace Motor::World
