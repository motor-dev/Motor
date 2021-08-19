/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin/stdafx.h>
#include <motor/plugin/hook.hh>

namespace Motor { namespace Plugin {

IPluginHook::~IPluginHook()
{
    this->unhook();
}

}}  // namespace Motor::Plugin
