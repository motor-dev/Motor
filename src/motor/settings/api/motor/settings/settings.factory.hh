/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_SETTINGS_SETTINGS_FACTORY_HH_
#define MOTOR_SETTINGS_SETTINGS_FACTORY_HH_
/**************************************************************************************************/
#include <motor/settings/stdafx.h>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>
#include <motor/meta/engine/propertyinfo.meta.hh>
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
    static void onProviderAdded(weak< const SettingsProvider > provider);

protected:
    SettingsBase(raw< const Meta::Class > settingsClass);
    ~SettingsBase();
};

template < typename T >
struct Settings : public SettingsBase
{
private:
    static MOTOR_EXPORT SettingsProvider::SettingsRegistration s_registration;
    static MOTOR_EXPORT T& getStaticSettings()
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
    static MOTOR_EXPORT const T& get()
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
    static MOTOR_EXPORT raw< const Meta::Class > klass();
    static MOTOR_EXPORT istring                  name()
    {
        static const istring s_name(minitl::format< 2048u >("Settings<%s>") | TypeID< T >::name());
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
    static const Meta::Method::Overload s_method_get_overloads[];
    static const Meta::Method           s_methods[];
};

template < typename T >
Meta::Value
Settings_RTTIHelper< T >::trampoline_method_get_overload_0(raw< const Meta::Method > method,
                                                           Meta::Value* params, u32 paramCount)
{
    motor_forceuse(method);
    motor_assert(paramCount == 0, "expected no parameter; received %d" | paramCount);
    motor_forceuse(params);
    return Meta::Value(Meta::Value::ByRef(Settings< T >::get()));
}

template < typename T >
const Meta::Method::Overload Settings_RTTIHelper< T >::s_method_get_overloads[]
    = {{{0}, {0, 0}, motor_type< T& >(), false, &trampoline_method_get_overload_0}};

template < typename T >
const Meta::Method Settings_RTTIHelper< T >::s_methods[1]
    = {{istring("get"), {1, s_method_get_overloads}, {0}}};

}  // namespace Settings

template < typename T >
MOTOR_EXPORT raw< const Meta::Class > Meta::ClassID< Settings::Settings< T > >::klass()
{
    static Meta::Class       s_class = {name(),
                                  0,
                                  0,
                                  Meta::ClassType_Struct,
                                  {motor_motor_Namespace_Motor_Settings().m_ptr},
                                  motor_class< void >(),
                                  {0},
                                  {0},
                                  {0, 0},
                                  {1, Settings::Settings_RTTIHelper< T >::s_methods},
                                  {0},
                                  Meta::OperatorTable::s_emptyTable,
                                  0,
                                  0};
    raw< const Meta::Class > result  = {&s_class};
    return result;
}

}  // namespace Motor

/**************************************************************************************************/
#endif
