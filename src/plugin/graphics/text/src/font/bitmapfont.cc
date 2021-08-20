/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.3d/shader/types.meta.hh>
#include <motor/plugin.graphics.text/bitmapfont.meta.hh>

namespace Motor {

BitmapFont::BitmapFont(const istring& fontSystemName)
    : m_fontSystemName(fontSystemName)
    , m_fontFile()
{
}

BitmapFont::BitmapFont(weak< const File > fontFile) : m_fontSystemName(""), m_fontFile(fontFile)
{
}

BitmapFont::~BitmapFont()
{
}

}  // namespace Motor
