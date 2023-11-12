/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_CONTROLLER_HH
#define MOTOR_PLUGIN_INPUT_INPUT_CONTROLLERS_CONTROLLER_HH

#include <motor/plugin.input.input/stdafx.h>

namespace Motor { namespace Input {

class motor_api(INPUT) Controller : public minitl::pointer
{
protected:
    Controller();
    ~Controller() override;
};

}}  // namespace Motor::Input

#endif
