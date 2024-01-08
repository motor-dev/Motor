/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_DYNOBJECT_HH
#define MOTOR_PLUGIN_DYNOBJECT_HH

#include <motor/plugin/stdafx.h>
#include <motor/core/string/istring.hh>

namespace Motor { namespace Plugin {

class motor_api(PLUGIN) DynamicObject
{
private:
    template < typename T >
    union Symbol
    {
        void* pointer;
        T*    symbol;
    };
    typedef void* Handle;

private:
    Handle m_handle;

private:
    static Handle load(const inamespace& pluginName, const ipath& pluginPath);
    static void   unload(Handle handle);
    static void*  getSymbolInternal(Handle handle, const istring& symbolName);

public:
    DynamicObject(const inamespace& objectName, const ipath& objectPath);
    ~DynamicObject();

    operator const void*() const  // NOLINT(google-explicit-constructor)
    {
        return m_handle;
    }
    bool operator!() const
    {
        return m_handle == nullptr;
    }

    template < typename T >
    T* getSymbol(const istring& name) const
    {
        Symbol< T > s;
        s.pointer = getSymbolInternal(m_handle, name);
        return s.symbol;
    }
};

}}  // namespace Motor::Plugin

#endif
