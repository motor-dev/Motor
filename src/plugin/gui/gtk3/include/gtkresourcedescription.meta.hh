/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GTKRESOURCEDESCRIPTION_HH_
#define MOTOR_UI_GTK3_GTKRESOURCEDESCRIPTION_HH_
/**************************************************************************************************/
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
    ~GtkResourceDescription();
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
