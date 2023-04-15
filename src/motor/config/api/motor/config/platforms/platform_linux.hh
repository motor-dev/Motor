/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define MOTOR_PLATFORM_NAME  Linux
#define MOTOR_PLATFORM_LINUX 1
#define MOTOR_PLATFORM_POSIX 1
#define MOTOR_PLATFORM_PC    1

#include <alloca.h>
#include <cstdlib>
#include <strings.h>
#define malloca  alloca
#define freea(p) (void)p
#define DIRENT_H <dirent.h>
