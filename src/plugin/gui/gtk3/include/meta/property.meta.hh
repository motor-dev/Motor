/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_META_PROPERTY_META_HH_
#define MOTOR_UI_GTK3_META_PROPERTY_META_HH_
/**************************************************************************************************/
#include <stdafx.h>
#include <motor/meta/engine/propertyinfo.meta.hh>

namespace Motor { namespace Gtk3 {

struct Property
{
    Meta::Property metaProperty;

public:
    const guint propertyId;

    static Meta::Value get(raw< const Meta::Property > property, const void* data);
    static void set(raw< const Meta::Property > property, void* data, const Meta::Value& value);
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
