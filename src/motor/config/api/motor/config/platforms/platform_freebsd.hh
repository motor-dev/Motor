/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define MOTOR_PLATFORM_NAME    FreeBSD
#define MOTOR_PLATFORM_FREEBSD 1
#define MOTOR_PLATFORM_BSD     1
#define MOTOR_PLATFORM_POSIX   1
#define MOTOR_PLATFORM_PC      1

#include <cstdlib>
#define malloca  alloca
#define freea(p) (void)p
#define DIRENT_H <dirent.h>
