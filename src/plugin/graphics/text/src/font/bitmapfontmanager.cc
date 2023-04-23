/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <bitmapfontmanager.hh>
#include <fontlist.hh>

namespace Motor {

BitmapFontManager::BitmapFontManager(const weak< Resource::ResourceManager >& manager,
                                     const weak< FreetypeLibrary >&           freetype,
                                     const weak< const FontList >&            fontList)
    : m_manager(manager)
    , m_freetype(freetype)
    , m_fontList(fontList)
{
}

BitmapFontManager::~BitmapFontManager() = default;

void BitmapFontManager::load(const weak< const Resource::IDescription >& /*description*/,
                             Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "loading bitmap font");
}

void BitmapFontManager::reload(const weak< const Resource::IDescription >& /*oldDescription*/,
                               const weak< const Resource::IDescription >& /*newDescription*/,
                               Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "reloading bitmap font");
}

void BitmapFontManager::unload(const weak< const Resource::IDescription >& /*description*/,
                               Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "unloading bitmap font");
}

void BitmapFontManager::onTicketLoaded(const weak< const Resource::IDescription >& /*description*/,
                                       Resource::Resource& /*resource*/,
                                       const minitl::Allocator::Block< u8 >& /*buffer*/,
                                       LoadType /*type*/)
{
    motor_info(Log::resource(), "bitmap font file done loading");
}

}  // namespace Motor
