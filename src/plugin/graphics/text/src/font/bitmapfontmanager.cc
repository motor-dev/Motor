/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <bitmapfontmanager.hh>
#include <fontlist.hh>

namespace Motor {

BitmapFontManager::BitmapFontManager(weak< Resource::ResourceManager > manager,
                                     weak< FreetypeLibrary >           freetype,
                                     weak< const FontList >            fontList)
    : m_manager(manager)
    , m_freetype(freetype)
    , m_fontList(fontList)
{
}

BitmapFontManager::~BitmapFontManager()
{
}

void BitmapFontManager::load(weak< const Resource::IDescription > /*description*/,
                             Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "loading bitmap font");
}

void BitmapFontManager::reload(weak< const Resource::IDescription > /*oldDescription*/,
                               weak< const Resource::IDescription > /*newDescription*/,
                               Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "reloading bitmap font");
}

void BitmapFontManager::unload(weak< const Resource::IDescription > /*description*/,
                               Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "unloading bitmap font");
}

void BitmapFontManager::onTicketLoaded(weak< const Resource::IDescription > /*description*/,
                                       Resource::Resource& /*resource*/,
                                       const minitl::Allocator::Block< u8 >& /*buffer*/,
                                       LoadType /*type*/)
{
    motor_info(Log::resource(), "bitmap font file done loading");
}

}  // namespace Motor
