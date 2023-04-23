/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.text/stdafx.h>
#include <textmanager.hh>

namespace Motor {

TextManager::TextManager() = default;

TextManager::~TextManager() = default;

void TextManager::load(const weak< const Resource::IDescription >& /*description*/,
                       Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "loading text");
}

void TextManager::reload(const weak< const Resource::IDescription >& /*oldDescription*/,
                         const weak< const Resource::IDescription >& /*newDescription*/,
                         Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "reloading text");
}

void TextManager::unload(const weak< const Resource::IDescription >& /*description*/,
                         Resource::Resource& /*resource*/)
{
    motor_info(Log::resource(), "unloading text");
}

}  // namespace Motor
