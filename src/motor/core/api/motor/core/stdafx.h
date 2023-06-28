/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CORE_STDAFX_H
#define MOTOR_CORE_STDAFX_H
#pragma once

#include <motor/kernel/stdafx.h>
#include <motor/core/coredefs.hh>

#ifndef MOTOR_COMPUTE

#    include <motor/core/string/istring.hh>
#    include <motor/core/string/text.hh>

#    include <motor/core/logger.hh>

namespace Motor { namespace Log {

motor_api(CORE) weak< Logger > motor();
motor_api(CORE) weak< Logger > system();
motor_api(CORE) weak< Logger > thread();

}}  // namespace Motor::Log

#endif

#endif
