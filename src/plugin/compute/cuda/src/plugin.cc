/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.compute.cuda/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin/plugin.hh>
#include <scheduler.hh>

MOTOR_PLUGIN_REGISTER(Motor::KernelScheduler::Cuda::Scheduler)
