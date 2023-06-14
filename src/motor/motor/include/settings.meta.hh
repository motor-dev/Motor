/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_MOTOR_SETTINGS_META_HH
#define MOTOR_MOTOR_SETTINGS_META_HH

#include <motor/stdafx.h>
#include <motor/settings/settings.factory.hh>

namespace Motor { namespace MainSettings {

struct Log : public Settings::Settings< Log >
{
    bool enableConsoleLog;
    bool enableFileLog;

    Log() : enableConsoleLog(true), enableFileLog(true)
    {
    }
};

}}  // namespace Motor::MainSettings

#endif
