/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_SETTINGS_SETTINGS_FACTORY_HH
#define MOTOR_SETTINGS_SETTINGS_FACTORY_HH

#include <motor/settings/stdafx.h>
#include <motor/meta/method.meta.hh>
#include <motor/meta/object.meta.hh>
#include <motor/meta/property.meta.hh>
#include <motor/meta/typeinfo.hh>
#include <motor/meta/value.hh>
#include <motor/settings/settingsprovider.hh>

namespace Motor { namespace Settings {

template < typename T >
struct Settings;

struct motor_api(SETTINGS) SettingsBase : public minitl::intrusive_list< SettingsBase >::item
{
    template < typename T >
    friend struct Settings;
    friend class SettingsProvider;

private:
    static minitl::intrusive_list< SettingsBase >& getSettings();

private:
    raw< const Meta::Class > const m_settingsClass;

private:
    static void onProviderAdded(const weak< const SettingsProvider >& provider);

protected:
    explicit SettingsBase(raw< const Meta::Class > settingsClass);
    ~SettingsBase();
};

template < typename T >
struct Settings : public SettingsBase
{
private:
    MOTOR_EXPORT static SettingsProvider::SettingsRegistration s_registration;
    MOTOR_EXPORT static T&                                     getStaticSettings()
    {
        static T s_settings;
        return s_settings;
    }

protected:
    Settings() : SettingsBase(motor_class< T >())
    {
        (void)s_registration;
    }

public:
    MOTOR_EXPORT static const T& get()
    {
        return getStaticSettings();
    }
};

template < typename T >
MOTOR_EXPORT SettingsProvider::SettingsRegistration
             Settings< T >::s_registration(getStaticSettings());

}}  // namespace Motor::Settings

#include <motor/settings/settings.meta.factory.hh>
#endif
