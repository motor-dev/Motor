/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_CONFIG_PLATFORMS_PLATFORM_LINUX_HH
#define MOTOR_CONFIG_PLATFORMS_PLATFORM_LINUX_HH

#define MOTOR_PLATFORM_NAME  Linux
#define MOTOR_PLATFORM_LINUX 1
#define MOTOR_PLATFORM_POSIX 1
#define MOTOR_PLATFORM_PC    1

#include <alloca.h>
#include <stdlib.h>
#include <strings.h>
#define malloca  alloca
#define freea(p) (void)p
#define DIRENT_H <dirent.h>

#endif
