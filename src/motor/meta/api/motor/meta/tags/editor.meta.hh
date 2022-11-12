/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
