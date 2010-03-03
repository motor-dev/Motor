/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <stdafx.h>
#include    <bulletworldmanager.hh>
#include    <bulletworld.hh>

namespace BugEngine { namespace Physics { namespace Bullet
{

BulletWorldManager::BulletWorldManager()
{
}

BulletWorldManager::~BulletWorldManager()
{
}

ref<IWorld> BulletWorldManager::createWorld(float3 extents) const
{
    return ref<BulletWorld>::create(extents);
}

}}}

