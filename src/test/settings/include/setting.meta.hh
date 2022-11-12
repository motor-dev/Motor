/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <stdafx.h>
#include <motor/settings/settings.factory.hh>

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
