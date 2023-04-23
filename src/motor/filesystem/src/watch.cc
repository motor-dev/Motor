
/* Motor <motor.devel@gmail.com>
 see LICENSE for detail */

#include <motor/filesystem/stdafx.h>
#include <motor/filesystem/folder.meta.hh>

namespace Motor {

Folder::Watch::Watch(const weak< Folder >& folder) : m_folder(folder)
{
}

Folder::Watch::~Watch() = default;

void Folder::Watch::signal()
{
    m_folder->onChanged();
}

}  // namespace Motor
