/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_BITMAPFONT_SCRIPT_HH_
#define MOTOR_TEXT_BITMAPFONT_SCRIPT_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/filesystem/file.script.hh>
#include <motor/resource/description.script.hh>

namespace Motor {

class BitmapFontManager;

class motor_api(TEXT) BitmapFont : public Resource::Description
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
