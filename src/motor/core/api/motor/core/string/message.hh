/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/stdafx.h>

namespace Motor {

class motor_api(CORE) message
{
private:
    const char* m_msg;

public:
    message(const char* str);
    ~message();

private:
    message();
};

}  // namespace Motor
