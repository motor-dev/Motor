/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.debug.runtime/stdafx.h>
#include <motor/plugin.debug.runtime/module.hh>

namespace Motor { namespace Runtime {

ref< const Module > Module::self()
{
    static ref< Module > s_module;
    return s_module;
}

}}  // namespace Motor::Runtime
