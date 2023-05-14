#undef _GLIBCXX_ATOMIC_BUILTINS

static inline long __builtin_labs(long x)  // NOLINT
{
    return x < 0 ? -x : x;
}

static inline long long __builtin_llabs(long long x)  // NOLINT
{
    return x < 0 ? -x : x;
}
