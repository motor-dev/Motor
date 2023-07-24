/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_BITMAPFONT_META_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_BITMAPFONT_META_HH

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

public:
    explicit BitmapFont(const istring& fontSystemName);
    explicit BitmapFont(const weak< const File >& fontFile);
    ~BitmapFont() override;
};

}  // namespace Motor

#endif
