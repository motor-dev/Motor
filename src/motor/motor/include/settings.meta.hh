/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

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
