/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/loader.hh>
#include <motor/resource/resourcemanager.hh>
#include <freetypelib.hh>

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
    BitmapFontManager(const weak< Resource::ResourceManager >& manager,
                      const weak< FreetypeLibrary >&           freetype,
                      const weak< const FontList >&            fontList);
    ~BitmapFontManager() override;

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
