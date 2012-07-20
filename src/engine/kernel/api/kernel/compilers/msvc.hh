/* BugEngine / 2008-2012  Nicolas MERCIER <mercier.nicolas@gmail.com>
   see LICENSE for detail */

#ifndef BE_KERNEL_COMPILERS_MSVC_HH_
#define BE_KERNEL_COMPILERS_MSVC_HH_
/*****************************************************************************/

#define be_alignof(t)           __alignof(t&)

typedef signed __int8           i8;
typedef signed __int16          i16;
typedef signed __int32          i32;
typedef signed __int64          i64;
typedef unsigned __int8         u8;
typedef unsigned __int16        u16;
typedef unsigned __int32        u32;
typedef unsigned __int64        u64;
typedef u8                      byte;

#pragma warning(default:4263)   // member function does not override any base class virtual member function
#pragma warning(default:4264)   // no override available for virtual member function from base 'class'; function is hidden
#pragma warning(default:4265)   // class has virtual functions, but destructor is not virtual
#pragma warning(default:4266)   // no override available for virtual member function from base 'type'; function is hidden
#pragma warning(default:4906)   // wide string literal cast to 'LPSTR'
#pragma warning(default:4946)   // reinterpret_cast used between related classes

#pragma warning(error:4715)     // not all control paths return a value

#pragma warning(disable:4275)   // non dll-interface class 'X' used as base for dll-interface class 'Y'
#ifdef NDEBUG
# pragma warning(error:4541)    // 'dynamic_cast' used on polymorphic type with '/GR-'
# pragma warning(disable:4530)  // C++ exception handler used, but unwind semantics are not enabled
# pragma warning(disable:4100)  // unreferenced formal parameter
#endif
#pragma warning(disable:4355)   // this used in base member initialization list
#pragma warning(disable:4127)   // conditional expression is constant
//#pragma warning(disable:4181)   // qualifier applied to reference type; ignored
#pragma warning(disable:4505)   // unreferenced local function has been removed
#pragma warning(disable:4510)   // default constructor could not be generated
#pragma warning(disable:4511)   // copy constructor could not be generated
#pragma warning(disable:4512)   // assignment operator could not be generated
#pragma warning(disable:4610)   // struct X can never be instantiated - user defined constructor required
#pragma warning(disable:4800)   // forcing value to bool 'true' or 'false' (performance warning)
#define BE_NOINLINE             __declspec(noinline)
#define BE_ALWAYSINLINE         __forceinline
#define BE_SELECTOVERLOAD(o)    (o)

#define BE_SET_ALIGNMENT(n)     __declspec(align(n))
#ifndef BE_STATIC
# define BE_EXPORT              __declspec(dllexport)
# define BE_IMPORT              __declspec(dllimport)
#else
# define BE_EXPORT
# define BE_IMPORT
#endif

#if _MSC_VER >= 1600
# define BE_HAS_MOVE_SEMANTICS
#endif

#if _MSC_VER >= 1300
# ifndef _XBOX
#  include <xmmintrin.h>
# endif
# define be_break() __debugbreak()
#else
# define be_break() asm  { int 3; }
#endif

#if _MSC_VER >= 1400
# pragma warning(disable:4481)   // use of "override" extension
#else
# define override
# pragma warning(disable:4702)   // unreachable code
# pragma warning(disable:4714)   // function marked as __forceinline but not inlined
#endif

/*****************************************************************************/
#endif