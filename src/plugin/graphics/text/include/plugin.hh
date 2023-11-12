/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_PLUGIN_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_PLUGIN_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/minitl/pointer.hh>
#include <motor/plugin/plugin.hh>

namespace Motor {

class TextManager;
class OutlineFontManager;
class BitmapFontManager;
class FontList;
class FreetypeLibrary;

class TextPlugin : public minitl::pointer
{
private:
    weak< Resource::ResourceManager > m_resourceManager;
    scoped< FreetypeLibrary >         m_freetypeLibrary;
    scoped< FontList >                m_fontList;
    scoped< TextManager >             m_textManager;
    scoped< OutlineFontManager >      m_outlineFontManager;
    scoped< BitmapFontManager >       m_bitmapFontManager;

public:
    explicit TextPlugin(const Plugin::Context& pluginContext);
    ~TextPlugin() override;
};

}  // namespace Motor

#endif
