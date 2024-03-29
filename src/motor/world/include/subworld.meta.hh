/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_SUBWORLD_META_HH
#define MOTOR_WORLD_SUBWORLD_META_HH

#include <motor/world/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor { namespace World {

class motor_api(WORLD) SubWorld : public Resource::Description< SubWorld >
{
public:
    SubWorld();
    ~SubWorld() override;
};

}}  // namespace Motor::World

#include <subworld.meta.factory.hh>
#endif
