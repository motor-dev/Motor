/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PLUGIN_DYNOBJECTLIST_HH_
#define MOTOR_PLUGIN_DYNOBJECTLIST_HH_
/**************************************************************************************************/
#include <motor/plugin/stdafx.h>

namespace Motor { namespace Plugin {

class DynamicObject;

#ifdef MOTOR_STATIC

class motor_api(PLUGIN) DynamicObjectList
{
private:
    static DynamicObjectList* s_dynamicObjectRoot;

private:
    struct SymbolPointer
    {
        void* data1;
        void* data2;
    };
    template < typename SYMBOL >
    union SymbolObject
    {
        SymbolPointer pointer;
        SYMBOL        symbol;
    };
    struct Symbol
    {
        const char*   name;
        SymbolPointer symbol;
        Symbol();
    };

private:
    DynamicObjectList* m_next;
    const char* const  m_name;
    Symbol             m_symbols[16];
    u32                m_symbolCount;

private:
    bool                 registerSymbolInternal(const char* name, SymbolPointer value);
    const SymbolPointer* findSymbolInternal(const char* name) const;

public:
    DynamicObjectList(const char* name);
    ~DynamicObjectList();

    template < typename SYMBOL >
    bool registerSymbol(SYMBOL symbol, const char* name)
    {
        SymbolObject< SYMBOL > s;
        s.symbol = symbol;
        return registerSymbolInternal(name, s.pointer);
    }
    template < typename SYMBOL >
    SYMBOL findSymbol(const char* name) const
    {
        const SymbolPointer* ptr = findSymbolInternal(name);
        if(ptr)
        {
            SymbolObject< SYMBOL > s;
            s.pointer = *ptr;
            return s.symbol;
        }
        else
        {
            return 0;
        }
    }
    static DynamicObjectList* findDynamicObject(const char* name);
    static void               showList();
};

#    define _MOTOR_PLUGIN_EXPORT_VAR(var, value) static var = value;
#    define _MOTOR_PLUGIN_EXPORT                 static
#    define _MOTOR_REGISTER_PLUGIN_(id, name)                                                      \
        MOTOR_EXPORT Motor::Plugin::DynamicObjectList s_plugin_##id(#name);
#    define _MOTOR_REGISTER_PLUGIN(id, name) _MOTOR_REGISTER_PLUGIN_(id, name)
#    define _MOTOR_REGISTER_METHOD_(id, x, name)                                                   \
        MOTOR_EXPORT bool s_symbol_##id##_##x = s_plugin_##id.registerSymbol(&x, #name);
#    define _MOTOR_REGISTER_METHOD(id, x)             _MOTOR_REGISTER_METHOD_(id, x, x)
#    define _MOTOR_REGISTER_METHOD_NAMED(id, x, name) _MOTOR_REGISTER_METHOD_(id, x, name)

#else

#    define _MOTOR_PLUGIN_EXPORT_VAR(var, value)                                                   \
        _MOTOR_PLUGIN_EXPORT var;                                                                  \
        var = value;
#    define _MOTOR_PLUGIN_EXPORT extern "C" MOTOR_EXPORT
#    define _MOTOR_REGISTER_PLUGIN(id, name)
#    define _MOTOR_REGISTER_METHOD(id, x)
#    define _MOTOR_REGISTER_METHOD_NAMED(id, x, name)

#endif

}}  // namespace Motor::Plugin

/**************************************************************************************************/
#endif
