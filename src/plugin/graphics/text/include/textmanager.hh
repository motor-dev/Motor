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

    void load(weak< const Resource::IDescription > description,
              Resource::Resource&                  resource) override;
    void reload(weak< const Resource::IDescription > oldDescription,
                weak< const Resource::IDescription > newDescription,
                Resource::Resource&                  resource) override;
    void unload(weak< const Resource::IDescription > description,
                Resource::Resource&                  resource) override;
};

}  // namespace Motor

/**************************************************************************************************/
#endif
