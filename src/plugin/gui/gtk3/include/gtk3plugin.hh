/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/core/memory/allocators/system.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <glib-object.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin
{
private:
    struct Page;

private:
    SystemAllocator               m_allocator;
    Page*                         m_firstPage {};
    GQuark                        m_motorQuark;
    raw< const Meta::ObjectInfo > m_objectPtr;
    weak< Logger >                m_logger;
    guint                         m_logHandlerDefault;
    guint                         m_logHandlerGLib;
    guint                         m_logHandlerGtk;

private:
    void* allocate(u32 size);

    void registerBoxed(GType type);
    void registerEnum(GType type);
    void registerFlags(GType type);
    void registerInterface(GType type);
    void registerClass(GType type);
    void unregisterClass(GType type);
    void unregisterInterface(GType type);

public:
    Gtk3Plugin();
    ~Gtk3Plugin();

    template < typename T >
    T* allocate()
    {
        return static_cast< T* >(allocate(sizeof(T)));
    }
    template < typename T >
    T* allocateArray(u32 count)
    {
        return static_cast< T* >(allocate(count * sizeof(T)));
    }
    GQuark quark() const
    {
        return m_motorQuark;
    }

    void        registerValue(const istring& name, const Meta::Value& value);
    Meta::Type  fromGType(GType type);
    Meta::Value fromGValue(const GValue* value);
};

}}  // namespace Motor::Gtk3
