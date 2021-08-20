
/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/folder.meta.hh>

namespace Motor {

Folder::Watch::Watch(weak< Folder > folder) : m_folder(folder)
{
}

Folder::Watch::~Watch()
{
}

void Folder::Watch::signal()
{
    m_folder->onChanged();
}

}  // namespace Motor
