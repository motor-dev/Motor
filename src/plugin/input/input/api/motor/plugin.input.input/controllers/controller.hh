/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.input.input/stdafx.h>

namespace Motor { namespace Input {

class motor_api(INPUT) Controller : public minitl::refcountable
{
protected:
    Controller();
    ~Controller() override;
};

}}  // namespace Motor::Input
