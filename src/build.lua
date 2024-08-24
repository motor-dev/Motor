local context = ...

minitl = context:library('motor.minitl', {})
context:library('motor.core', { minitl })