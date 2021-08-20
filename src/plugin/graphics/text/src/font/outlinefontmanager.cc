
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

OutlineFontManager::OutlineFontManager(weak< Resource::ResourceManager > manager,
                                       weak< FreetypeLibrary >           freetype,
                                       weak< const FontList >            fontList)
    : m_manager(manager)
    , m_freetype(freetype)
    , m_fontList(fontList)
{
}

OutlineFontManager::~OutlineFontManager()
{
}

void OutlineFontManager::load(weak< const Resource::Description > description,
                              Resource::Resource& /*resource*/)
{
    motor_info("loading outline font");
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

void OutlineFontManager::reload(weak< const Resource::Description > /*oldDescription*/,
                                weak< const Resource::Description > newDescription,
                                Resource::Resource& /*resource*/)
{
    motor_info("reloading outline font");
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

void OutlineFontManager::unload(Resource::Resource& resource)
{
    motor_info("unloading outline font");
    resource.clearRefHandle();
}

void OutlineFontManager::onTicketLoaded(weak< const Resource::Description > /*description*/,
                                        Resource::Resource&                   resource,
                                        const minitl::Allocator::Block< u8 >& buffer,
                                        LoadType /*type*/)
{
    motor_info("outline font file done loading");
    ref< FreetypeFace > face = ref< FreetypeFace >::create(Arena::game(), m_freetype, buffer);
    resource.clearRefHandle();
    resource.setRefHandle(face);
}

}  // namespace Motor
