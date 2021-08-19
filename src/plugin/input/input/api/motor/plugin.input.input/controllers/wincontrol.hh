/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_INPUT_CONTROLLERS_WINCONTROL_HH_
#define MOTOR_INPUT_CONTROLLERS_WINCONTROL_HH_
/**************************************************************************************************/
#include <motor/plugin.input.input/stdafx.h>
#include <motor/plugin.input.input/controllers/controller.hh>

namespace Motor { namespace Input {

class Wincontrol : public Controller
{
    MOTOR_NOCOPY(Wincontrol);

public:
    Wincontrol();
    ~Wincontrol();
};

}}  // namespace Motor::Input

/**************************************************************************************************/
#endif
