
/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/plugin.graphics.text/outlinefont.meta.hh>
#include <motor/resource/resourcemanager.hh>
#include <fontlist.hh>
#include <freetypeface.hh>
#include <freetypelib.hh>
#include <outlinefontmanager.hh>

namespace Motor {

OutlineFontManager::OutlineFontManager(const weak< Resource::ResourceManager >& manager,
                                       const weak< FreetypeLibrary >&           freetype,
                                       const weak< const FontList >&            fontList)
    : m_manager(manager)
    , m_freetype(freetype)
    , m_fontList(fontList)
{
}

OutlineFontManager::~OutlineFontManager() = default;

void OutlineFontManager::load(const weak< const Resource::IDescription >& description,
                              Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "loading outline font");
    if(motor_checked_cast< const OutlineFont >(description)->m_fontFile)
    {
        m_manager->addTicket(this, description,
                             motor_checked_cast< const OutlineFont >(description)->m_fontFile,
                             FileBinary, LoadFirstTime);
    }
    else
    {
        /* load from system font */
        motor_unimplemented();
    }
}

void OutlineFontManager::reload(const weak< const Resource::IDescription >& /*oldDescription*/,
                                const weak< const Resource::IDescription >& newDescription,
                                Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "reloading outline font");
    if(motor_checked_cast< const OutlineFont >(newDescription)->m_fontFile)
    {
        m_manager->addTicket(this, newDescription,
                             motor_checked_cast< const OutlineFont >(newDescription)->m_fontFile,
                             FileBinary, LoadReload);
    }
    else
    {
        /* load from system font */
        motor_unimplemented();
    }
}

void OutlineFontManager::unload(const weak< const Resource::IDescription >& /*description*/,
                                Resource::Resource& resource)
{
    motor_info(Log::resource(), "unloading outline font");
    resource.clearRefHandle();
}

void OutlineFontManager::onTicketLoaded(const weak< const Resource::IDescription >& /*description*/,
                                        Resource::Resource&                   resource,
                                        const minitl::Allocator::Block< u8 >& buffer,
                                        LoadType /*type*/)
{
    motor_info(Log::resource(), "outline font file done loading");
    ref< FreetypeFace > face = ref< FreetypeFace >::create(Arena::game(), m_freetype, buffer);
    resource.clearRefHandle();
    resource.setRefHandle(face);
}

}  // namespace Motor
