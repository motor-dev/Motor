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

namespace Motor {

MOTOR_EXPORT raw< Meta::Class > motor_motor_Namespace_Motor_Settings();

namespace Meta {

template < typename T >
struct ClassID< Settings::Settings< T > >
{
    MOTOR_EXPORT static raw< const Meta::Class > klass();
    MOTOR_EXPORT static istring                  name()
    {
        static const istring s_name(
            minitl::format< 2048u >(FMT("Settings<{0}>"), TypeID< T >::name()));
        return s_name;
    }
};

}  // namespace Meta

namespace Settings {

template < typename T >
struct MOTOR_EXPORT Settings_RTTIHelper
{
    static Meta::Value trampoline_method_get_overload_0(raw< const Meta::Method > method,
                                                        Meta::Value*              parameters,
                                                        u32                       parameterCount);
    static const Meta::Method::Overload s_method_get_overloads;
    static const Meta::Method           s_method;
};

template < typename T >
Meta::Value Settings_RTTIHelper< T >::trampoline_method_get_overload_0(
    raw< const Meta::Method > method, Meta::Value* parameters, u32 parameterCount)
{
    motor_forceuse(method);
    motor_assert_format(parameterCount == 0, "expected no parameter; received {0}", parameterCount);
    motor_forceuse(parameters);
    return Meta::Value(Meta::Value::ByRef(Settings< T >::get()));
}

template < typename T >
const Meta::Method::Overload Settings_RTTIHelper< T >::s_method_get_overloads
    = {{nullptr},
       {nullptr, nullptr},
       motor_type< T& >(),
       false,
       false,
       &trampoline_method_get_overload_0};

template < typename T >
const Meta::Method Settings_RTTIHelper< T >::s_method
    = {{motor_class< void >()->methods},
       istring("get"),
       {&s_method_get_overloads, &s_method_get_overloads + 1}};

}  // namespace Settings

template < typename T >
MOTOR_EXPORT raw< const Meta::Class > Meta::ClassID< Settings::Settings< T > >::klass()
{
    static Meta::Class       s_class = {name(),
                                        0,
                                        motor_class< void >(),
                                        0,
                                        motor_class< void >()->objects,
                                        motor_class< void >()->tags,
                                        motor_class< void >()->properties,
                                        {&Settings::Settings_RTTIHelper< T >::s_method},
                                        {nullptr},
                                        motor_class< void >()->interfaces,
                                        nullptr,
                                        nullptr};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

}  // namespace Motor

#endif
