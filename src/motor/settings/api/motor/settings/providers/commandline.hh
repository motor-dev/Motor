/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/settings/stdafx.h>
#include <motor/settings/settingsprovider.hh>

namespace Motor { namespace Settings {

class motor_api(SETTINGS) CommandLineSettingsProvider : public SettingsProvider
{
private:
    minitl::hashmap< istring, SettingsProvider::SettingsList > buildSettings(int         argc,
                                                                             const char* argv[]);

    virtual void log(const Meta::AST::Message& message) const override;

public:
    CommandLineSettingsProvider(int argc, const char* argv[], ref< Folder > folder);
    ~CommandLineSettingsProvider();
};

}}  // namespace Motor::Settings
