/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <motor/plugin.graphics.3d/stdafx.h>
#include <motor/plugin.graphics.3d/shader/node.meta.hh>

namespace Motor { namespace Shaders {

class motor_api(3D) Output : public Node
{
protected:
    Output();
    ~Output() override;
};

class motor_api(3D) Float : public Output
{
protected:
    Float();
    ~Float() override;
};

class motor_api(3D) Float2 : public Output
{
protected:
    Float2();
    ~Float2() override;
};

class motor_api(3D) Float3 : public Output
{
protected:
    Float3();
    ~Float3() override;
};

class motor_api(3D) Float4 : public Output
{
protected:
    Float4();
    ~Float4() override;
};

class motor_api(3D) Int : public Output
{
protected:
    Int();
    ~Int() override;
};

class motor_api(3D) Int2 : public Output
{
protected:
    Int2();
    ~Int2() override;
};

class motor_api(3D) Int3 : public Output
{
protected:
    Int3();
    ~Int3() override;
};

class motor_api(3D) Int4 : public Output
{
protected:
    Int4();
    ~Int4() override;
};

class motor_api(3D) UInt : public Output
{
protected:
    UInt();
    ~UInt() override;
};

class motor_api(3D) UInt2 : public Output
{
protected:
    UInt2();
    ~UInt2() override;
};

class motor_api(3D) UInt3 : public Output
{
protected:
    UInt3();
    ~UInt3() override;
};

class motor_api(3D) UInt4 : public Output
{
protected:
    UInt4();
    ~UInt4() override;
};

class motor_api(3D) Bool : public Node
{
protected:
    Bool();
    ~Bool() override;
};

}}  // namespace Motor::Shaders
