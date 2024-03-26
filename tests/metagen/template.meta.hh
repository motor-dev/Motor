#pragma once

template < typename T >
class X
{
public:
    template < typename T2 >
    class Y;
};

template < typename T >
template < typename T2 >
class X< T >::Y
{
    void f();
};

template < typename T >
template < typename T2 >
void X< T >::Y< T2 >::f()
{
}

#include <template.meta.factory.hh>
