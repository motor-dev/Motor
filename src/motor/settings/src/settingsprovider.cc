/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/settings/stdafx.h>
#include <motor/meta/engine/namespace.hh>
#include <motor/settings/settings.factory.hh>
#include <motor/settings/settingsprovider.hh>

#include <motor/minitl/type_traits.hh>

namespace Motor { namespace Settings {

void SettingsProvider::addSetting(minitl::hashmap< istring, SettingsList >& container,
                                  istring category, istring name, ref< Meta::AST::Node > value)
{
    minitl::hashmap< istring, SettingsList >::iterator where;
    where = container.insert(category, SettingsList(Arena::general())).first;
    for(auto& it: where->second)
    {
        if(it.first == name)
        {
            motor_warning_format(Log::settings(), "setting {0}.{1} overriden; first value ignored",
                                 category, name);
            it.third = value;
            return;
        }
    }
    where->second.push_back(minitl::make_tuple(
        name,
        ref< Meta::AST::Namespace >::create(Arena::general(), minitl::byref(Arena::general())),
        value));
}

SettingsProvider::SettingsProvider(const minitl::hashmap< istring, SettingsList >& initialSettings,
                                   const ref< Folder >&                            folder)
    : m_settings(Arena::general(), initialSettings)
    , m_folder(folder)
{
    SettingsRegistration::getSettingsList().push_back(*this);
    SettingsBase::onProviderAdded(this);
}

SettingsProvider::~SettingsProvider()
{
    this->unhook();
}

SettingsProvider::SettingsRegistration::SettingsRegistration(SettingsBase& settings)
{
    const minitl::intrusive_list< SettingsProvider >& providers = getSettingsList();
    for(const auto& provider: providers)
    {
        provider.apply(settings);
    }
}

SettingsProvider::SettingsRegistration::~SettingsRegistration() = default;

minitl::intrusive_list< SettingsProvider >&
SettingsProvider::SettingsRegistration::getSettingsList()
{
    static minitl::intrusive_list< SettingsProvider > s_providerList;
    return s_providerList;
}

void SettingsProvider::apply(SettingsBase& settings) const
{
    Meta::Type type
        = Meta::Type::makeType(settings.m_settingsClass, Meta::Type::Indirection::Value,
                               Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    Meta::Value settingsValue = Meta::Value(type, &settings);
    for(const auto& category: m_settings)
    {
        if(category.first == settings.m_settingsClass->name)
        {
            for(const auto& setting: category.second)
            {
                raw< const Meta::Property > property
                    = settings.m_settingsClass->getProperty(setting.first);
                if(!property)
                {
                    motor_error_format(Log::settings(), "Unknwon setting {0} in category {1}",
                                       setting.first, category.first);
                }
                else
                {
                    Meta::AST::DbContext context(Arena::stack(), setting.second, m_folder);
                    setting.third->resolve(context);
                    Meta::Value v = setting.third->eval(property->type);
                    if(!context.errorCount)
                    {
                        property->set(settingsValue, v);
                    }
                    for(Meta::AST::MessageList::const_iterator message = context.messages.begin();
                        message != context.messages.end(); ++message)
                    {
                        log(*message);
                    }
                }
            }
        }
    }
}

}}  // namespace Motor::Settings
