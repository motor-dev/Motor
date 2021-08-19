/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_BITMAPFONTMANAGER_HH_
#define MOTOR_TEXT_BITMAPFONTMANAGER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <freetypelib.hh>
#include <motor/resource/loader.hh>
#include <motor/resource/resourcemanager.hh>

namespace Motor {

class FreetypeLibrary;
class FontList;

class BitmapFontManager : public Resource::ILoader
{
private:
    weak< Resource::ResourceManager > m_manager;
    weak< FreetypeLibrary >           m_freetype;
    weak< const FontList >            m_fontList;

public:
    BitmapFontManager(weak< Resource::ResourceManager > manager, weak< FreetypeLibrary > freetype,
                      weak< const FontList > fontList);
    ~BitmapFontManager();

    void load(weak< const Resource::Description > description,
              Resource::Resource&                 resource) override;
    void reload(weak< const Resource::Description > oldDescription,
                weak< const Resource::Description > newDescription,
                Resource::Resource&                 resource) override;
    void unload(Resource::Resource& resource) override;
    void onTicketLoaded(weak< const Resource::Description > description,
                        Resource::Resource& resource, const minitl::Allocator::Block< u8 >& buffer,
                        LoadType type) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
