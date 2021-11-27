/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <textmanager.hh>

namespace Motor {

TextManager::TextManager()
{
}

TextManager::~TextManager()
{
}

void TextManager::load(weak< const Resource::Description > /*description*/,
                       Resource::Resource& /*resource*/)
{
    motor_info("loading text");
}

void TextManager::reload(weak< const Resource::Description > /*oldDescription*/,
                         weak< const Resource::Description > /*newDescription*/,
                         Resource::Resource& /*resource*/)
{
    motor_info("reloading text");
}

void TextManager::unload(weak< const Resource::Description > /*description*/,
                         Resource::Resource& /*resource*/)
{
    motor_info("unloading text");
}

}  // namespace Motor
