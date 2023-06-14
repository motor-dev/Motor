/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SETTINGS_SETTINGS_PROVIDERS_COMMANDLINE_HH
#define MOTOR_SETTINGS_SETTINGS_PROVIDERS_COMMANDLINE_HH

#include <motor/settings/stdafx.h>
#include <motor/settings/settingsprovider.hh>

namespace Motor { namespace Settings {

class motor_api(SETTINGS) CommandLineSettingsProvider : public SettingsProvider
{
private:
    static minitl::hashmap< istring, SettingsProvider::SettingsList > buildSettings(
        int argc, const char* argv[]);

    void log(const Meta::AST::Message& message) const override;

public:
    CommandLineSettingsProvider(int argc, const char* argv[], const ref< Folder >& folder);
    ~CommandLineSettingsProvider() override;
};

}}  // namespace Motor::Settings

#endif
