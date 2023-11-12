/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_PHYSICS_BULLET_BULLETWORLD_HH
#define MOTOR_PLUGIN_PHYSICS_BULLET_BULLETWORLD_HH

#include <stdafx.h>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Physics { namespace Bullet {

class BulletWorld : public minitl::pointer
{
public:
    explicit BulletWorld(const Plugin::Context& context);
    ~BulletWorld() override;

    void step();
};

}}}  // namespace Motor::Physics::Bullet

#endif
