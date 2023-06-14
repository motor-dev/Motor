/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CONFIG_PLATFORMS_PLATFORM_FREEBSD_HH
#define MOTOR_CONFIG_PLATFORMS_PLATFORM_FREEBSD_HH

#define MOTOR_PLATFORM_NAME    FreeBSD
#define MOTOR_PLATFORM_FREEBSD 1
#define MOTOR_PLATFORM_BSD     1
#define MOTOR_PLATFORM_POSIX   1
#define MOTOR_PLATFORM_PC      1

#include <stdlib.h>
#define malloca  alloca
#define freea(p) (void)p
#define DIRENT_H <dirent.h>

#endif
