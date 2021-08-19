/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/stdafx.h>
#include <motor/script.script.hh>

namespace Motor {

Script::Script(weak< const File > file) : m_file(file)
{
}

Script::~Script()
{
}

ifilename Script::getScriptName() const
{
    return m_file->getFileName();
}

}  // namespace Motor
