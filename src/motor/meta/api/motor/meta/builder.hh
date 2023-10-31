/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */                                                                       \
#ifndef MOTOR_META_BUILDER_HH
#define MOTOR_META_BUILDER_HH

namespace Motor { namespace Meta {

template < typename T >
void metaCopy(const void* source, void* dest)
{
    new(dest) T(*reinterpret_cast< const T* >(source));
}

template < typename T >
void metaDestroy(void* source)
{
    reinterpret_cast< T* >(source)->~T();
}

}}  // namespace Motor::Meta

#endif  // MOTOR_META_BUILDER_HH
