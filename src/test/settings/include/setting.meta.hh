/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_TEST_SETTINGS_SETTINGS_META_HH
#define MOTOR_TEST_SETTINGS_SETTINGS_META_HH

#include <stdafx.h>
#include <motor/settings/settings.meta.hh>

namespace Motor { namespace TestSettings {

enum EnumSetting
{
    EnumSettingValue1,
    EnumSettingValue2
};

struct TestSettings : public Settings::Settings< TestSettings >
{
    EnumSetting enumSetting;

    TestSettings() : enumSetting(EnumSettingValue1)
    {
    }
};

}}  // namespace Motor::TestSettings

#include <setting.meta.factory.hh>
#endif
