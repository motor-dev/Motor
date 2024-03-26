/* Motor <motor.devel@gmail.com> under New BSD License
   see LICENSE for detail */
#ifndef MOTOR_TEST_WORLD_COMPONENT_META_HH
#define MOTOR_TEST_WORLD_COMPONENT_META_HH

#include <stdafx.h>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace Test { namespace World {

struct [[motor::meta(tag = LogicComponent())]] Component
{
};

struct [[motor::meta(tag = LogicComponent())]] Component2
{
};

}}}  // namespace Motor::Test::World

#include <component.meta.factory.hh>
#endif
