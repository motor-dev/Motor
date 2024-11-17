/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/meta/stdafx.h>
#include <motor/meta/class.meta.hh>

#include <motor/meta/builtins/numbers.hh>
#include <motor/meta/interfacetable.hh>
#include <motor/meta/namespace.hh>

namespace Motor { namespace Meta {
const Object s_objects[] = {{{&s_objects[1]},
                             motor_motor_Namespace(),
                             ClassID< void >::name(),
                             Value(raw< const Class >{&ClassID< void >::s_class})},

                            {{&s_objects[2]},
                             motor_motor_Namespace(),
                             ClassID< minitl::pointer >::name(),
                             Value(ClassID< minitl::pointer >::klass())},

                            {{&s_objects[3]},
                             motor_motor_Namespace(),
                             ClassID< bool >::name(),
                             Value(ClassID< bool >::klass())},

                            {{&s_objects[4]},
                             motor_motor_Namespace(),
                             ClassID< u8 >::name(),
                             Value(ClassID< u8 >::klass())},

                            {{&s_objects[5]},
                             motor_motor_Namespace(),
                             ClassID< i8 >::name(),
                             Value(ClassID< i8 >::klass())},

                            {{&s_objects[6]},
                             motor_motor_Namespace(),
                             ClassID< u16 >::name(),
                             Value(ClassID< u16 >::klass())},

                            {{&s_objects[7]},
                             motor_motor_Namespace(),
                             ClassID< i16 >::name(),
                             Value(ClassID< i16 >::klass())},

                            {{&s_objects[8]},
                             motor_motor_Namespace(),
                             ClassID< u32 >::name(),
                             Value(ClassID< i32 >::klass())},

                            {{&s_objects[9]},
                             motor_motor_Namespace(),
                             ClassID< i32 >::name(),
                             Value(ClassID< i32 >::klass())},

                            {{&s_objects[10]},
                             motor_motor_Namespace(),
                             ClassID< u64 >::name(),
                             Value(ClassID< u64 >::klass())},

                            {{&s_objects[11]},
                             motor_motor_Namespace(),
                             ClassID< i64 >::name(),
                             Value(ClassID< i64 >::klass())},

                            {{&s_objects[12]},
                             motor_motor_Namespace(),
                             ClassID< float >::name(),
                             Value(ClassID< float >::klass())},

                            {{motor_motor_Namespace()->objects.exchange(s_objects)},
                             motor_motor_Namespace(),
                             ClassID< double >::name(),
                             Value(ClassID< double >::klass())}};

static void nullconstructor(const void* /*src*/, void* /*dst*/)
{
}

template <typename T>
static void copyconstructor(const void* src, void* dst)
{
    memcpy(dst, src, sizeof(T));
}

static void nulldestructor(void*)
{
}

static InterfaceTable s_emptyTable
    = {{nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr},
       {nullptr}, {nullptr}, {nullptr}, {nullptr}, {nullptr}, nullptr};

template <typename FROM, typename TO>
static Value construct(FROM t)
{
    return Value(TO(t));
}

template <typename FROM, typename TO>
static FROM get(const Value& value)
{
    return FROM(value.as< TO >());
}

template <typename FROM, typename TO>
static InterfaceTable::TypeInterface< FROM > s_builtinInterfaceType
    = {TypeID< TO >::type(), &construct< FROM, TO >, &get< FROM, TO >};

template <typename TO>
static InterfaceTable s_builtinInterface = {{&s_builtinInterfaceType< bool, TO >},
                                            {&s_builtinInterfaceType< i64, TO >},
                                            {&s_builtinInterfaceType< u64, TO >},
                                            {&s_builtinInterfaceType< float, TO >},
                                            {&s_builtinInterfaceType< double, TO >},
                                            {nullptr},
                                            {nullptr},
                                            {nullptr},
                                            {nullptr},
                                            {nullptr},
                                            {nullptr},
                                            {nullptr}

};

MOTOR_EXPORT istring ClassID< void >::name()
{
    static const istring s_name("void");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< void >::s_class
    = {0, {nullptr}, 0, {&s_objects[0]}, {nullptr}, {nullptr},
       {nullptr}, {nullptr}, {nullptr}, {&s_emptyTable}, &nullconstructor, &nulldestructor};

MOTOR_EXPORT istring ClassID< minitl::pointer >::name()
{
    static const istring s_name("pointer");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< minitl::pointer >::s_class = {0,
                                                                ClassID< void >::klass(),
                                                                0,
                                                                {&s_objects[1]},
                                                                {nullptr},
                                                                {nullptr},
                                                                {nullptr},
                                                                {nullptr},
                                                                {nullptr},
                                                                {&s_emptyTable},
                                                                &nullconstructor,
                                                                &nulldestructor};

MOTOR_EXPORT istring ClassID< bool >::name()
{
    static const istring s_name("bool");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< bool >::s_class = {sizeof(bool),
                                                     ClassID< void >::klass(),
                                                     0,
                                                     {&s_objects[2]},
                                                     {nullptr},
                                                     {nullptr},
                                                     {nullptr},
                                                     {nullptr},
                                                     {nullptr},
                                                     {&s_builtinInterface< bool >},
                                                     &copyconstructor< bool >,
                                                     &nulldestructor};

MOTOR_EXPORT istring ClassID< u8 >::name()
{
    static const istring s_name("u8");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< u8 >::s_class = {sizeof(u8),
                                                   ClassID< void >::klass(),
                                                   0,
                                                   {&s_objects[3]},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {&s_builtinInterface< u8 >},
                                                   &copyconstructor< u8 >,
                                                   &nulldestructor};

MOTOR_EXPORT istring ClassID< i8 >::name()
{
    static const istring s_name("i8");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< i8 >::s_class = {sizeof(i8),
                                                   ClassID< void >::klass(),
                                                   0,
                                                   {&s_objects[4]},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {nullptr},
                                                   {&s_builtinInterface< i8 >},
                                                   &copyconstructor< i8 >,
                                                   &nulldestructor};

MOTOR_EXPORT istring ClassID< u16 >::name()
{
    static const istring s_name("u16");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< u16 >::s_class = {sizeof(u16),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[5]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< u16 >},
                                                    &copyconstructor< u16 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< i16 >::name()
{
    static const istring s_name("i16");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< i16 >::s_class = {sizeof(i16),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[6]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< i16 >},
                                                    &copyconstructor< i16 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< u32 >::name()
{
    static const istring s_name("u32");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< u32 >::s_class = {sizeof(u32),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[7]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< u32 >},
                                                    &copyconstructor< u32 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< i32 >::name()
{
    static const istring s_name("i32");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< i32 >::s_class = {sizeof(i32),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[8]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< i32 >},
                                                    &copyconstructor< i32 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< u64 >::name()
{
    static const istring s_name("u64");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< u64 >::s_class = {sizeof(u64),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[9]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< u64 >},
                                                    &copyconstructor< u64 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< i64 >::name()
{
    static const istring s_name("i64");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< i64 >::s_class = {sizeof(i64),
                                                    ClassID< void >::klass(),
                                                    0,
                                                    {&s_objects[10]},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {nullptr},
                                                    {&s_builtinInterface< i64 >},
                                                    &copyconstructor< i64 >,
                                                    &nulldestructor};

MOTOR_EXPORT istring ClassID< float >::name()
{
    static const istring s_name("float");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< float >::s_class = {sizeof(float),
                                                      ClassID< void >::klass(),
                                                      0,
                                                      {&s_objects[11]},
                                                      {nullptr},
                                                      {nullptr},
                                                      {nullptr},
                                                      {nullptr},
                                                      {nullptr},
                                                      {&s_builtinInterface< float >},
                                                      &copyconstructor< float >,
                                                      &nulldestructor};

MOTOR_EXPORT istring ClassID< double >::name()
{
    static const istring s_name("double");
    return s_name;
}

MOTOR_EXPORT const Class ClassID< double >::s_class = {sizeof(double),
                                                       ClassID< void >::klass(),
                                                       0,
                                                       {&s_objects[12]},
                                                       {nullptr},
                                                       {nullptr},
                                                       {nullptr},
                                                       {nullptr},
                                                       {nullptr},
                                                       {&s_builtinInterface< double >},
                                                       &copyconstructor< double >,
                                                       &nulldestructor};

const ConversionCost ConversionCost::s_incompatible{0, 0, 0, 0, 1};
const ConversionCost ConversionCost::s_variant{0, 0, 0, 1, 0};
}} // namespace Motor::Meta
