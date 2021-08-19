/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_ENGINE_TUPLE_HH_
#define MOTOR_META_ENGINE_TUPLE_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.script.hh>
#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/methodinfo.script.hh>
#include <motor/meta/engine/objectinfo.script.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/minitl/tuple.hh>

namespace Motor {

template < typename T1, typename T2, typename T3, typename T4, typename T5 >
static Meta::Value make_tuple(Meta::Value* v, u32 count);

}

#include <motor/meta/engine/helper/tuple2.factory.hh>
#include <motor/meta/engine/helper/tuple3.factory.hh>
#include <motor/meta/engine/helper/tuple4.factory.hh>
#include <motor/meta/engine/helper/tuple5.factory.hh>

/**************************************************************************************************/
#endif
