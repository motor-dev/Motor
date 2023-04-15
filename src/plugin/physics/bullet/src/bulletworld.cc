/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <bulletworld.hh>

namespace Motor { namespace Arena {

static minitl::Allocator& bullet()
{
    return general();
}

}}  // namespace Motor::Arena

namespace Motor { namespace Physics { namespace Bullet {

static MOTOR_NEVER_INLINE void* allocate(size_t size)
{
    return Arena::bullet().alloc(size, 16);
}

static MOTOR_NEVER_INLINE void* allocate(size_t size, int align)
{
    return Arena::bullet().alloc(size, align);
}

static MOTOR_NEVER_INLINE void free(void* block)
{
    return Arena::bullet().free(block);
}

BulletWorld::BulletWorld(const Plugin::Context& /*context*/)
{
    btAlignedAllocSetCustom(allocate, free);
    btAlignedAllocSetCustomAligned(allocate, free);
}

BulletWorld::~BulletWorld()
{
}

void BulletWorld::step()
{
}

}}}  // namespace Motor::Physics::Bullet
