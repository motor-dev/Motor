/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/engine/operatortable.meta.hh>

namespace Motor { namespace Meta {

static const OperatorTable s_table                     = {{nullptr}, {0, nullptr}, {nullptr}};
raw< const OperatorTable > OperatorTable::s_emptyTable = {&s_table};

}}  // namespace Motor::Meta
