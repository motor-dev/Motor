/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_BITMAPFONT_META_HH_
#define MOTOR_TEXT_BITMAPFONT_META_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/resource/description.hh>

namespace Motor {

class BitmapFontManager;

class motor_api(TEXT) BitmapFont : public Resource::Description< BitmapFont >
{
    friend class BitmapFontManager;

private:
    istring const            m_fontSystemName;
    weak< const File > const m_fontFile;
published:
    BitmapFont(const istring& fontSystemName);
    BitmapFont(weak< const File > fontFile);
    ~BitmapFont();
};

}  // namespace Motor

/**************************************************************************************************/
#endif
