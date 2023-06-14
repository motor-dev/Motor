/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_PHYSICS_BULLET_BULLETWORLD_HH
#define MOTOR_PLUGIN_PHYSICS_BULLET_BULLETWORLD_HH

#include <stdafx.h>
#include <motor/plugin/plugin.hh>

#ifdef MOTOR_COMPILER_MSVC
#    pragma warning(push, 1)
#endif
#include <LinearMath/btAlignedAllocator.h>
#include <btBulletDynamicsCommon.h>
#ifdef MOTOR_COMPILER_MSVC
#    pragma warning(pop)
#endif

namespace Motor { namespace Physics { namespace Bullet {

class BulletWorld : public minitl::refcountable
{
public:
    explicit BulletWorld(const Plugin::Context& context);
    ~BulletWorld() override;

    void step();

public:
    void* operator new(size_t size, void* where)
    {
        return ::operator new(size, where);
    }
    static void operator delete(void* memory, void* where)
    {
        ::operator delete(memory, where);
    }
    static void operator delete(void* memory)
    {
        motor_notreached();
        ::operator delete(memory);
    }
};

}}}  // namespace Motor::Physics::Bullet

#endif
