/* BugEngine <bugengine.devel@gmail.com> / 2008-2014
   see LICENSE for detail */

#ifndef BE_INPUT_CONTROLLERS_KEYBOARD_HH_
#define BE_INPUT_CONTROLLERS_KEYBOARD_HH_
/**************************************************************************************************/
#include    <input/stdafx.h>
#include    <input/controllers/controller.hh>

namespace BugEngine { namespace Input
{

class Keyboard : public Controller
{
    BE_NOCOPY(Keyboard);
public:
    Keyboard();
    ~Keyboard();
};

}}

/**************************************************************************************************/
#endif
