/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.text/outlinefont.meta.hh>

namespace Motor {

OutlineFont::OutlineFont(const istring& fontSystemName)
    : m_fontSystemName(fontSystemName)
    , m_fontFile()
{
}

OutlineFont::OutlineFont(const weak< const File >& fontFile)
    : m_fontSystemName("")
    , m_fontFile(fontFile)
{
}

OutlineFont::~OutlineFont() = default;

}  // namespace Motor
