/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_3D_STDAFX_H_
#define MOTOR_3D_STDAFX_H_
/**************************************************************************************************/

#include <motor/stdafx.h>

#if defined(building_3d)
#    define MOTOR_API_3D MOTOR_EXPORT
#elif defined(motor_dll_3d)
#    define MOTOR_API_3D MOTOR_IMPORT
#else
#    define MOTOR_API_3D
#endif

/**************************************************************************************************/
#endif
