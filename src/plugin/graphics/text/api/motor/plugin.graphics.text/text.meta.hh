/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_TEXT_META_HH_
#define MOTOR_TEXT_TEXT_META_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/description.hh>

namespace Motor {

class motor_api(TEXT) Text : public Resource::Description< Text >
{
public:
    Text();
    ~Text();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
