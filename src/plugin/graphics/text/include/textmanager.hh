/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor {

class FontList;

class TextManager : public Resource::ILoader
{
public:
    TextManager();
    ~TextManager() override;

    void load(const weak< const Resource::IDescription >& description,
              Resource::Resource&                         resource) override;
    void reload(const weak< const Resource::IDescription >& oldDescription,
                const weak< const Resource::IDescription >& newDescription,
                Resource::Resource&                         resource) override;
    void unload(const weak< const Resource::IDescription >& description,
                Resource::Resource&                         resource) override;
};

}  // namespace Motor
