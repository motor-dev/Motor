/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SETTINGS_SETTINGSPROVIDER_HH_
#define MOTOR_SETTINGS_SETTINGSPROVIDER_HH_
/**************************************************************************************************/
#include <motor/settings/stdafx.h>
#include <motor/minitl/tuple.hh>
#include <motor/minitl/vector.hh>
#include <motor/reflection/valueparse.hh>

namespace Motor { namespace Settings {

struct SettingsBase;
template < typename T >
struct Settings;

class motor_api(SETTINGS) SettingsProvider
    : public minitl::refcountable
    , public minitl::intrusive_list< SettingsProvider >::item
{
    friend struct SettingsBase;
    template < typename T >
    friend struct Settings;

private:
    struct motor_api(SETTINGS) SettingsRegistration
    {
        static minitl::intrusive_list< SettingsProvider >& getSettingsList();
        SettingsRegistration(SettingsBase & settings);
        ~SettingsRegistration();
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
    SettingsProvider(const SettingsCategoryMap& initialSettings, ref< Folder > folder);
    virtual ~SettingsProvider();

    static void  addSetting(SettingsCategoryMap & container, istring category, istring name,
                            ref< Meta::AST::Node > value);
    virtual void log(const Meta::AST::Message& message) const = 0;

private:
    void apply(SettingsBase & settings) const;
};

}}  // namespace Motor::Settings

/**************************************************************************************************/
#endif
