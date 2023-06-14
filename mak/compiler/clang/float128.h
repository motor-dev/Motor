#ifndef MOTOR_CLANG_FLOAT128_H
#define MOTOR_CLANG_FLOAT128_H

#if __cplusplus
struct __float128
{
    __float128(int);
    bool  operator<(__float128) const;
    bool  operator>(__float128) const;
    bool  operator<=(__float128) const;
    bool  operator>=(__float128) const;
    bool  operator==(__float128) const;
    bool  operator!=(__float128) const;
    float operator+(__float128) const;
    float operator-(__float128) const;
    float operator*(__float128) const;
    float operator/(__float128) const;
    float operator-() const;
};
#endif

#endif
