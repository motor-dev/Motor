/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_TEXT_OUTLINEFONTMANAGER_HH
#define MOTOR_PLUGIN_GRAPHICS_TEXT_OUTLINEFONTMANAGER_HH

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor {

class FreetypeLibrary;
class FontList;

class OutlineFontManager : public Resource::ILoader
{
private:
    weak< Resource::ResourceManager > m_manager;
    weak< FreetypeLibrary >           m_freetype;
    weak< const FontList >            m_fontList;

public:
    OutlineFontManager(const weak< Resource::ResourceManager >& manager,
                       const weak< FreetypeLibrary >&           freetype,
                       const weak< const FontList >&            fontList);
    ~OutlineFontManager() override;

    void load(const weak< const Resource::IDescription >& description,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldDescription,
                const weak< const Resource::IDescription >& newDescription,
                Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         resource) override;
    void onTicketLoaded(const weak< const Resource::IDescription >& description,
                        Resource::Resource& resource, const minitl::allocator::block< u8 >& buffer,
                        LoadType type) override;
};

}  // namespace Motor

#endif
