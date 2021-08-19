/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/string/message.hh>

#include <cstring>

namespace Motor {

message::message(const char* msg) : m_msg(msg)
{
}

message::~message()
{
}

}  // namespace Motor
