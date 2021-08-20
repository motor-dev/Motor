/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.text/bitmapfont.meta.hh>
#include <motor/plugin.graphics.text/outlinefont.meta.hh>
#include <motor/plugin.graphics.text/text.meta.hh>
#include <motor/plugin/plugin.hh>
#include <motor/resource/resourcemanager.hh>
#include <bitmapfontmanager.hh>
#include <fontlist.hh>
#include <freetypelib.hh>
#include <outlinefontmanager.hh>
#include <plugin.hh>
#include <textmanager.hh>

namespace Motor {

TextPlugin::TextPlugin(const Plugin::Context& pluginContext)
    : m_resourceManager(pluginContext.resourceManager)
    , m_freetypeLibrary(scoped< FreetypeLibrary >::create(Arena::game()))
    , m_fontList(scoped< FontList >::create(Arena::game()))
    , m_textManager(scoped< TextManager >::create(Arena::game()))
    , m_outlineFontManager(scoped< OutlineFontManager >::create(Arena::game(), m_resourceManager,
                                                                m_freetypeLibrary, m_fontList))
    , m_bitmapFontManager(scoped< BitmapFontManager >::create(Arena::game(), m_resourceManager,
                                                              m_freetypeLibrary, m_fontList))
{
    m_resourceManager->attach(motor_class< Text >(), m_textManager);
    m_resourceManager->attach(motor_class< OutlineFont >(), m_outlineFontManager);
    m_resourceManager->attach(motor_class< BitmapFont >(), m_bitmapFontManager);
}

TextPlugin::~TextPlugin()
{
    m_resourceManager->detach(motor_class< BitmapFont >(), m_bitmapFontManager);
    m_resourceManager->detach(motor_class< OutlineFont >(), m_outlineFontManager);
    m_resourceManager->detach(motor_class< Text >(), m_textManager);
}

}  // namespace Motor

MOTOR_PLUGIN_REGISTER(Motor::TextPlugin);
