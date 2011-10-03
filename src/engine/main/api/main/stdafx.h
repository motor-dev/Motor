/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_MAIN_STDAFX_H_
#define BE_MAIN_STDAFX_H_
/*****************************************************************************/

#include    <core/stdafx.h>
#include    <rtti/stdafx.h>
#include    <system/stdafx.h>
#include    <world/stdafx.h>

#if defined(building_main) || defined(MAIN_EXPORTS)
# define     MAINEXPORT          BE_EXPORT
#elif defined(main_dll)
# define     MAINEXPORT          BE_IMPORT
#else
# define     MAINEXPORT
#endif

/*****************************************************************************/
#endif
