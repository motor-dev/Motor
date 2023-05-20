/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/core/stdafx.h>
#include <motor/core/environment.hh>

namespace Motor {

Environment::Environment()
    : m_homeDirectory(getenv("HOME"))
    , m_dataDirectory(ipath("share/motor"))
    , m_game("")
    , m_user(getenv("USER"))
    , m_programPath()
{
    m_homeDirectory.push_back(istring(".motor"));
}

}  // namespace Motor
