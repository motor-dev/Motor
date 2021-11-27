/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_TEXT_TEXTMANAGER_HH_
#define MOTOR_TEXT_TEXTMANAGER_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.text/stdafx.h>
#include <motor/resource/loader.hh>

namespace Motor {

class FontList;

class TextManager : public Resource::ILoader
{
public:
    TextManager();
    ~TextManager();

    void load(weak< const Resource::Description > description,
              Resource::Resource&                 resource) override;
    void reload(weak< const Resource::Description > oldDescription,
                weak< const Resource::Description > newDescription,
                Resource::Resource&                 resource) override;
    void unload(weak< const Resource::Description > description,
                Resource::Resource&                 resource) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
