/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/meta/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/meta/engine/helper/staticarray.hh>
#include <motor/meta/engine/objectinfo.meta.hh>
#include <motor/meta/engine/operatortable.meta.hh>

#define MOTOR_REGISTER_NAMESPACE_1_NAMED(plugin, n)                                                \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##plugin##_Namespace();                                               \
    raw< Meta::Class > motor_##plugin##_Namespace_##n()                                            \
    {                                                                                              \
        static Meta::Class ci                                                                      \
            = {istring(#n), 0,      0,   Meta::ClassType_Namespace,         {0}, {0}, {0}, {0},    \
               {0, 0},      {0, 0}, {0}, Meta::OperatorTable::s_emptyTable, 0,   0};               \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    static Meta::ObjectInfo s_##plugin##_Namespace_##n##_ob                                        \
        = {motor_##plugin##_Namespace()->objects,                                                  \
           {0},                                                                                    \
           istring(#n),                                                                            \
           Meta::Value(motor_##plugin##_Namespace_##n())};                                         \
    MOTOR_EXPORT const Meta::ObjectInfo* s_##plugin##_Namespace_##n##_r                            \
        = motor_##plugin##_Namespace()->objects.set(&s_##plugin##_Namespace_##n##_ob);             \
    }

#define MOTOR_REGISTER_NAMESPACE_2_NAMED(plugin, n1, n2)                                           \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1();                                          \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2()                                    \
    {                                                                                              \
        static Meta::Class ci  = {istring(#n2),                                                    \
                                  0,                                                               \
                                  0,                                                               \
                                  Meta::ClassType_Namespace,                                       \
                                  {motor_##plugin##_Namespace_##n1().m_ptr},                       \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0, 0},                                                          \
                                  {0, 0},                                                          \
                                  {0},                                                             \
                                  Meta::OperatorTable::s_emptyTable,                               \
                                  0,                                                               \
                                  0};                                                              \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    static Meta::ObjectInfo s_##plugin##_Namespace_##n1##_##n2##_ob                                \
        = {motor_##plugin##_Namespace_##n1()->objects,                                             \
           {0},                                                                                    \
           istring(#n2),                                                                           \
           Meta::Value(motor_##plugin##_Namespace_##n1##_##n2())};                                 \
    MOTOR_EXPORT const Meta::ObjectInfo* s_##plugin##_Namespace_##n1##_##n2##_r                    \
        = motor_##plugin##_Namespace_##n1()->objects.set(                                          \
            &s_##plugin##_Namespace_##n1##_##n2##_ob);                                             \
    }

#define MOTOR_REGISTER_NAMESPACE_3_NAMED(plugin, n1, n2, n3)                                       \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2();                                   \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2##_##n3()                             \
    {                                                                                              \
        static Meta::Class ci  = {istring(#n3),                                                    \
                                  0,                                                               \
                                  0,                                                               \
                                  Meta::ClassType_Namespace,                                       \
                                  {motor_##plugin##_Namespace_##n1##_##n2().m_ptr},                \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0, 0},                                                          \
                                  {0, 0},                                                          \
                                  {0},                                                             \
                                  Meta::OperatorTable::s_emptyTable,                               \
                                  0,                                                               \
                                  0};                                                              \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    static Meta::ObjectInfo s_##plugin##_Namespace_##n1##_##n2##_##n3##_ob                         \
        = {motor_##plugin##_Namespace_##n1##_##n2()->objects,                                      \
           {0},                                                                                    \
           istring(#n3),                                                                           \
           Meta::Value(motor_##plugin##_Namespace_##n1##_##n2##_##n3())};                          \
    MOTOR_EXPORT const Meta::ObjectInfo* s_##plugin##_Namespace_##n1##_##n2##_##n3##_r             \
        = motor_##plugin##_Namespace_##n1##_##n2()->objects.set(                                   \
            &s_##plugin##_Namespace_##n1##_##n2##_##n3##_ob);                                      \
    }

#define MOTOR_REGISTER_NAMESPACE_4_NAMED(plugin, n1, n2, n3, n4)                                   \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2##_##n3();                            \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4()                      \
    {                                                                                              \
        static Meta::Class ci  = {istring(#n4),                                                    \
                                  0,                                                               \
                                  0,                                                               \
                                  Meta::ClassType_Namespace,                                       \
                                  {motor_##plugin##_Namespace_##n1##_##n2##_##n3().m_ptr},         \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0, 0},                                                          \
                                  {0, 0},                                                          \
                                  {0},                                                             \
                                  Meta::OperatorTable::s_emptyTable,                               \
                                  0,                                                               \
                                  0};                                                              \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    static Meta::ObjectInfo s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_ob                  \
        = {motor_##plugin##_Namespace_##n1##_##n2##_##n3()->objects,                               \
           {0},                                                                                    \
           istring(#n4),                                                                           \
           Meta::Value(motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4())};                   \
    MOTOR_EXPORT const Meta::ObjectInfo* s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_r      \
        = motor_##plugin##_Namespace_##n1##_##n2##_##n3()->objects.set(                            \
            &s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_ob);                               \
    }

#define MOTOR_REGISTER_NAMESPACE_5_NAMED(plugin, n1, n2, n3, n4, n5)                               \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4();                     \
    raw< Meta::Class > motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_##n5()               \
    {                                                                                              \
        static Meta::Class ci  = {istring(#n5),                                                    \
                                  0,                                                               \
                                  0,                                                               \
                                  Meta::ClassType_Namespace,                                       \
                                  {motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4().m_ptr},  \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0},                                                             \
                                  {0, 0},                                                          \
                                  {0, 0},                                                          \
                                  {0},                                                             \
                                  Meta::OperatorTable::s_emptyTable,                               \
                                  0,                                                               \
                                  0};                                                              \
        raw< Meta::Class > ptr = {&ci};                                                            \
        return ptr;                                                                                \
    }                                                                                              \
    static Meta::ObjectInfo s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_##n5##_ob           \
        = {motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4()->objects,                        \
           {0},                                                                                    \
           istring(#n5),                                                                           \
           Meta::Value(motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_##n5())};            \
    MOTOR_EXPORT const Meta::ObjectInfo*                                                           \
                       s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_##n5##_r                 \
        = motor_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4()->objects.set(                     \
            &s_##plugin##_Namespace_##n1##_##n2##_##n3##_##n4##_##n5##_ob);                        \
    }

#define MOTOR_REGISTER_NAMESPACE_1_(plugin, n1)     MOTOR_REGISTER_NAMESPACE_1_NAMED(plugin, n1)
#define MOTOR_REGISTER_NAMESPACE_2_(plugin, n1, n2) MOTOR_REGISTER_NAMESPACE_2_NAMED(plugin, n1, n2)
#define MOTOR_REGISTER_NAMESPACE_3_(plugin, n1, n2, n3)                                            \
    MOTOR_REGISTER_NAMESPACE_3_NAMED(plugin, n1, n2, n3)
#define MOTOR_REGISTER_NAMESPACE_4_(plugin, n1, n2, n3, n4)                                        \
    MOTOR_REGISTER_NAMESPACE_4_NAMED(plugin, n1, n2, n3, n4)
#define MOTOR_REGISTER_NAMESPACE_5_(plugin, n1, n2, n3, n4, n5)                                    \
    MOTOR_REGISTER_NAMESPACE_5_NAMED(plugin, n1, n2, n3, n4, n5)

#define MOTOR_REGISTER_NAMESPACE_1(n1)     MOTOR_REGISTER_NAMESPACE_1_(MOTOR_PROJECTID, n1)
#define MOTOR_REGISTER_NAMESPACE_2(n1, n2) MOTOR_REGISTER_NAMESPACE_2_(MOTOR_PROJECTID, n1, n2)
#define MOTOR_REGISTER_NAMESPACE_3(n1, n2, n3)                                                     \
    MOTOR_REGISTER_NAMESPACE_3_(MOTOR_PROJECTID, n1, n2, n3)
#define MOTOR_REGISTER_NAMESPACE_4(n1, n2, n3, n4)                                                 \
    MOTOR_REGISTER_NAMESPACE_4_(MOTOR_PROJECTID, n1, n2, n3, n4)
#define MOTOR_REGISTER_NAMESPACE_5(n1, n2, n3, n4, n5)                                             \
    MOTOR_REGISTER_NAMESPACE_5_(MOTOR_PROJECTID, n1, n2, n3, n4, n5)

#define MOTOR_REGISTER_ROOT_NAMESPACE_(id, parent, name)                                           \
    namespace Motor {                                                                              \
    raw< Meta::Class > motor_##id##_Namespace##parent();                                           \
    raw< Meta::Class > motor_##id##_Namespace##parent##_##name()                                   \
    {                                                                                              \
        return motor_##id##_Namespace();                                                           \
    }                                                                                              \
    static Meta::ObjectInfo ob##id##parent##_##name = {motor_##id##_Namespace##parent()->objects,  \
                                                       {0},                                        \
                                                       istring(#name),                             \
                                                       Meta::Value(motor_##id##_Namespace())};     \
    MOTOR_EXPORT const Meta::ObjectInfo* s_namespaceRegistration_##id##parent##_##name             \
        = (motor_##id##_Namespace##parent()->objects.m_ptr = &ob##id##parent##_##name);            \
    }
#define MOTOR_REGISTER_ROOT_NAMESPACE(id, ns, parent) MOTOR_REGISTER_ROOT_NAMESPACE_(id, ns, parent)
