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
    ~TextManager();

    void load(weak< const Resource::IDescription > description,
              Resource::Resource&                  resource) override;
    void reload(weak< const Resource::IDescription > oldDescription,
                weak< const Resource::IDescription > newDescription,
                Resource::Resource&                  resource) override;
    void unload(weak< const Resource::IDescription > description,
                Resource::Resource&                  resource) override;
};

}  // namespace Motor
