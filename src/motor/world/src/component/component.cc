
/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/world/stdafx.h>
#include <motor/world/component/component.meta.hh>

namespace Motor { namespace World {

Component::Component() = default;

LogicComponent::LogicComponent(raw< const Meta::Class > kernelClass) : kernelClass(kernelClass)
{
    motor_forceuse(this->kernelClass);
}

}}  // namespace Motor::World
