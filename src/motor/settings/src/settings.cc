/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/settings/stdafx.h>
#include <motor/meta/engine/namespace.hh>
#include <motor/settings/settings.factory.hh>

MOTOR_REGISTER_NAMESPACE_2_NAMED(motor, Motor, Settings)

namespace Motor { namespace Settings {

minitl::intrusive_list< SettingsBase >& SettingsBase::getSettings()
{
    static minitl::intrusive_list< SettingsBase > s_settingsList;
    return s_settingsList;
}

SettingsBase::SettingsBase(raw< const Meta::Class > settingsClass) : m_settingsClass(settingsClass)
{
    getSettings().push_back(*this);
}

SettingsBase::~SettingsBase()
{
    motor_assert_format(this->hooked(), "Settings object {0} was removed from the settings list",
                        m_settingsClass->fullname());
    this->unhook();
}

void SettingsBase::onProviderAdded(const weak< const SettingsProvider >& provider)
{
    for(auto& it: getSettings())
    {
        provider->apply(it);
    }
}

}}  // namespace Motor::Settings
