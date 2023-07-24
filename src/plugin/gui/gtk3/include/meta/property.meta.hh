/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_META_PROPERTY_META_HH
#define MOTOR_PLUGIN_GUI_GTK3_META_PROPERTY_META_HH

#include <stdafx.h>
#include <motor/meta/property.meta.hh>

namespace Motor { namespace Gtk3 {

class Property
{
public:
    Meta::Property metaProperty;

public:
    [[motor::meta(noexport)]] const guint propertyId {};

    [[motor::meta(noexport)]] static Meta::Value get(raw< const Meta::Property > property,
                                                     const void*                 data);
    [[motor::meta(noexport)]] static void set(raw< const Meta::Property > property, void* data,
                                              const Meta::Value& value);
};

}}  // namespace Motor::Gtk3

#endif
