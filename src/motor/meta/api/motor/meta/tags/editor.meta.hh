/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>

namespace Motor { namespace EditHint {

struct motor_api(META) Extension
{
    const istring ext;
    explicit Extension(const istring& ext) : ext(ext)
    {
    }
};

struct motor_api(META) Temporary
{
    Temporary() = default;
};

struct motor_api(META) OutputNode
{
    OutputNode() = default;
};

}}  // namespace Motor::EditHint
