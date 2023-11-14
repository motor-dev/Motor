/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SETTINGS_SETTINGSPROVIDER_HH
#define MOTOR_SETTINGS_SETTINGSPROVIDER_HH

#include <motor/settings/stdafx.h>
#include <motor/minitl/tuple.hh>
#include <motor/minitl/vector.hh>
#include <motor/reflection/valueparse.hh>

namespace Motor { namespace Settings {

struct SettingsBase;
template < typename T >
struct Settings;

class motor_api(SETTINGS) SettingsProvider
    : public minitl::pointer
    , public minitl::intrusive_list< SettingsProvider >::item
{
    friend struct SettingsBase;
    template < typename T >
    friend struct Settings;

private:
    struct motor_api(SETTINGS) SettingsRegistration
    {
        static minitl::intrusive_list< SettingsProvider >& getSettingsList();
        explicit SettingsRegistration(SettingsBase & settings);
        ~SettingsRegistration() = default;
    };
    friend struct SettingsRegistration;

protected:
    typedef minitl::vector<
        minitl::tuple< istring, ref< Meta::AST::Namespace >, ref< Meta::AST::Node > > >
                                                     SettingsList;
    typedef minitl::hashmap< istring, SettingsList > SettingsCategoryMap;

private:
    SettingsCategoryMap m_settings;
    ref< Folder >       m_folder;

protected:
    SettingsProvider(SettingsCategoryMap && initialSettings, const ref< Folder >& folder);
    ~SettingsProvider() override;

    static void  addSetting(SettingsCategoryMap & container, istring category, istring name,
                            const ref< Meta::AST::Node >& value);
    virtual void log(const Meta::AST::Message& message) const = 0;

private:
    void apply(SettingsBase & settings) const;
};

}}  // namespace Motor::Settings

#endif
