/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_WORLD_RESOURCE_HANDLE_META_HH
#define MOTOR_WORLD_RESOURCE_HANDLE_META_HH

#include <motor/world/stdafx.h>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace World {

struct ResourceHandle
{
    void* const resource;
};

}}  // namespace Motor::World

#include <motor/world/resource/handle.meta.factory.hh>
#endif
