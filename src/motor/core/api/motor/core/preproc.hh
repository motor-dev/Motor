/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>

#define MOTOR_STRINGIZE_IMPL(n) #n
#define MOTOR_STRINGIZE(n)      MOTOR_STRINGIZE_IMPL(n)
#define MOTOR_CONCAT_IMPL(i, j) i##j
#define MOTOR_CONCAT(i, j)      MOTOR_CONCAT_IMPL(i, j)
