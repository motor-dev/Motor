/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#define MOTOR_PLATFORM_NAME  SunOS
#define MOTOR_PLATFORM_SUN   1
#define MOTOR_PLATFORM_POSIX 1
#define MOTOR_PLATFORM_PC    1

#include <alloca.h>
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define malloca  alloca
#define freea(p) (void)p
#define DIRENT_H <dirent.h>
