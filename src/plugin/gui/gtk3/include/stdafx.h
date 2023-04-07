/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/stdafx.h>

#if defined(building_gtk3)
#    define MOTOR_API_GTK3 MOTOR_EXPORT
#elif defined(motor_dll_gtk3)
#    define MOTOR_API_GTK3 MOTOR_IMPORT
#else
#    define MOTOR_API_GTK3
#endif

#ifdef __GNUC__
#    pragma GCC diagnostic ignored "-Wparentheses"
#endif

#include <glib-object.h>
#include <gtk/gtk.h>

namespace Motor { namespace Log {

weak< Logger > gtk();

}}  // namespace Motor::Log
