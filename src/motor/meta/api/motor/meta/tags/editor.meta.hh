/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_META_TAGS_EDITOR_SCRIPT_HH_
#define MOTOR_META_TAGS_EDITOR_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/meta/stdafx.h>

namespace Motor { namespace EditHint {

struct motor_api(META) Extension
{
    const istring ext;
    Extension(const istring& ext) : ext(ext)
    {
    }
};

struct motor_api(META) Temporary {Temporary() {}};

struct motor_api(META) OutputNode {OutputNode() {}};

}}  // namespace Motor::EditHint

/**************************************************************************************************/
#endif
