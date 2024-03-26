/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GUI_GTK3_GTKRESOURCEDESCRIPTION_META_HH
#define MOTOR_PLUGIN_GUI_GTK3_GTKRESOURCEDESCRIPTION_META_HH

#include <stdafx.h>
#include <motor/resource/description.hh>

namespace Motor { namespace Gtk3 {

struct GBoxedWrapper
{
public:
    gpointer value;
};

struct GEnumWrapper
{
public:
    gint value;
};

struct GFlagsWrapper
{
public:
    guint value;
};

struct GObjectWrapper
{
public:
    GObject* value;
};

class GtkResourceDescription : public Resource::Description< GtkResourceDescription >
{
protected:
    GtkResourceDescription();
    ~GtkResourceDescription() override;
};

}}  // namespace Motor::Gtk3

#include <gtkresourcedescription.meta.factory.hh>
#endif
