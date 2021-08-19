/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_TEXT_SCRIPT_HH_
#define MOTOR_TEXT_TEXT_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/description.script.hh>

namespace Motor {

class motor_api(TEXT) Text : public Resource::Description
{
public:
    Text();
    ~Text();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
