/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_UI_GTK3_GOBJECT_HH_
#define MOTOR_UI_GTK3_GOBJECT_HH_
/**************************************************************************************************/
#include <motor/resource/description.script.hh>

namespace Motor {

MOTOR_EXPORT raw< Meta::Class > motor_plugin_ui_gtk3_Namespace();

}

namespace Motor { namespace Gtk3 {

class GObject : public Resource::Description
{
    published : GObject();
    ~GObject();
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
