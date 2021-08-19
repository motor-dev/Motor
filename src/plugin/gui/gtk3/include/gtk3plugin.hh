/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GUI_GTK3_GTK3PLUGIN_HH_
#define MOTOR_GUI_GTK3_GTK3PLUGIN_HH_
/**************************************************************************************************/
#include <glib-object.h>
#include <motor/core/memory/allocators/system.hh>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin
{
private:
    struct Page;

private:
    SystemAllocator m_allocator;
    Page*           m_firstPage;
    GQuark          m_motorQuark;

public:
    Gtk3Plugin();
    ~Gtk3Plugin();
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
