/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include   <stdafx.h>
#include   <bulletworld.hh>

namespace BugEngine { namespace Arena
{

static Allocator& bullet() { return general(); }

}}

namespace BugEngine { namespace Physics { namespace Bullet
{

static BE_NOINLINE void* allocate(size_t size)
{
    return Arena::bullet().alloc(size, 16);
}

static BE_NOINLINE void* allocate(size_t size, int align)
{
    return Arena::bullet().alloc(size, align);
}

static BE_NOINLINE void free(void* block)
{
    return Arena::bullet().free(block);
}


BulletWorld::BulletWorld(const PluginContext& /*context*/)
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

}}}

