/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GTKRESOURCEDESCRIPTION_HH_
#define MOTOR_UI_GTK3_GTKRESOURCEDESCRIPTION_HH_
/**************************************************************************************************/
#include <motor/resource/description.meta.hh>

namespace Motor { namespace Gtk3 {

struct GBoxedWrapper
{
public:
    gpointer gobject;
};

struct GEnumWrapper
{
public:
    gint gobject;
};

struct GFlagsWrapper
{
public:
    guint gobject;
};

struct GObjectWrapper
{
public:
    GObject* gobject;
};

class GtkResourceDescription : public Resource::Description
{
protected:
    GtkResourceDescription();
    ~GtkResourceDescription();
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
