/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_OUTLINEFONTMANAGER_HH_
#define MOTOR_TEXT_OUTLINEFONTMANAGER_HH_
/**************************************************************************************************/
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
    OutlineFontManager(weak< Resource::ResourceManager > manager, weak< FreetypeLibrary > freetype,
                       weak< const FontList > fontList);
    ~OutlineFontManager();

    void load(weak< const Resource::IDescription > description,
              Resource::Resource&                  resource) override;
    void reload(weak< const Resource::IDescription > oldDescription,
                weak< const Resource::IDescription > newDescription,
                Resource::Resource&                  resource) override;
    void unload(weak< const Resource::IDescription > description,
                Resource::Resource&                  resource) override;
    void onTicketLoaded(weak< const Resource::IDescription > description,
                        Resource::Resource& resource, const minitl::Allocator::Block< u8 >& buffer,
                        LoadType type) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
