/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_OUTLINEFONT_META_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_OUTLINEFONT_META_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/filesystem/file.meta.hh>
#include <motor/resource/description.hh>

namespace Motor {

class OutlineFontManager;

class motor_api(TEXT) OutlineFont : public Resource::Description< OutlineFont >
{
    friend class OutlineFontManager;

private:
    istring const            m_fontSystemName;
    weak< const File > const m_fontFile;
published:
    explicit OutlineFont(const istring& fontSystemName);
    explicit OutlineFont(const weak< const File >& fontFile);
    ~OutlineFont() override;
};

}  // namespace Motor

#endif
